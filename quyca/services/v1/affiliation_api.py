from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from infraestructure.mongo.utils.session import client
from core.config import settings


class AffiliationApiService:
    def __init__(self):
        self.colav_db = client[settings.MONGO_INITDB_DATABASE]
        self.impactu_db = client[settings.MONGO_IMPACTU_DB]

    def get_production(self,idx=None,max_results=100,page=1,start_year=None,end_year=None,sort=None,direction=None):
        total = 0
        papers=[]
        if start_year:
            try:
                start_year=int(start_year)
            except:
                print("Could not convert start year to int")
                return None
        if end_year:
            try:
                end_year=int(end_year)
            except:
                print("Could not convert end year to int")
                return None

        search_dict={}

        if idx:
            search_dict["authors.affiliations.id"]=ObjectId(idx)
                
        if start_year or end_year:
            search_dict["year_published"]={}
        if start_year:
            search_dict["year_published"]["$gte"]=start_year
        if end_year:
            search_dict["year_published"]["$lte"]=end_year
        
        cursor=self.colav_db["works"].find(search_dict)
        total=self.colav_db["works"].count_documents(search_dict)

        if not page:
            page=1
        else:
            try:
                page=int(page)
            except:
                print("Could not convert end page to int")
                return None
        if not max_results:
            max_results=100
        else:
            try:
                max_results=int(max_results)
            except:
                print("Could not convert end max to int")
                return None
        if max_results>250:
            max_results=250
        
        if sort=="citations" and direction=="ascending":
            cursor.sort([("citations_count.count",ASCENDING)])
        if sort=="citations" and direction=="descending":
            cursor.sort([("citations_count.count",DESCENDING)])
        if sort=="year" and direction=="ascending":
            cursor.sort([("year_published",ASCENDING)])
        if sort=="year" and direction=="descending":
            cursor.sort([("year_published",DESCENDING)])

        cursor=cursor.skip(max_results*(page-1)).limit(max_results)

        if cursor:
            for paper in cursor:
                entry=paper.copy()
                subjects=[]
                for subject in entry["subjects"]:
                    sub_entry=subject.copy()
                    if subject["source"]=="openalex":
                        sub_entry["subjects"]=[]
                        for sub in subject["subjects"]:
                            name = sub.get("name", "No name specified in DB")
                            lang = sub.get("lang", "No language specified in DB")
                            sub["names"]=[{"name":name,"lang":lang}]
                            sub_entry["subjects"].append(sub)
                    subjects.append(sub_entry)
                source=None
                if "id" in paper["source"].keys():
                    source=self.colav_db["sources"].find_one({"_id":paper["source"]["id"]})
                if source:
                    entry["source"]={
                        "id":source["_id"],
                        "names":source["names"],
                        "external_ids":source["external_ids"],
                        "ranking":source["ranking"],
                        "licenses":source["licenses"],
                        "apc":source["apc"],
                        "waiver":source["waiver"],
                        "addresses":source["addresses"],
                        "publisher":source["publisher"]
                    }
                else:
                    entry["source"]={}
                authors=[]
                for author in paper["authors"]:
                    au_entry=author.copy()
                    if not "affiliations" in au_entry.keys():
                        au_entry["affiliations"]=[]
                    author_db=None
                    if "id" in author.keys():
                        author_db=self.colav_db["person"].find_one({"_id":author["id"]})
                    if author_db:
                        au_entry={
                            "id":author_db["_id"],
                            "full_name":author_db["full_name"],
                            "first_names":author_db["first_names"],
                            "last_names":author_db["last_names"],
                            "external_ids":[ext for ext in author_db["external_ids"] if not ext["source"] in ["Cédula de Ciudadanía","Cédula de Extranjería","Passport"]],
                            "ranking":author_db["ranking"],
                            "sex":author_db["sex"]
                        }
                    affiliations=[]
                    aff_ids=[]
                    aff_types=[]
                    for aff in author["affiliations"]:
                        if "id" in aff.keys():
                            if aff["id"]:
                                aff_db=self.colav_db["affiliations"].find_one({"_id":aff["id"]})
                                if aff_db:
                                    aff_ids.append(aff["id"])
                                    aff_entry={
                                        "id":aff_db["_id"],
                                        "name":"",
                                        "external_ids":aff_db["external_ids"],
                                        "types":aff_db["types"],
                                        "addresses":aff_db["addresses"],
                                        "start_date":None,
                                        "end_date":None
                                    }
                                    if author_db:
                                        for aff_au in author_db["affiliations"]:
                                            if aff_au["id"]==aff["id"]:
                                                if "start_date" in aff_au.keys():
                                                    aff_entry["start_date"]=aff_au["start_date"]
                                                if "end_date" in aff_au.keys():
                                                    aff_entry["end_date"]=aff_au["end_date"]
                                                break
                                    name=aff_db["names"][0]["name"]
                                    lang=""
                                    for n in aff_db["names"]:
                                        if "lang" in n.keys():
                                            if n["lang"]=="es":
                                                name=n["name"]
                                                lang=n["lang"]
                                                break
                                            elif n["lang"]=="en":
                                                name=n["name"]
                                                lang=n["lang"]
                                    aff["name"]=name
                                    if "types" in aff.keys():
                                        for typ in aff["types"]:
                                            if "type" in typ.keys():
                                                if not typ["type"] in aff_types:
                                                    aff_types.append(typ["type"])
                                    affiliations.append(aff)
                    if author_db:
                        for aff in author_db["affiliations"]:
                            if aff["id"] in aff_ids:
                                continue
                            if aff["id"]:
                                aff_db=self.colav_db["affiliations"].find_one({"_id":aff["id"]})
                                inst_already=False
                                if aff_db:
                                    if "types" in aff_db.keys():
                                        for typ in aff_db["types"]:
                                            if "type" in typ.keys():
                                                if typ["type"] in aff_types:
                                                    inst_already=True
                                    if inst_already:
                                        continue
                                    aff_ids.append(aff["id"])
                                    aff_entry={
                                        "id":aff_db["_id"],
                                        "name":"",
                                        "external_ids":aff_db["external_ids"],
                                        "types":aff_db["types"],
                                        "addresses":aff_db["addresses"],
                                        "start_date":None,
                                        "end_date":None
                                    }
                                    if author_db:
                                        for aff_au in author_db["affiliations"]:
                                            if aff_au["id"]==aff["id"]:
                                                if "start_date" in aff_au.keys():
                                                    aff_entry["start_date"]=aff_au["start_date"]
                                                if "end_date" in aff_au.keys():
                                                    aff_entry["end_date"]=aff_au["end_date"]
                                                break
                                    name=aff_db["names"][0]["name"]
                                    lang=""
                                    for n in aff_db["names"]:
                                        if "lang" in n.keys():
                                            if n["lang"]=="es":
                                                name=n["name"]
                                                lang=n["lang"]
                                                break
                                            elif n["lang"]=="en":
                                                name=n["name"]
                                                lang=n["lang"]
                                    aff["name"]=name
                                    affiliations.append(aff)
                    au_entry["affiliations"]=affiliations
                    authors.append(au_entry)
                entry["authors"]=authors
                papers.append(entry)

            return {"data":papers,
                    "count":len(papers),
                    "page":page,
                    "total_results":total
                }
        else:
            return None

    def get_info(self):
        pass


affiliation_api_service = AffiliationApiService()


    
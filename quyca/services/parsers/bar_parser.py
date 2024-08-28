from datetime import datetime
from typing import Generator

from currency_converter import CurrencyConverter

from utils.cpi import inflate
from utils.hindex import hindex


def get_by_work_year_and_work_type(works: Generator) -> list:
    result = {}
    for work in works:
        if not work.year_published:
            continue
        work_year = work.year_published
        if work_year not in result.keys():
            result[work_year] = {}
        for work_type in work.types:
            if (
                work_type.source == "scienti"
                and work_type.type == "Publicado en revista especializada"
            ):
                if work_type.type not in result[work_year].keys():
                    result[work_year][work_type.type] = 1
                else:
                    result[work_year][work_type.type] += 1
    plot = []
    for year in result.keys():
        for work_type in result[year].keys():
            plot += (
                [{"x": year, "y": result[year][work_type], "type": work_type}]
                if year
                else []
            )
    plot = sorted(plot, key=lambda x: x.get("x", -99))
    return plot


def get_by_affiliation_type(data) -> list:
    if not isinstance(data, dict):
        print(type(data))
        return None
    if len(data) == 0:
        print(len(data))
        return None
    result = {}
    for name, works in data.items():
        for work in works:
            if name not in result.keys():
                result[name] = {}

            for work_type in work["types"]:
                if (
                    work_type["source"] == "scienti"
                    and work_type["type"] == "Publicado en revista especializada"
                ):
                    # if typ["level"] == 2:
                    if work_type["type"] not in result[name].keys():
                        result[name][work_type["type"]] = 1
                    else:
                        result[name][work_type["type"]] += 1
    plot = []
    for name in result.keys():
        for work_type in result[name].keys():
            plot.append({"x": name, "y": result[name][work_type], "type": work_type})
    plot = sorted(plot, key=lambda x: x["y"], reverse=True)
    return plot


def get_citations_by_year(works: Generator) -> list:
    result = {}
    no_info = 0
    for work in works:
        if not work.citations_by_year:
            no_info += 1
            continue
        for yearly in work.citations_by_year:
            if yearly.year in result.keys():
                result[yearly.year] += yearly.cited_by_count
            else:
                result[yearly.year] = yearly.cited_by_count
    plot = sorted(result.items(), key=lambda x: x[0])
    plot = [{"x": x[0], "y": x[1]} for x in plot]
    plot += [{"x": "Sin información", "y": no_info}]
    return plot


def apc_by_year(sources: Generator, base_year) -> list:
    data = map(lambda x: x.apc, sources)
    currency = CurrencyConverter()
    result = {}
    for apc in data:
        try:
            if apc.currency == "USD":
                raw_value = apc.charges
                value = inflate(
                    raw_value,
                    apc.year_published,
                    to=max(base_year, int(apc.year_published)),
                )
            else:
                raw_value = currency.convert(apc.charges, apc.currency, "USD")
                value = inflate(
                    raw_value,
                    apc.year_published,
                    to=max(base_year, int(apc.year_published)),
                )
        except ValueError as e:
            value = 0
        if value:
            if apc.year_published not in result.keys():
                result[apc.year_published] = value
            else:
                result[apc.year_published] += value
    sorted_result = sorted(result.items(), key=lambda x: x[0])
    plot = [{"x": x[0], "y": int(x[1])} for x in sorted_result]
    return plot


def oa_by_year(works: Generator) -> list:
    result = {}
    for work in works:
        year = work.year_published
        if year in result.keys():
            if work.bibliographic_info.is_open_access:
                result[year]["open"] += 1
            else:
                result[year]["closed"] += 1
        else:
            if work.bibliographic_info.is_open_access:
                result[year] = {"open": 1, "closed": 0}
            else:
                result[year] = {"open": 0, "closed": 1}
    result_list = []
    for year in result.keys():
        for typ in result[year].keys():
            result_list.append({"x": year, "y": result[year][typ], "type": typ})
    return sorted(result_list, key=lambda x: x["x"])


def works_by_publisher_year(data: Generator) -> list:
    result = {}
    top5 = {}
    for source in data:
        year = int(source.apc.year_published or 0)
        if year in result.keys():
            if source.publisher.name not in result[year].keys():
                result[year][source.publisher.name] = 1
            else:
                result[year][source.publisher.name] += 1
        else:
            result[year] = {source.publisher.name: 1}
        if source.publisher.name not in top5.keys():
            top5[source.publisher.name] = 1
        else:
            top5[source.publisher.name] += 1
    top5 = [top[0] for top in sorted(top5.items(), key=lambda x: x[1], reverse=True)][
        :5
    ]
    plot = []
    for year in result.keys():
        for publisher in top5:
            if publisher in result[year].keys():
                plot.append(
                    {"x": year, "y": result[year][publisher], "type": publisher}
                )
            else:
                plot.append({"x": year, "y": 0, "type": publisher})
    plot = sorted(plot, key=lambda x: x["x"])
    return plot


def h_index_by_year(works: Generator) -> list:
    h_by_year = {}
    total_work_citations_by_year = []
    for work in works:
        acc_citations_by_year = []
        sorted_citations = sorted(work.citations_by_year, key=lambda x: x.year)
        for citation in sorted_citations:
            if len(acc_citations_by_year) == 0:
                acc_citations_by_year.append(
                    {
                        "year": citation.year,
                        "citations": citation.cited_by_count,
                    }
                )
            else:
                acc_citations_by_year.append(
                    {
                        "year": citation.year,
                        "citations": citation.cited_by_count
                        + acc_citations_by_year[-1]["citations"],
                    }
                )
        total_work_citations_by_year.append(acc_citations_by_year)
    for work in total_work_citations_by_year:
        for citations in work:
            year = citations["year"]
            citations = citations["citations"]

            if not year in h_by_year.keys():
                h_by_year[year] = [citations]
            else:
                h_by_year[year].append(citations)
    index_by_year = []
    years = set([x[0] for x in h_by_year.items()])
    for year in years:
        index_by_year.append({"x": year, "y": hindex(h_by_year[year])})
    sorted_index_by_year = sorted(index_by_year, key=lambda x: x["x"])
    return sorted_index_by_year


def works_by_researcher_category_and_year(data) -> list:
    result = {}
    for work in data:
        if "year_published" in work.keys():
            year = work["year_published"]

            if year not in result.keys():
                result[year] = {}

            if work["rank"] not in result[year].keys():
                result[year][work["rank"]] = 1
            else:
                result[year][work["rank"]] += 1
    plot = []
    for year in result.keys():
        for rank in result[year].keys():
            plot.append({"x": year, "y": result[year][rank], "type": rank})
    plot = sorted(plot, key=lambda x: x["x"] if x["x"] else -1)
    return plot


def products_by_year_by_group_category(works: list) -> list:
    result = {}
    for work in works:
        if work.year_published and work.date_published:
            year = work.year_published
            year_timestamp = datetime.strptime(str(year), "%Y").timestamp()
            rank_name = ""
            for rank in work.ranking_:
                if rank.source == "scienti" and rank.from_date and rank.to_date:
                    if (
                        rank.from_date < year_timestamp
                        and rank.to_date > year_timestamp
                    ):
                        rank_name = rank.rank
                        break
            if rank_name != "":
                if year not in result.keys():
                    result[year] = {}
                if rank_name not in result[year].keys():
                    result[year][rank_name] = 1
                else:
                    result[year][rank_name] += 1
    plot = []
    for year in result.keys():
        for group_category in result[year].keys():
            plot.append(
                {
                    "x": year,
                    "y": result[year][group_category],
                    "type": group_category,
                }
            )
    plot = sorted(plot, key=lambda x: x["x"])
    return plot

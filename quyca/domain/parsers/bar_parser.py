from collections import defaultdict
from typing import Generator

from pymongo.command_cursor import CommandCursor


def parse_annual_evolution_by_scienti_classification(works: Generator) -> dict:
    data: defaultdict = defaultdict(lambda: defaultdict(int))
    for work in works:
        if not work.year_published:
            continue
        for work_type in work.types:
            if work_type.source == "scienti" and work_type.level == 2:
                data[work.year_published][work_type.type] += 1
    plot = [
        {"x": year, "y": count, "type": work_type}
        for year, work_types in data.items()
        for work_type, count in work_types.items()
    ]
    return {"plot": sorted(plot, key=lambda x: x.get("x"))}


def parse_affiliations_by_product_type(data: CommandCursor) -> dict:
    plot = [{"x": item["name"], "y": item["works_count"], "type": item["type"]} for item in data]
    return {"plot": sorted(plot, key=lambda x: x.get("y"), reverse=True)}


def parse_annual_citation_count(works: Generator) -> dict:
    data: dict = {}
    no_info = 0
    for work in works:
        if not work.citations_by_year:
            no_info += 1
            continue
        for citation in work.citations_by_year:
            if citation.year in data.keys():
                data[citation.year] += citation.cited_by_count
            else:
                data[citation.year] = citation.cited_by_count
    plot = [{"x": year, "y": count} for year, count in sorted(data.items())]
    plot += [{"x": "Sin información", "y": no_info}]
    return {"plot": plot}


def parse_annual_articles_open_access(works: Generator) -> dict:
    data: defaultdict = defaultdict(lambda: {"Abierto": 0, "Cerrado": 0, "Sin información": 0})
    for work in works:
        access_type = "Abierto" if work.open_access.is_open_access else "Cerrado"
        if work.open_access.is_open_access is None and not work.year_published:
            data["Sin año"]["Sin información"] += 1
            continue
        if work.open_access.is_open_access is None:
            data[work.year_published]["Sin información"] += 1
            continue
        if work.year_published is None:
            data["Sin año"][access_type] += 1
            continue
        data[work.year_published][access_type] += 1
    plot = [
        {"x": year, "y": count, "type": access_type}
        for year, counts in data.items()
        for access_type, count in counts.items()
    ]
    return {"plot": sorted(plot, key=lambda x: float("inf") if x.get("x") == "Sin año" else x.get("x"))}


def parse_annual_articles_by_top_publishers(works: Generator) -> dict:
    data: defaultdict = defaultdict(lambda: defaultdict(int))
    for work in works:
        if not work.source.publisher and not work.year_published:
            data["Sin año"]["Sin información"] += 1
            continue
        if not work.source.publisher:
            data[work.year_published]["Sin información"] += 1
            continue
        if not work.year_published:
            data["Sin año"][work.source.publisher.name] += 1
            continue
        data[work.year_published][work.source.publisher.name] += 1
    plot = [
        {"x": year, "y": count, "type": publisher}
        for year, publishers in data.items()
        for publisher, count in publishers.items()
    ]
    return {"plot": sorted(plot, key=lambda x: float("inf") if x.get("x") == "Sin año" else x.get("x"))}


def parse_annual_apc_expenses(works: Generator) -> dict:
    data: defaultdict = defaultdict(int)
    total_apc = 0
    total_results = 0
    for work in works:
        total_results += 1
        if not work.apc.paid.value_usd:
            continue
        data[work.year_published] += work.apc.paid.value_usd
        total_apc += work.apc.paid.value_usd
    plot = [{"x": year, "y": value} for year, value in data.items()]
    return {"plot": sorted(plot, key=lambda x: x.get("x")), "total_apc": total_apc, "total_results": total_results}
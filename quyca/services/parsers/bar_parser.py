from collections import defaultdict
from typing import Generator

from currency_converter import CurrencyConverter

from utils.cpi import inflate


def parse_annual_evolution_by_scienti_classification(works: Generator) -> list:
    result: defaultdict = defaultdict(lambda: defaultdict(int))
    for work in works:
        if not work.year_published:
            continue
        for work_type in work.types:
            if work_type.source == "scienti" and work_type.level == 2:
                result[work.year_published][work_type.type] += 1
    plot = [
        {"x": year, "y": count, "type": work_type}
        for year, work_types in result.items()
        for work_type, count in work_types.items()
    ]
    return sorted(plot, key=lambda x: x.get("x"))


def get_by_affiliation_type(data: dict) -> list | None:
    if not isinstance(data, dict):
        print(type(data))
        return None
    if len(data) == 0:
        print(len(data))
        return None
    result: dict = {}
    for name, works in data.items():
        for work in works:
            if name not in result.keys():
                result[name] = {}

            for work_type in work["types"]:
                if work_type["source"] == "scienti" and work_type["type"] == "Publicado en revista especializada":
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
    result: dict = {}
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
    plot_data = sorted(result.items(), key=lambda x: x[0])
    plot = [{"x": x[0], "y": x[1]} for x in plot_data]
    plot += [{"x": "Sin información", "y": no_info}]
    return plot


def apc_by_year(sources: Generator, base_year: int) -> list:
    data = map(lambda x: x.apc, sources)
    currency = CurrencyConverter()
    result: dict = {}
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
        except ValueError:
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
    result: dict = {}
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
    result: dict = {}
    top5: dict = {}
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
    top = [top[0] for top in sorted(top5.items(), key=lambda x: x[1], reverse=True)][:5]
    plot = []
    for year in result.keys():
        for publisher in top:
            if publisher in result[year].keys():
                plot.append({"x": year, "y": result[year][publisher], "type": publisher})
            else:
                plot.append({"x": year, "y": 0, "type": publisher})
    plot = sorted(plot, key=lambda x: x["x"])
    return plot

from functools import wraps
from datetime import datetime
from itertools import chain
from typing import Callable, Iterable, Generator
from collections import Counter, defaultdict
from pymongo.command_cursor import CommandCursor

from domain.constants.open_access_status import open_access_status_dict
from domain.models.affiliation_model import Affiliation
from domain.helpers import get_works_h_index_by_scholar_citations


def get_percentage(func: Callable[..., list]) -> Callable[..., dict]:
    @wraps(func)
    def wrapper(*args: Iterable, **kwargs: dict) -> dict:
        data = func(*args, **kwargs)
        total = sum(item["value"] for item in data)
        for item in data:
            item["percentage"] = round(item["value"] / total * 100, 2) if total else 0
        return {"plot": data, "sum": total}

    return wrapper


@get_percentage
def parse_citations_by_affiliations(data: CommandCursor) -> list:
    plot: list = []
    for item in data:
        citations_count = item.get("citations_count", {})
        openalex_citations_count: dict = next(filter(lambda x: x["source"] == "openalex", citations_count), {})
        plot.append({"name": item.get("name", "No name"), "value": openalex_citations_count.get("count", 0)})
    return plot


@get_percentage
def parse_apc_expenses_by_affiliations(data: CommandCursor) -> list:
    result: defaultdict = defaultdict(int)
    for item in data:
        value = item.get("work").get("apc").get("paid").get("value_usd", 0)
        result[item.get("names", [{"name": "No name"}])[0].get("name")] += value
    plot = []
    for name, value in result.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def parse_h_index_by_affiliation(data: CommandCursor) -> list:
    plot = []
    for item in data:
        plot.append({"name": item.get("name"), "value": get_works_h_index_by_scholar_citations(item.get("works"))})
    return plot


@get_percentage
def parse_articles_by_publisher(works: Generator) -> list:
    data = map(
        lambda x: (
            x.source.publisher.name
            if x.source.publisher and isinstance(x.source.publisher.name, str)
            else "Sin información"
        ),
        works,
    )
    counter = Counter(data)
    plot = []
    for name, value in counter.items():
        plot += [{"name": name, "value": value}]
    return plot


@get_percentage
def parse_products_by_subject(works: Generator) -> list:
    data = chain.from_iterable(
        map(
            lambda x: [sub for subject in x.subjects for sub in subject.subjects if subject.source == "openalex"],
            works,
        )
    )
    results = Counter(subject.name for subject in data)
    plot = []
    for name, value in results.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def parse_products_by_access_route(works: Generator) -> list:
    data = map(
        lambda x: (x.open_access.open_access_status if x.open_access.open_access_status else "no_info"),
        works,
    )
    counter = Counter(data)
    plot = []
    for name, value in counter.items():
        plot.append({"name": open_access_status_dict.get(name), "value": value})
    return plot


@get_percentage
def parse_products_by_author_sex(data: CommandCursor) -> list:
    plot = []
    for item in data:
        if item.get("_id", "") == "":
            plot.append({"name": "Sin información", "value": item.get("works_count", 0)})
            continue
        plot.append({"name": item.get("_id"), "value": item.get("works_count", 0)})
    return plot


@get_percentage
def parse_products_by_age_range(persons: CommandCursor) -> list:
    ranges = {"14-26": (14, 26), "27-59": (27, 59), "60+": (60, float("inf"))}
    result = {"14-26": 0, "27-59": 0, "60+": 0, "Sin información": 0}
    for person in persons:
        if not person.get("birthdate") or person.get("birthdate") == -1:
            result["Sin información"] += person.get("works_count", 0)
            continue
        birthdate = datetime.fromtimestamp(person.get("birthdate")).year
        age = datetime.now().year - birthdate
        for name, (low_age, high_age) in ranges.items():
            if low_age <= age <= high_age:
                result[name] += person.get("works_count", 0)
                break
    plot = []
    for name, value in result.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def parse_articles_by_scienti_category(works: list) -> list:
    total_works = len(works)
    data = filter(
        lambda x: x.source == "scienti" and x.rank and x.rank.split("_")[-1] in ["A", "A1", "B", "C", "D"],
        chain.from_iterable(map(lambda x: x.ranking, works)),
    )
    counter = Counter(map(lambda x: x.rank.split("_")[-1], data))
    plot = []
    for name, value in counter.items():
        plot.append({"name": name, "value": value})
    plot.append({"name": "Sin información", "value": total_works - sum(counter.values())})
    return plot


@get_percentage
def parse_articles_by_scimago_quartile(works: Generator) -> list:
    data = []
    total_articles = 0
    for work in works:
        total_articles += 1
        for ranking in work.source.ranking:
            condition = (
                ranking.source in ["Scimago Best Quartile", "scimago Best Quartile"]
                and ranking.rank != "-"
                and work.date_published
                and ranking.from_date <= work.date_published <= ranking.to_date
            )
            if condition:
                data.append(ranking.rank)
                break
    counter = Counter(data)
    plot = [{"name": "Sin información", "value": total_articles - len(data)}]
    for name, value in counter.items():
        plot.append({"name": name, "value": value})
    return plot


@get_percentage
def parse_articles_by_publishing_institution(works: Generator, institution: Affiliation) -> list:
    result = {"Misma": 0, "Diferente": 0, "Sin información": 0}
    names = []
    if institution:
        names = list(set([name.name.lower() for name in institution.names]))
    for work in works:
        if (
            not work.source.publisher
            or not work.source.publisher.name
            or not isinstance(work.source.publisher.name, str)
        ):
            result["Sin información"] += 1
            continue
        if work.source.publisher.name.lower() in names:
            result["Misma"] += 1
        else:
            result["Diferente"] += 1
    plot = []
    for name, value in result.items():
        plot.append({"name": name, "value": value})
    return plot
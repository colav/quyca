from domain.models.base_model import QueryParams
from infrastructure.repositories import news_repository
from domain.parsers import news_parser


def get_news_by_person(person_id: str, query_params: QueryParams) -> dict:
    """
    Retrieves and parses news related to a specific person.

    This function fetches news documents associated with a given person ID,
    parses the results, and returns the data along with the total count.

    Parameters:
    -----------
    person_id : str
        The ID of the person for whom the news is being retrieved.
    query_params : QueryParams
        Query parameters for filtering or paginating the results.

    Returns:
    --------
    dict
        A dictionary containing:
        - data: the parsed list of news entries.
        - total_results: the total number of related news items.
    """
    news = news_repository.get_news_by_person(person_id, query_params)
    data = news_parser.parse_news(news)
    total_results = news_repository.news_count_by_person(person_id)
    return {"data": data, "total_results": total_results}

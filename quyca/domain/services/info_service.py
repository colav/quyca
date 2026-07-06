from quyca.infrastructure.repositories import (
    info_repository,
)


def get_info() -> dict:
    return {
        "db_update": info_repository.get_last_db_update(),
        "total_products": info_repository.get_entity_count("works"),
        "total_institutions": info_repository.get_entity_count("affiliations", "institution"),
        "total_faculties": info_repository.get_entity_count("affiliations", "faculty"),
        "total_departments": info_repository.get_entity_count("affiliations", "department"),
        "total_groups": info_repository.get_entity_count("affiliations", "group"),
        "total_patents": info_repository.get_entity_count("patents"),
        "total_projects": info_repository.get_entity_count("projects"),
        "total_authors": info_repository.get_entity_count("person"),
        "total_news": info_repository.get_news_count(),
        "total_open_access": info_repository.get_open_access_count(),
        "total_sources": info_repository.get_entity_count("sources"),
    }


def get_works_quality_metrics() -> dict:
    return {
        "works_collection": info_repository.get_works_quality_metrics(),
        "person_collection": info_repository.get_person_quality_metrics(),
        "affiliations_collection": info_repository.get_affiliations_quality_metrics(),
        "sources_collection": info_repository.get_sources_quality_metrics(),
    }

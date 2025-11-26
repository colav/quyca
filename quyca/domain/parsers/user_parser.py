from domain.models.user_model import User

""" This function extracts the rolID attribute from a User object and returns it inside a dictionary. """


def user_ror_id_and_institution(user: User) -> dict:
    info_user = {"_id": user.id, "institution": user.institution, "rol": user.rol}
    return info_user

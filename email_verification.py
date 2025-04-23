import re

def is_valid_email(email):
    # Expression régulière pour vérifier le format de l'e-mail
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    return re.match(email_regex, email) is not None

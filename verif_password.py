import bcrypt


#inverser le hachage
def reverse(password, password_bd):
    bytes_pass = password_bd.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), bytes_pass)


def password_is_personal_info(nom, prenom, password):
    """
    Vérifie si le mot de passe contient des informations personnelles (nom/prénom).
    Rend la vérification insensible à la casse.
    """
    password_lower = password.lower()
    if nom and nom.lower() in password_lower:
        return True
    if prenom and prenom.lower() in password_lower:
        return True
    return False


# Fonction utilitaire (à implémenter si ce n'est pas déjà fait)
def hash_password(password):
    """
    Hache le mot de passe en utilisant bcrypt.
    """
    # Génère un sel et hache le mot de passe
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # Retourne la chaîne de caractères UTF-8


def get_valid_password(nom, prenom, password, confirm_password):

    if password != confirm_password:
        return False, "Les mots de passe ne correspondent pas. Veuillez réessayer."

    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères."

    if password_is_personal_info(nom, prenom, password):
        return False, "Le mot de passe ne doit pas contenir votre nom ou prénom. Veuillez réessayer."

    # Si toutes les validations passent, hachez le mot de passe et retournez-le
    hashed_password = hash_password(password)
    return True, hashed_password

import bcrypt

def password_is_personal_info(nom, prenom, password):
    return nom.lower() in password.lower() or prenom.lower() in password.lower()


# Fonction pour hacher le mot de passe avec bcrypt
def hash_password(password):
    # Générer un "salt" aléatoire
    salt = bcrypt.gensalt()
    # Hacher le mot de passe avec le salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


# Fonction pour demander un mot de passe valide (modifiée pour utiliser le hachage)
def get_valid_password(nom, prenom, password,  confirm_password):
        if password != confirm_password:
            return "Les mots de passe ne correspondent pas. Veuillez réessayer."
        elif len(password) < 8:
            return "Le mot de passe doit contenir au moins 8 caractères."
        elif password_is_personal_info(nom, prenom, password):
            return "Le mot de passe ne doit pas contenir votre nom ou prénom. Veuillez réessayer."
        else:
            return hash_password(password)  # Hacher le mot de passe avant de le retourner
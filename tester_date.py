from datetime import date, timedelta, datetime


def ajuster_si_weekend(date):
    """Décale la date au lundi si elle tombe  un dimanche."""
    if date.weekday() == 6:  # dimanche
        return date + timedelta(days=1)
    return date

def jours_feries(annee):
    """Retourne tous les jours fériés en France (hors Alsace-Moselle) pour une année donnée."""

    # Jours fériés fixes
    feries = {
        "Jour de l'an": date(annee, 1, 1),
        "Résurection 1947": date(annee, 3, 29),
        "Fête du travail": date(annee, 5, 1),
        "Fête nationale": date(annee, 6, 26),
        "Assomption": date(annee, 8, 15),
        "Toussaint": date(annee, 11, 1),
        "Noël": date(annee, 12, 25),
        "Saint Sylvestre": date(annee, 12, 31)
    }

    # Date de Pâques (algorithme de Butcher-Meeus)
    def paques(annee):
        a = annee % 19
        b = annee // 100
        c = annee % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        mois = (h + l - 7 * m + 114) // 31
        jour = ((h + l - 7 * m + 114) % 31) + 1
        return date(annee, mois, jour)

    paques_date = paques(annee)

    # Jours fériés variables
    feries.update({
        "Pâques": paques_date,
        "Lundi de Pâques": paques_date + timedelta(days=1),
        "Ascension": paques_date + timedelta(days=39),
        "Lundi de Pentecôte": paques_date + timedelta(days=50),
    })

    return feries

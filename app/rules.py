
# Priorität anhand der Dringlichkeit bestimmen
def assign_priority(urgency: str) -> str:
    priority_mapping = {
        "Hoch": "P1",
        "Mittel": "P2",
        "Niedrig": "P3"
    }

    if urgency not in priority_mapping:
        raise ValueError(f"Ungültige Dringlichkeit: {urgency}")

    return priority_mapping[urgency]


# Zuständige Abteilung anhand der Kategorie bestimmen
def assign_department(category: str) -> str:
    department_mapping = {
        "Versand": "Logistik",
        "Rechnung": "Buchhaltung",
        "Technischer Support": "IT-Support",
        "Sonstiges": "Kundenservice"
    }

    if category not in department_mapping:
        raise ValueError(f"Ungültige Kategorie: {category}")

    return department_mapping[category]


import sys
from pathlib import Path

import pytest

# Projektordner zum Python-Suchpfad hinzufügen
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rules import assign_priority, assign_department


# Tests für die Priorität
def test_high_priority():
    assert assign_priority("Hoch") == "P1"


def test_medium_priority():
    assert assign_priority("Mittel") == "P2"


def test_low_priority():
    assert assign_priority("Niedrig") == "P3"


def test_invalid_urgency():
    with pytest.raises(ValueError):
        assign_priority("Unbekannt")


# Tests für die zuständige Abteilung
def test_shipping_department():
    assert assign_department("Versand") == "Logistik"


def test_billing_department():
    assert assign_department("Rechnung") == "Buchhaltung"


def test_technical_support_department():
    assert assign_department("Technischer Support") == "IT-Support"


def test_other_department():
    assert assign_department("Sonstiges") == "Kundenservice"


def test_invalid_category():
    with pytest.raises(ValueError):
        assign_department("Unbekannt")

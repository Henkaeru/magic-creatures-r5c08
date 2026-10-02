"""Analyses du cours, une classe par méthode.

Le module expose les classes que main.py enchaîne. Le correctif de scikit-learn
utilisé par l'AFC est chargé avec ce paquet. Ce fichier ne lance pas les calculs.
"""

import matplotlib

matplotlib.use("Agg")

from analyse.acm import AnalyseACM
from analyse.acp import AnalyseACP
from analyse.afc import AnalyseAFC
from analyse.clustering import Partitionnement
from analyse.journal import Journal
from analyse.population import PopulationCreatures
from analyse.supervise import ApprentissageSupervise

__all__ = [
    "AnalyseACM",
    "AnalyseACP",
    "AnalyseAFC",
    "ApprentissageSupervise",
    "Journal",
    "Partitionnement",
    "PopulationCreatures",
]

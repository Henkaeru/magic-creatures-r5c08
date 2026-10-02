"""Population des créatures et matrice standardisée pour l'ACP.

Le module lit `data/cards.csv` et sépare les créatures du reste des cartes.
Il ne réalise pas l'ACP : il prépare la table des cas complets et la matrice
centrée-réduite utilisée par les autres classes.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CARDS = DATA / "cards.csv"

RANDOM_STATE = 0
COULEURS = {
    "W": "Blanc",
    "U": "Bleu",
    "B": "Noir",
    "R": "Rouge",
    "G": "Vert",
}
ORDRE_COULEURS = ["Blanc", "Bleu", "Noir", "Rouge", "Vert", "Incolore"]


def morceaux(valeur):
    if pd.isna(valeur) or str(valeur).strip() == "":
        return []
    return [morceau.strip() for morceau in str(valeur).split(",") if morceau.strip()]


def est_creature(types):
    return "Creature" in morceaux(types)


def couleurs_de(valeur):
    couleurs = [COULEURS[code] for code in morceaux(valeur) if code in COULEURS]
    return couleurs or ["Incolore"]


def groupe_couleur(valeur):
    couleurs = [code for code in morceaux(valeur) if code in COULEURS]
    if not couleurs:
        return "Incolore"
    if len(couleurs) == 1:
        return "Monocolore"
    return "Multicolore"


class PopulationCreatures:
    """Lit `cards.csv` et prépare les données des créatures utilisées par chaque méthode."""

    def __init__(self, journal, chemin=None):
        self.journal = journal
        self.chemin = Path(chemin) if chemin is not None else CARDS
        self.cartes = None
        self.creatures = None
        self.df = None
        self.quantitatif = None
        self.x_scaled = None
        self.coordonnees = None
        self.variance = None
        self.types_gardes = None

    def charger(self):
        """Lit `cards.csv`, conserve les créatures et standardise six variables.

        Les forces ou endurances indiquées par `*` sont écartées et ne sont pas
        remplacées par une médiane. Les créatures sans prix numérique sont également
        exclues.
        """
        cartes = pd.read_csv(self.chemin, low_memory=False)
        creatures = cartes.loc[cartes["types"].map(est_creature)].copy()

        # L'ACP a besoin de nombres. On ne remplace pas une force en étoile par une médiane.
        for colonne in [
            "power",
            "toughness",
            "mana_value",
            "retail_price",
            "rarity_rank",
            "printing_count",
        ]:
            creatures[colonne + "_num"] = pd.to_numeric(
                creatures[colonne], errors="coerce"
            )

        complet = (
            creatures[
                [
                    "power_num",
                    "toughness_num",
                    "mana_value_num",
                    "retail_price_num",
                    "rarity_rank_num",
                    "printing_count_num",
                ]
            ]
            .notna()
            .all(axis=1)
        )
        df = creatures.loc[complet].copy()
        df["groupe_couleur"] = df["color_identity"].map(groupe_couleur)
        df["type_principal"] = df["subtypes"].map(
            lambda valeur: (morceaux(valeur) or ["Sans type"])[0]
        )

        afficher = self.journal.afficher
        self.journal.titre("POPULATION", saut=False)
        afficher(f"Lignes de cards.csv: {len(cartes)}")
        afficher(f"Creatures (type Creature): {len(creatures)}")
        afficher(
            "Creatures avec mana, force, endurance, rarete et prix numeriques: "
            f"{len(df)}"
        )
        afficher(f"Ecartees pour l'ACP: {len(creatures) - len(df)}")
        afficher("Groupes de couleur (population ACP):")
        afficher(df["groupe_couleur"].value_counts().to_string())

        quantitatif = pd.DataFrame(
            {
                "mana": df["mana_value_num"],
                "force": df["power_num"],
                "endurance": df["toughness_num"],
                "rarete": df["rarity_rank_num"],
                "impressions (log)": np.log1p(df["printing_count_num"].clip(lower=0)),
                "prix (log)": np.log1p(df["retail_price_num"].clip(lower=0)),
            }
        )
        x_scaled = StandardScaler().fit_transform(quantitatif)

        self.journal.tableau(
            "Controle de la standardisation (moyenne, ecart-type):",
            pd.DataFrame(x_scaled, columns=quantitatif.columns)
            .agg(["mean", "std"])
            .round(3)
            .to_string(),
        )
        self.journal.tableau("Correlations:", quantitatif.corr().round(2).to_string())

        self.cartes = cartes
        self.creatures = creatures
        self.df = df
        self.quantitatif = quantitatif
        self.x_scaled = x_scaled
        return self

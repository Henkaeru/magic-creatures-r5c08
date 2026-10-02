"""AFC du type de créature selon l'identité de couleur.

L'analyse porte sur l'ensemble des créatures, et pas uniquement sur les cas
complets.

Le tableau de contingence compte les couples type-couleur. La classe écrit
ce tableau et génère les figures `afc_*.png`.
"""

import matplotlib

matplotlib.use("Agg")

import sklearn.utils.validation as skval

# factor_analyzer appelle encore check_array(force_all_finite=...),
# un argument renommé ensure_all_finite dans les versions récentes de scikit-learn.
_check_array = skval.check_array


def _check_array_compat(*args, **kwargs):
    if "force_all_finite" in kwargs:
        kwargs["ensure_all_finite"] = kwargs.pop("force_all_finite")
    return _check_array(*args, **kwargs)


skval.check_array = _check_array_compat

import factor_analyzer.factor_analyzer as fa_mod

fa_mod.check_array = _check_array_compat

import numpy as np
import pandas as pd
import seaborn as sns
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
from scipy.stats import chi2_contingency
from sklearn.decomposition import FactorAnalysis

from analyse.graphiques import Graphiques
from analyse.population import ORDRE_COULEURS, RANDOM_STATE, couleurs_de, morceaux

# En dessous de ce nombre de cartes, un type de créature est trop rare
# pour donner une case stable dans le tableau de contingence.
SEUIL_TYPE = 400


class AnalyseAFC:
    """Une créature ayant plusieurs types et plusieurs couleurs est comptée une fois
    pour chaque couple type-couleur, et non une seule fois pour la carte.
    """

    def __init__(self, population, journal):
        self.population = population
        self.journal = journal
        self.graphiques = Graphiques(journal)

    def executer(self):
        """Réalise l'AFC du type selon la couleur.

        Le tableau n'est pas construit avec une ligne par carte : chaque couple
        sous-type-couleur compte pour 1. La méthode écrit les résultats de Bartlett
        et du khi-deux, puis conserve la liste des types fréquents pour l'ACM.
        """
        afficher = self.journal.afficher
        g = self.graphiques
        creatures = self.population.creatures

        paires = []
        for subtypes, identite in zip(
            creatures["subtypes"], creatures["color_identity"]
        ):
            for type_creature in morceaux(subtypes):
                for couleur in couleurs_de(identite):
                    paires.append((type_creature, couleur))

        paires = pd.DataFrame(paires, columns=["type", "couleur"])
        effectifs_types = paires["type"].value_counts()
        types_gardes = effectifs_types[effectifs_types >= SEUIL_TYPE].index
        paires_afc = paires.loc[paires["type"].isin(types_gardes)]
        contingence = pd.crosstab(paires_afc["type"], paires_afc["couleur"])
        contingence = contingence.reindex(
            columns=[c for c in ORDRE_COULEURS if c in contingence.columns]
        )
        contingence = contingence.loc[
            contingence.sum(axis=1).sort_values(ascending=False).index
        ]

        standardisee = contingence.sub(contingence.mean()).div(contingence.std())
        chi2_bartlett, p_bartlett = calculate_bartlett_sphericity(standardisee)
        chi2_test, p_chi2, ddl, _ = chi2_contingency(contingence)

        concernees = (
            creatures["subtypes"]
            .map(
                lambda valeur: any(
                    type_creature in types_gardes for type_creature in morceaux(valeur)
                )
            )
            .sum()
        )

        self.journal.titre("AFC - TYPE DE CREATURE x COULEUR")
        afficher(
            f"Couples (type, couleur) avant filtre: {len(paires)}. "
            f"Types gardes (>= {SEUIL_TYPE} occurrences): {len(types_gardes)}."
        )
        afficher("Types: " + ", ".join(contingence.index))
        afficher(contingence.to_string())
        afficher(f"Total du tableau: {int(contingence.to_numpy().sum())}")
        afficher(f"Creatures distinctes concernees par ces types: {concernees}")
        afficher(f"Bartlett: chi2 = {chi2_bartlett:.2f}, p-value = {p_bartlett:.3e}")
        afficher(
            f"Chi2 d'independance: chi2 = {chi2_test:.2f}, ddl = {ddl}, p-value = {p_chi2:.3e}"
        )

        n_facteurs_max = min(contingence.shape) - 1
        analyse_facteurs = FactorAnalyzer(n_factors=n_facteurs_max, rotation=None)
        analyse_facteurs.fit(standardisee)
        valeurs_facteurs, _ = analyse_facteurs.get_eigenvalues()
        n_facteurs_kaiser = int((valeurs_facteurs >= 1).sum())
        afficher(f"Valeurs propres des facteurs: {np.round(valeurs_facteurs, 3)}")
        afficher(f"Facteurs avec valeur propre >= 1: {n_facteurs_kaiser}")

        with g.figure(
            "afc_contingence.png",
            (11, 8),
            "Contingence : type de creature x couleur",
            xlabel="Couleur de l'identite",
            ylabel="Type de creature",
        ):
            sns.heatmap(contingence, annot=True, fmt="d", cmap="Blues")

        g.eboulis(
            "afc_scree.png",
            valeurs_facteurs,
            "Facteur",
            "AFC - éboulis des valeurs propres",
            figsize=(7, 4.5),
        )

        rotations = [
            ("Sans rotation", None),
            ("Varimax", "varimax"),
            ("Quartimax", "quartimax"),
        ]
        with g.sous_figures(
            "afc_rotations.png",
            "AFC - trois rotations",
            ncols=3,
            figsize=(16, 6),
            sharex=True,
            sharey=True,
        ) as (_fig, axes):
            for ax, (titre, rotation) in zip(axes, rotations):
                modele = FactorAnalysis(
                    n_components=2, rotation=rotation, random_state=RANDOM_STATE
                )
                modele.fit(standardisee)
                colonnes = modele.components_
                lignes = modele.transform(standardisee)
                ax.scatter(
                    colonnes[0, :], colonnes[1, :], color="#C44E52", label="Couleur"
                )
                ax.scatter(
                    lignes[:, 0],
                    lignes[:, 1],
                    color="#4C72B0",
                    marker="s",
                    label="Type",
                )
                ax.axhline(0, color="gray", linewidth=0.6)
                ax.axvline(0, color="gray", linewidth=0.6)
                for x_pos, y_pos, etiquette in zip(
                    colonnes[0, :], colonnes[1, :], standardisee.columns
                ):
                    ax.annotate(
                        str(etiquette),
                        (x_pos, y_pos),
                        textcoords="offset points",
                        xytext=(4, 4),
                        color="#C44E52",
                        fontsize=8,
                    )
                for x_pos, y_pos, etiquette in zip(
                    lignes[:, 0], lignes[:, 1], standardisee.index
                ):
                    ax.annotate(
                        str(etiquette),
                        (x_pos, y_pos),
                        textcoords="offset points",
                        xytext=(4, -8),
                        color="#4C72B0",
                        fontsize=7,
                    )
                ax.set_title(titre)
                ax.set_xlabel("Facteur 1")
            axes[0].set_ylabel("Facteur 2")
            axes[0].legend(frameon=False, loc="best")

        self.population.types_gardes = types_gardes

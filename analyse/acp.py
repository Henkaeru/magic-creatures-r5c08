"""ACP des variables numériques des créatures.

Cette classe réalise une analyse en composantes principales (ACP) à partir
de la matrice standardisée des cas complets. Elle écrit les tableaux de
résultats dans le journal et génère les figures `acp_*.png`.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA

from analyse.graphiques import Graphiques
from analyse.population import RANDOM_STATE


class AnalyseACP:
    def __init__(self, population, journal):
        self.population = population
        self.journal = journal
        self.graphiques = Graphiques(journal)

    def executer(self):
        """Réalise l'ACP sur les cas complets, puis écrit le journal et les figures du premier plan.

        Les coordonnées et la part de variance expliquée sont conservées pour chaque
        individu afin de servir à la visualisation des résultats du k-means.
        """
        afficher = self.journal.afficher
        g = self.graphiques
        df = self.population.df
        quantitatif = self.population.quantitatif
        x_scaled = self.population.x_scaled

        pca = PCA(random_state=RANDOM_STATE)
        coordonnees = pca.fit_transform(x_scaled)
        variance = pca.explained_variance_ratio_ * 100
        valeurs_propres = pca.explained_variance_
        cumul = np.cumsum(variance)
        n_composantes_affichees = min(4, len(variance))
        charges_df = pd.DataFrame(
            pca.components_.T * np.sqrt(valeurs_propres),
            index=quantitatif.columns,
            columns=[f"Dim{i + 1}" for i in range(len(variance))],
        )
        tableau_acp = pd.DataFrame(
            {
                "Dimension": [f"Dim{i + 1}" for i in range(len(variance))],
                "Valeur singuliere": pca.singular_values_,
                "Valeur propre": valeurs_propres,
                "% variance": variance,
                "% cumule": cumul,
            }
        )
        n_kaiser = int((valeurs_propres >= 1).sum())

        self.journal.titre("ACP - VALEURS PROPRES")
        afficher(tableau_acp.round(2).to_string(index=False))
        afficher(f"Composantes avec valeur propre >= 1: {n_kaiser}")
        afficher(f"Variance du premier plan (Dim1 + Dim2): {cumul[1]:.1f} %")
        self.journal.tableau(
            "Charges (correlations variable-composante), triees sur Dim1:",
            charges_df.iloc[:, :n_composantes_affichees]
            .sort_values("Dim1", key=lambda serie: serie.abs(), ascending=False)
            .round(3)
            .to_string(),
        )

        extremes = pd.DataFrame(coordonnees[:, :2], columns=["Dim1", "Dim2"])
        extremes["nom"] = df["name"].to_numpy()
        self.journal.tableau("Cartes extremes")
        for dimension in ["Dim1", "Dim2"]:
            afficher(f"\n{dimension} negatif:")
            afficher(
                extremes.nsmallest(8, dimension)[["nom", "Dim1", "Dim2"]]
                .round(2)
                .to_string(index=False)
            )
            afficher(f"\n{dimension} positif:")
            afficher(
                extremes.nlargest(8, dimension)[["nom", "Dim1", "Dim2"]]
                .round(2)
                .to_string(index=False)
            )

        xlabel = f"Dim1 ({variance[0]:.1f} %)"
        ylabel = f"Dim2 ({variance[1]:.1f} %)"

        with g.figure(
            "acp_variance.png",
            (8, 4.5),
            "ACP - part de variance de chaque composante",
            ylabel="% de variance",
        ):
            plt.bar(
                tableau_acp["Dimension"], tableau_acp["% variance"], color="#4C72B0"
            )

        g.eboulis(
            "acp_scree.png",
            valeurs_propres,
            "Composante",
            "ACP - éboulis des valeurs propres",
        )

        with g.figure(
            "acp_correlation.png",
            (8, 6.5),
            "Correlations entre les variables de l'ACP",
        ):
            sns.heatmap(
                quantitatif.corr().round(2),
                annot=True,
                cmap="vlag",
                center=0,
                vmin=-1,
                vmax=1,
            )
            plt.xticks(rotation=40, ha="right")

        with g.figure(
            "acp_cercle.png",
            (7.5, 7.5),
            "ACP - cercle des correlations",
            xlabel=xlabel,
            ylabel=ylabel,
        ):
            for variable in charges_df.index:
                g.fleche(
                    charges_df.loc[variable, "Dim1"],
                    charges_df.loc[variable, "Dim2"],
                    variable,
                )
            plt.gca().add_artist(plt.Circle((0, 0), 1, fill=False, color="gray"))
            g.axes_zero()
            plt.xlim(-1.35, 1.35)
            plt.ylim(-1.35, 1.35)
            plt.gca().set_aspect("equal")

        with g.figure(
            "acp_biplot.png",
            (9, 7),
            "ACP - biplot du premier plan",
            xlabel=xlabel,
            ylabel=ylabel,
        ):
            plt.scatter(
                coordonnees[:, 0], coordonnees[:, 1], s=8, alpha=0.2, color="#4C72B0"
            )
            (x_bas, x_haut), (y_bas, y_haut) = g.cadrer(
                coordonnees[:, 0], coordonnees[:, 1]
            )
            charges = charges_df[["Dim1", "Dim2"]].to_numpy()
            longueurs = np.hypot(charges[:, 0], charges[:, 1])
            cote_court = min(x_haut - x_bas, y_haut - y_bas)
            echelle_fleches = (0.5 * cote_court) / longueurs.max()
            for variable in charges_df.index:
                g.fleche(
                    charges_df.loc[variable, "Dim1"] * echelle_fleches,
                    charges_df.loc[variable, "Dim2"] * echelle_fleches,
                    variable,
                    couleur_fleche="#C44E52",
                    couleur_texte="#C44E52",
                    head_width=0.035 * longueurs.max() * echelle_fleches,
                )
            g.axes_zero()

        with g.figure(
            "acp_individus.png",
            (8, 6),
            "ACP - plan factoriel des creatures",
            xlabel=xlabel,
            ylabel=ylabel,
        ):
            plt.scatter(
                coordonnees[:, 0], coordonnees[:, 1], s=8, alpha=0.25, color="#4C72B0"
            )
            g.cadrer(coordonnees[:, 0], coordonnees[:, 1])
            g.axes_zero()

        palette = plt.get_cmap("Dark2")
        ordre_groupes = ["Incolore", "Monocolore", "Multicolore"]
        couleurs_groupes = {nom: palette(i) for i, nom in enumerate(ordre_groupes)}
        with g.figure(
            "acp_individus_couleurs.png",
            (8, 6),
            "ACP - creatures selon l'identite de couleur",
            xlabel=xlabel,
            ylabel=ylabel,
            legende=True,
            legende_kw={"frameon": False},
        ):
            for nom in ordre_groupes:
                masque = df["groupe_couleur"].to_numpy() == nom
                plt.scatter(
                    coordonnees[masque, 0],
                    coordonnees[masque, 1],
                    s=8,
                    alpha=0.3,
                    color=couleurs_groupes[nom],
                    label=f"{nom} ({masque.sum()})",
                )
            g.cadrer(coordonnees[:, 0], coordonnees[:, 1])
            g.axes_zero()

        self.population.coordonnees = coordonnees
        self.population.variance = variance

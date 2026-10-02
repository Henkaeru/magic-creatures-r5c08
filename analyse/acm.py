"""ACM de la couleur, de la rareté et du type principal.

Chaque ligne correspond à une créature, y compris celles qui ne possèdent
pas de force numérique. Les types trop rares sont regroupés dans `Autre`.
La classe génère le plan des modalités.
"""

import matplotlib.pyplot as plt
import pandas as pd
from mca import MCA

from analyse.graphiques import Graphiques
from analyse.population import groupe_couleur, morceaux


class AnalyseACM:
    """Chaque créature est comptée une seule fois. Le type principal correspond
    au premier sous-type, tandis que les types rares sont regroupés dans
    `Autre`.
    """

    def __init__(self, population, journal):
        self.population = population
        self.journal = journal
        self.graphiques = Graphiques(journal)

    def executer(self):
        """Réalise l'ACM sur l'ensemble des créatures, à partir des types fréquents identifiés par l'AFC.

        Les coordonnées des modalités sont écrites dans le journal et représentées
        dans `acm_modalites.png`.
        """
        types_frequents = set(self.population.types_gardes)
        df_acm = self.population.creatures.copy()
        df_acm["groupe_couleur"] = df_acm["color_identity"].map(groupe_couleur)
        df_acm["type_principal"] = df_acm["subtypes"].map(
            lambda valeur: (morceaux(valeur) or ["Sans type"])[0]
        )
        df_acm.loc[
            ~df_acm["type_principal"].isin(types_frequents), "type_principal"
        ] = "Autre"
        df_acm["rarete_acm"] = df_acm["rarity"].fillna("inconnue")
        rares = df_acm["rarete_acm"].value_counts()
        df_acm.loc[df_acm["rarete_acm"].isin(rares[rares < 50].index), "rarete_acm"] = (
            "autre"
        )

        variables_acm = ["groupe_couleur", "rarete_acm", "type_principal"]
        disjonctif = pd.get_dummies(df_acm[variables_acm].astype(str)).astype(int)
        acm = MCA(disjonctif, benzecri=False)
        coord_modalites = acm.fs_c()

        self.journal.titre("ACM")
        self.journal.afficher(
            f"Tableau disjonctif: {disjonctif.shape[0]} creatures, {disjonctif.shape[1]} modalites"
        )
        self.journal.afficher(
            pd.DataFrame(
                coord_modalites[:, :2],
                index=disjonctif.columns,
                columns=["Axe1", "Axe2"],
            )
            .round(3)
            .to_string()
        )

        with self.graphiques.figure(
            "acm_modalites.png",
            (11, 8),
            "ACM - couleur, rarete et type principal",
            xlabel="Axe 1",
            ylabel="Axe 2",
        ):
            plt.scatter(coord_modalites[:, 0], coord_modalites[:, 1], color="#4C72B0")
            for indice, (x_pos, y_pos, nom) in enumerate(
                zip(coord_modalites[:, 0], coord_modalites[:, 1], disjonctif.columns)
            ):
                plt.annotate(
                    nom.replace("groupe_couleur_", "couleur ")
                    .replace("rarete_acm_", "rarete ")
                    .replace("type_principal_", "type "),
                    xy=(x_pos, y_pos),
                    xytext=(5, 7 if indice % 2 == 0 else -10),
                    textcoords="offset points",
                    fontsize=8,
                )
            self.graphiques.axes_zero()

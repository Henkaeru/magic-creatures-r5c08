"""K-means et classification ascendante hiérarchique.

Les deux méthodes utilisent la même matrice standardisée que celle de l'ACP.

Le dendrogramme ne porte pas sur l'ensemble des créatures : il est construit
à partir d'un échantillon fixe de 3 000 créatures, avec une graine fixée à 0.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering, KMeans

from analyse.graphiques import Graphiques
from analyse.population import RANDOM_STATE

TAILLE_CAH = 3000


def plot_dendrogram(model, **kwargs):
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count
    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)
    dendrogram(linkage_matrix, **kwargs)


def coude(ks, inerties):
    debut = np.array([ks[0], inerties[0]], dtype=float)
    fin = np.array([ks[-1], inerties[-1]], dtype=float)
    segment = fin - debut
    longueurs = []
    for k, inertie in zip(ks, inerties):
        point = np.array([k, inertie], dtype=float)
        produit = segment[0] * (debut[1] - point[1]) - segment[1] * (
            debut[0] - point[0]
        )
        longueurs.append(abs(produit) / np.linalg.norm(segment))
    return int(ks[int(np.argmax(longueurs))])


class Partitionnement:
    def __init__(self, population, journal):
        self.population = population
        self.journal = journal
        self.graphiques = Graphiques(journal)

    def executer(self):
        """Réalise le k-means pour k allant de 2 à 10, puis une CAH de Ward sur 3 000 créatures.

        Les inerties, les profils des groupes et les figures `clustering_*.png`
        sont générés à la fin.
        """
        afficher = self.journal.afficher
        g = self.graphiques
        df = self.population.df
        x_scaled = self.population.x_scaled
        coordonnees = self.population.coordonnees
        variance = self.population.variance

        ks = list(range(2, 11))
        inerties = [
            float(
                KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE)
                .fit(x_scaled)
                .inertia_
            )
            for k in ks
        ]
        k_choisi = coude(ks, inerties)
        kmeans = KMeans(n_clusters=k_choisi, n_init=10, random_state=RANDOM_STATE)
        groupes = kmeans.fit_predict(x_scaled)

        self.journal.titre("K-MEANS")
        for k, inertie in zip(ks, inerties):
            afficher(f"k = {k}: inertie = {inertie:.1f}")
        afficher(f"k retenu par la regle du coude: {k_choisi}")

        profil = pd.DataFrame(
            {
                "mana": df["mana_value_num"].to_numpy(),
                "prix": df["retail_price_num"].to_numpy(),
                "impressions": df["printing_count_num"].to_numpy(),
                "force": df["power_num"].to_numpy(),
                "endurance": df["toughness_num"].to_numpy(),
                "rarete": df["rarity_rank_num"].to_numpy(),
                "groupe": groupes,
            }
        )
        self.journal.tableau(
            "Effectifs:", profil["groupe"].value_counts().sort_index().to_string()
        )
        self.journal.tableau(
            "Moyennes par groupe:", profil.groupby("groupe").mean().round(2).to_string()
        )
        self.journal.tableau("Exemples proches du centre:")
        for groupe in range(k_choisi):
            masque = groupes == groupe
            distances = np.linalg.norm(
                x_scaled[masque] - kmeans.cluster_centers_[groupe], axis=1
            )
            noms = df.loc[masque, "name"].to_numpy()
            afficher(f"Groupe {groupe}: " + ", ".join(noms[np.argsort(distances)[:8]]))

        with g.figure(
            "clustering_inertie.png",
            (8, 4.5),
            "K-means - perte d'inertie",
            xlabel="Nombre de groupes",
            ylabel="Inertie",
            grille=True,
            legende=True,
        ):
            plt.plot(ks, inerties, marker="o")
            plt.axvline(
                k_choisi, color="red", linestyle="--", label=f"k retenu = {k_choisi}"
            )

        palette = plt.get_cmap("Dark2")
        with g.figure(
            "clustering_plan.png",
            (8, 6),
            "K-means sur le premier plan factoriel",
            xlabel=f"Dim1 ({variance[0]:.1f} %)",
            ylabel=f"Dim2 ({variance[1]:.1f} %)",
            legende=True,
            legende_kw={"frameon": False, "markerscale": 2},
        ):
            for groupe in range(k_choisi):
                masque = groupes == groupe
                plt.scatter(
                    coordonnees[masque, 0],
                    coordonnees[masque, 1],
                    s=8,
                    alpha=0.3,
                    color=palette(groupe),
                    label=f"Groupe {groupe} ({masque.sum()})",
                )
            g.cadrer(coordonnees[:, 0], coordonnees[:, 1])
            g.axes_zero()

        generateur = np.random.default_rng(RANDOM_STATE)
        indice_cah = generateur.choice(
            len(df), size=min(TAILLE_CAH, len(df)), replace=False
        )
        cah = AgglomerativeClustering(distance_threshold=0, n_clusters=None)
        cah.fit(x_scaled[indice_cah])
        with g.figure(
            "clustering_dendrogramme.png",
            (11, 5),
            f"CAH tronquee (echantillon de {len(indice_cah)} creatures)",
            xlabel="Nombre de creatures dans la classe (ou indice sans parentheses)",
        ):
            plot_dendrogram(cah, truncate_mode="level", p=4)
        afficher()
        afficher(
            f"CAH: echantillon fixe de {len(indice_cah)} creatures, graine {RANDOM_STATE}, dendrogramme tronque au niveau 4."
        )

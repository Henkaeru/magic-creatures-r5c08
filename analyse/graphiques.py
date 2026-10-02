"""Cadre commun pour les figures : ouverture, axes et enregistrement.

Le module ouvre une figure, définit le titre et les axes, puis demande au
journal d'enregistrer le fichier PNG. Il ne réalise ni l'ACP ni le calcul
des groupes.
"""

from contextlib import contextmanager

import matplotlib.pyplot as plt
import numpy as np

DECALAGE_ETIQUETTE = {
    "mana": (8, 16),
    "force": (8, 2),
    "endurance": (8, -14),
    "impressions (log)": (6, 14),
    "prix (log)": (6, 0),
    "rarete": (8, -12),
}


class Graphiques:
    def __init__(self, journal):
        self.journal = journal

    @contextmanager
    def figure(
        self,
        nom,
        figsize,
        titre,
        xlabel=None,
        ylabel=None,
        grille=False,
        legende=False,
        legende_kw=None,
    ):
        plt.figure(figsize=figsize)
        yield
        if xlabel is not None:
            plt.xlabel(xlabel)
        if ylabel is not None:
            plt.ylabel(ylabel)
        plt.title(titre)
        if grille:
            plt.grid(True, alpha=0.3)
        if legende:
            plt.legend(**(legende_kw or {}))
        self.journal.sauver(nom)

    @staticmethod
    def axes_zero():
        plt.axhline(0, color="gray", linewidth=0.6)
        plt.axvline(0, color="gray", linewidth=0.6)

    @staticmethod
    def cadrer(x, y, marge=0.08):
        def cote(valeurs):
            ordre = np.sort(np.asarray(valeurs, dtype=float))
            bas, haut = float(ordre[0]), float(ordre[-1])
            if len(ordre) < 2:
                return bas, haut
            if haut > 0 and ordre[-2] > 0 and haut > 2 * float(ordre[-2]):
                haut = float(ordre[-2])
            if bas < 0 and ordre[1] < 0 and bas < 2 * float(ordre[1]):
                bas = float(ordre[1])
            return bas, haut

        x_bas, x_haut = cote(x)
        y_bas, y_haut = cote(y)
        dx = (x_haut - x_bas) * marge
        dy = (y_haut - y_bas) * marge
        plt.xlim(x_bas - dx, x_haut + dx)
        plt.ylim(y_bas - dy, y_haut + dy)
        return plt.xlim(), plt.ylim()

    def eboulis(self, nom, valeurs, xlabel, titre, figsize=(8, 4.5)):
        with self.figure(
            nom,
            figsize,
            titre,
            xlabel=xlabel,
            ylabel="Valeur propre",
            grille=True,
            legende=True,
        ):
            plt.plot(range(1, len(valeurs) + 1), valeurs, marker="o")
            plt.axhline(1, color="red", linestyle="--", label="Seuil de Kaiser = 1")
            plt.xticks(range(1, len(valeurs) + 1))

    @staticmethod
    def fleche(
        x_pos,
        y_pos,
        texte,
        couleur_fleche="#333333",
        couleur_texte="black",
        head_width=0.03,
    ):
        plt.arrow(
            0,
            0,
            x_pos,
            y_pos,
            head_width=head_width,
            length_includes_head=True,
            color=couleur_fleche,
        )
        dx, dy = DECALAGE_ETIQUETTE.get(texte, (6, 6))
        plt.annotate(
            texte,
            xy=(x_pos, y_pos),
            xytext=(dx, dy),
            textcoords="offset points",
            color=couleur_texte,
            fontsize=9,
        )

    @contextmanager
    def sous_figures(self, nom, titre, **kwargs):
        fig, axes = plt.subplots(**kwargs)
        yield fig, axes
        fig.suptitle(titre)
        self.journal.sauver(nom)

"""Journal des tableaux et enregistrement des figures.

Il reçoit le texte produit par les analyses et l'écrit dans
`figures/resultats.txt` à la fin. Les fichiers PNG sont enregistrés via
`save`. Ce fichier n'effectue aucun calcul.
"""

from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


class Journal:
    def __init__(self, figures=None):
        self.figures = Path(figures) if figures is not None else ROOT / "figures"
        self.figures.mkdir(exist_ok=True)
        self.lignes = []

    def afficher(self, texte=""):
        print(texte)
        self.lignes.append(str(texte))

    def titre(self, texte, saut=True):
        if saut:
            self.afficher()
        barre = "=" * 70
        self.afficher(barre)
        self.afficher(texte)
        self.afficher(barre)

    def tableau(self, legende, contenu=None):
        self.afficher()
        self.afficher(legende)
        if contenu is not None:
            self.afficher(contenu)

    def sauver(self, nom):
        plt.tight_layout()
        plt.savefig(self.figures / nom, dpi=120)
        plt.close()

    def ecrire(self):
        (self.figures / "resultats.txt").write_text(
            "\n".join(self.lignes) + "\n", encoding="utf-8"
        )
        print(f"\nFigures enregistrees dans {self.figures}")

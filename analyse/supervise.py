"""K plus proches voisins et arbre de décision sur la classe de prix.

Le prix est la variable cible, répartie en cinq classes selon les quantiles
de l'apprentissage, et n'est pas utilisé comme prédicteur. Aucune figure
n'est générée : seules les exactitudes sont écrites dans le journal.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from analyse.population import RANDOM_STATE


class ApprentissageSupervise:
    def __init__(self, population, journal):
        self.population = population
        self.journal = journal

    def executer(self):
        """Prédit la classe de prix des cas complets sans utiliser le prix comme prédicteur.

        Dix découpes de 20 % pour le test. Les cinq seuils sont les quantiles
        du prix d'apprentissage, appliqués ensuite au test. Les exactitudes
        moyennes sont écrites dans le journal.
        """
        afficher = self.journal.afficher
        df = self.population.df
        quantitatif = self.population.quantitatif
        etiquettes = ["Très bas", "Bas", "Moyen", "Élevé", "Très élevé"]
        predicteurs = [
            colonne for colonne in quantitatif.columns if colonne != "prix (log)"
        ]
        x_bonus = quantitatif[predicteurs]
        prix = df["retail_price_num"].to_numpy()
        k_voisins = [3, 5, 7, 11, 15]
        scores = {f"kNN k={k}": [] for k in k_voisins}
        scores["arbre gini"] = []
        scores["arbre entropie"] = []
        majorites = []

        for tirage in range(10):
            i_train, i_test = train_test_split(
                np.arange(len(df)), test_size=0.2, random_state=tirage
            )
            seuils = np.quantile(prix[i_train], [0.2, 0.4, 0.6, 0.8])
            for i in range(1, len(seuils)):
                if seuils[i] <= seuils[i - 1]:
                    seuils[i] = np.nextafter(seuils[i - 1], np.inf)
            bornes = np.concatenate(([-np.inf], seuils, [np.inf]))
            y_train = pd.cut(
                prix[i_train], bins=bornes, labels=etiquettes, include_lowest=True
            ).astype(str)
            y_test = pd.cut(
                prix[i_test], bins=bornes, labels=etiquettes, include_lowest=True
            ).astype(str)
            majorites.append(
                float(pd.Series(y_test).value_counts(normalize=True).max())
            )
            x_train = x_bonus.iloc[i_train]
            x_test = x_bonus.iloc[i_test]
            scaler_split = StandardScaler()
            x_train_std = scaler_split.fit_transform(x_train)
            x_test_std = scaler_split.transform(x_test)
            for k in k_voisins:
                modele = KNeighborsClassifier(n_neighbors=k)
                modele.fit(x_train_std, y_train)
                scores[f"kNN k={k}"].append(
                    accuracy_score(y_test, modele.predict(x_test_std))
                )
            for cle, critere in [("arbre gini", "gini"), ("arbre entropie", "entropy")]:
                arbre = DecisionTreeClassifier(
                    criterion=critere, random_state=RANDOM_STATE
                )
                arbre.fit(x_train, y_train)
                scores[cle].append(accuracy_score(y_test, arbre.predict(x_test)))

        self.journal.titre("APPRENTISSAGE SUPERVISE")
        afficher(
            "Cible: 5 quantiles du prix d'apprentissage, parmi les creatures de l'ACP"
        )
        afficher("Predicteurs: " + ", ".join(predicteurs))
        afficher(
            f"Part moyenne de la plus grande classe de test: {np.mean(majorites):.3f}"
        )
        afficher("Exactitude moyenne sur 10 decoupes (20 % de test):")
        for nom, valeurs in scores.items():
            afficher(
                f"  {nom}: {np.mean(valeurs):.3f} (ecart-type {np.std(valeurs):.3f})"
            )

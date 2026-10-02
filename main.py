#!/usr/bin/env python3
"""Point d'entrée du projet.

S'assure que `data/cards.csv` existe et contient les prix du jour, puis lance
les analyses du cours dans l'ordre. Ce fichier ne réalise pas les calculs :
il appelle les différentes classes et fait enregistrer les résultats dans
`figures/resultats.txt`.
"""

from analyse import (
    AnalyseACP,
    AnalyseAFC,
    AnalyseACM,
    ApprentissageSupervise,
    Journal,
    Partitionnement,
    PopulationCreatures,
)
from construire_cartes import ConstructeurCartes


def main():
    """Construit le CSV, puis enchaîne l'ACP, l'AFC, l'ACM, le partitionnement et le bonus.

    Si le cache MTGJSON contient déjà les données du jour, il est conservé.
    Sinon, `AllPricesToday` est mis à jour avant de recalculer les figures.
    """
    # ConstructeurCartes().construire()
    journal = Journal()
    population = PopulationCreatures(journal)
    population.charger()
    AnalyseACP(population, journal).executer()
    AnalyseAFC(population, journal).executer()
    AnalyseACM(population, journal).executer()
    Partitionnement(population, journal).executer()
    ApprentissageSupervise(population, journal).executer()
    journal.ecrire()


if __name__ == "__main__":
    main()

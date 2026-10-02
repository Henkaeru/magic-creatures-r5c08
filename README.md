# Créatures Magic : taille, couleur et type

Projet R5.C.08 (IUT de Lannion).

À partir des cartes de *Magic: The Gathering*, nous étudions les créatures afin de déterminer si leur taille est liée à leur coût et à leur prix, et si leur type de créature est lié à leur couleur.

Tout le nécessaire se trouve dans ce dossier.

Le fichier analysé est `data/cards.csv`, où chaque ligne correspond à une carte.

La signification des colonnes est détaillée dans `data/extraction.txt`.

## Lancer le projet

La ligne `ConstructeurCartes` est commentée dans `main.py` afin de conserver le fichier `cards.csv` utilisé pour le rapport. L'exécution de `main.py` lance ainsi directement les analyses sans reconstruire le fichier.

Pour mettre à jour les données, la ligne peut être décommentée. `ConstructeurCartes` télécharge alors, si nécessaire, deux fichiers publics depuis MTGJSON (`[https://mtgjson.com/api/v5/](https://mtgjson.com/api/v5/)`) :

* `AllPrintings.sqlite`, qui contient les cartes et leurs éditions (environ 660 Mo) ;
* `AllPricesToday.json.gz`, qui contient les prix de vente au détail du jour (taille variable).

Ces fichiers sont enregistrés dans `data/cache`. Le script génère ensuite `data/cards.csv`, avec une ligne par nom de carte.

Le fichier contient notamment le texte des cartes, leurs types, leurs mots-clés, leur légalité dans chaque format, leur statut de *game changer*, leurs rôles de commandant, leur rang EDHREC ainsi que leur prix moyen en dollars pour la vente au détail de cartes physiques en finition normale (TCGPlayer, Card Kingdom et Mana Pool).

Les caractéristiques liées à l'édition sont récupérées à partir de l'impression la plus récente. La liste complète des colonnes est disponible dans `data/extraction.txt`.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

`AllPrintings.sqlite` est conservé dans le cache. `AllPricesToday.json.gz` est retéléchargé lorsque la date indiquée dans le fichier n'est pas celle du jour.

Le fichier `cards.csv` est alors régénéré avec les prix mis à jour.

Le cache peut être supprimé à tout moment : il suffit de relancer `main.py` (ou `construire_cartes.py`) pour télécharger à nouveau les fichiers nécessaires.

Les classes du dossier `analyse/` génèrent ensuite les graphiques dans `figures/` ainsi que les tableaux de résultats dans `figures/resultats.txt`.

Le rapport final est `rapport/rapport.pdf`. `rapport/rapport.sh` le régénère à partir de `rapport/rapport.md`.

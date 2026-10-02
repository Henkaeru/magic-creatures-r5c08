Notes de lecture, avant la mise en page.

## Population

`cards.csv` contient 35 081 lignes, dont 19 169 créatures. Pour l'ACP, on garde 18 025 cas complets et on en écarte 1 144. Dans cette population ACP, on compte 13 664 créatures monocolores, 3 577 multicolores et 784 incolores. La standardisation donne bien une moyenne de 0 et un écart-type de 1 sur les six colonnes.

## Corrélations

Force et endurance : 0,74. Force et mana : 0,67. Endurance et mana : 0,65. Prix et rareté : 0,50. Prix et impressions : 0,30. Prix et mana : 0,14. Prix et force : 0,14. Prix et endurance : 0,17. Rareté et impressions : 0,34. Impressions et mana : 0,05.

Le gabarit est donc cohérent : force, endurance et mana évoluent ensemble. Le prix est surtout lié à la rareté, un peu aux rééditions, et très peu à la taille.

## ACP

Valeurs propres : Dim1 = 2,67 (44,52 %), Dim2 = 1,51 (25,15 %, cumul 69,67 %), Dim3 = 0,72 (11,99 %, cumul 81,66 %), puis 0,48, 0,36 et 0,25. Avec le critère de Kaiser, on retient deux composantes. Le premier plan représente 69,7 % de la variance.

Charges, triées sur Dim1 dans le journal :

* endurance : 0,837 / -0,319 / 0,051
* force : 0,833 / -0,352 / 0,072
* mana : 0,801 / -0,330 / 0,012
* rareté : 0,583 / 0,572 / -0,229
* prix (log) : 0,452 / 0,656 / -0,416
* impressions (log) : 0,301 / 0,646 / 0,697

Dim1 correspond principalement au gabarit : les trois variables de taille dépassent 0,80. Le prix n'est qu'à 0,452 et la rareté à 0,583. Une grosse créature n'est donc pas, selon cet axe, une créature chère.

Dim2 met plutôt en opposition le prix (0,656), les impressions (0,646) et la rareté (0,572) avec le gabarit, qui charge négativement : force -0,352, mana -0,330, endurance -0,319. En haut du plan, on trouve donc plutôt des cartes petites ou moyennes, chères et rééditées. En bas, des créatures avec un gros gabarit, mais qui ne correspondent pas à ce profil de prix et de rééditions.

Dim3 a une valeur propre de 0,72, donc sous le seuil de Kaiser. On ne l'ajoute pas au plan. On la note quand même parce que les impressions y chargent à 0,697 et le prix à -0,416. Rééditer et coûter cher ne correspondent donc pas exactement au même axe. On le garde comme élément de lecture, pas comme troisième composante retenue.

Cartes extrêmes. Sur Dim1 positif : B.F.M. (Big Furry Monster) à 57,98, puis Emrakul, the Aeons Torn à 12,32, Emrakul, the Promised End à 10,50, Emrakul and Chatterfang à 10,43, Worldspine Wurm à 10,38 et Impervious Greatwurm à 10,03. La carte-blague est environ cinq fois plus loin que la suivante, dans la même direction. L'échelle du nuage est donc fortement étirée par B.F.M. Le sens de l'axe reste cependant celui des grosses créatures, et les charges sont calculées sur les 18 025 lignes.

Sur Dim1 négatif : Half-Squirrel autour de -3,10, Clockwork Beetle à -3,05, puis Spike Drone, Iron Apprentice et Little Girl. Sur Dim2 positif : Birds of Paradise à 6,90, Cloud Midgar Mercenary, Lord of Atlantis, Royal Assassin, Vesuvan Doppelganger et Snapcaster Mage. Sur Dim2 négatif : B.F.M. encore, puis Autochthon Wurm à -4,14, Rust Goliath et Kozilek Compleated.

Colorer le plan en incolore, monocolore et multicolore ne sépare pas le nuage. La couleur n'organise donc pas directement le gabarit ou le prix sur ce plan.

## AFC

On obtient 41 688 couples avant filtrage. On garde les 24 types présents au moins 400 fois. Le tableau final contient 24 088 couples et concerne 12 909 créatures distinctes. Bartlett : 66,83, p = 1,628e-08. Khi-deux d'indépendance : 13 705,69, 115 ddl, p affichée à 0. Valeurs propres des facteurs : 3,653, 1,012, 0,539, 0,308, 0,264 et 0,225. Deux facteurs dépassent 1.

Une carte peut remplir plusieurs cases. Le test est donc très significatif, mais les 24 088 cases comptées ne correspondent pas à 24 088 cartes indépendantes.

Les effectifs bruts mélangent deux choses : " ce type est fréquent " et " ce type est associé à une couleur ". Pour distinguer les deux, on regarde la part de chaque case dans la somme de sa ligne.

Human : 1962 + 1228 + 1064 + 1225 + 874 + 8 = 6361. Blanc : 1962/6361 = 30,8 %. Bleu : 19,3 %, rouge : 19,3 %, noir : 16,7 %, vert : 13,7 %. Le blanc est la plus grande case, mais la ligne Human occupe les cinq couleurs. Lire " surtout blanc " à partir du seul 1 962 confondrait donc l'effectif du type avec sa répartition par couleur.

Goblin : 8 + 17 + 92 + 507 + 39 + 2 = 665. Rouge : 507/665 = 76,2 %.

Druid : 43 + 40 + 37 + 32 + 398 = 550. Vert : 398/550 = 72,4 %.

Merfolk : 27 + 300 + 16 + 9 + 67 = 419. Bleu : 300/419 = 71,6 %.

Zombie : 31 + 112 + 542 + 47 + 45 + 1 = 778. Noir : 542/778 = 69,7 %.

Vampire : 77 + 31 + 358 + 92 + 5 = 563. Noir : 358/563 = 63,6 %.

Elf : 95 + 75 + 126 + 52 + 602 = 950. Vert : 602/950 = 63,4 %.

Cleric : 507 + 44 + 199 + 47 + 65 + 2 = 864. Blanc : 507/864 = 58,7 %.

Soldier : 765 + 144 + 123 + 203 + 107 + 7 = 1349. Blanc : 765/1349 = 56,7 %.

Wizard : 223 + 910 + 270 + 255 + 144 + 4 = 1806. Bleu : 910/1806 = 50,4 %.

Dragon : 88 + 110 + 99 + 286 + 110 + 18 = 711. Rouge : 286/711 = 40,2 %. Le reste est réparti entre les autres couleurs, avec 15,5 % pour le bleu et le vert, 13,9 % pour le noir et 12,4 % pour le blanc.

Warrior : 293 + 104 + 270 + 593 + 438 + 3 = 1701. Rouge : 593/1701 = 34,9 %. Vert : 438/1701 = 25,7 %. Il n'y a donc pas une seule couleur dominante au même niveau que pour Goblin ou Druid.

Phyrexian : 88 + 77 + 217 + 66 + 95 + 45 = 588. Noir : 217/588 = 36,9 %. Incolore : 45/588 = 7,7 %. Les 45 sont le plus gros effectif de la colonne Incolore, mais cela reste une petite part de la ligne Phyrexian.

La somme des 24 lignes du script de contrôle donne bien 24 088, soit le total imprimé.

Sans rotation, le premier facteur isole surtout Human, qui est la ligne la plus lourde. Avec Varimax, le vert et le rouge se rapprochent d'Elf, Druid et Warrior, tandis que le noir et le bleu se rapprochent de Zombie et Wizard. Quartimax reste proche de la solution brute. On garde deux facteurs.

Pour l'interprétation, le détail des couleurs se lit surtout avec les parts de ligne. Le nuage montre davantage quels types contribuent aux axes.

## ACM

19 169 créatures et 33 modalités. ACM sans correction de Benzécri. Une ligne par créature, avec comme type principal le premier sous-type, et " Autre " dans les autres cas.

L'AFC comptait chaque sous-type, donc les deux analyses ne reposent pas exactement sur la même construction. Dans l'ACM, Soldier, Knight, Artificer et Cleric partent sur l'axe 2 : Soldier 8,404, Artificer 9,133, Knight 5,240 et Cleric 3,673. Ils sont rares comme premier type, alors que l'AFC les trouve fréquents quand tous leurs sous-types sont comptés.

Sur l'axe 1, on trouve le multicolore à -1,439 et le mythique à -1,865, près de Dragon à -1,790 et Rogue à -2,858, en face de la modalité commune à 0,900. L'incolore est isolé sur l'axe 2 à 3,608.

Shaman et Warrior ont les mêmes coordonnées imprimées, 3,710 et -1,434. On le note, sans chercher à en déduire une raison qui n'est pas donnée par les résultats.

## K-means

Inerties :

* k = 2 : 79 161,1
* k = 3 : 65 991,4
* k = 4 : 58 129,7
* k = 5 : 51 673,3
* k = 6 : 46 500,1
* k = 7 : 43 000,2
* k = 8 : 40 378,4
* k = 9 : 38 209,8
* k = 10 : 36 323,5

Le coude à k = 5 reste assez mou. Un k voisin resterait donc défendable.

Moyennes, dans l'ordre mana, prix, impressions, force, endurance, rareté, avec les cartes déjà listées comme proches du centre :

Groupe 0, n = 1 684 : 6,48 / 3,00 / 3,94 / 5,97 / 6,07 / 3,06. Numot, the Devastator, Gilgamesh, Master-at-Arms, Elder Brain. Ce sont de grosses créatures, plutôt rares, avec un prix modéré.

Groupe 1, n = 4 332 : 4,72 / 0,36 / 1,69 / 3,43 / 3,64 / 1,83. Memory Guardian, Henge Guardian. Gabarit moyen, prix faible et peu de rééditions.

Groupe 2, n = 6 690 : 2,47 / 0,34 / 1,69 / 1,65 / 1,83 / 1,42. Mother Bear, Throne Warden. Petites créatures, plutôt communes.

Groupe 3, n = 3 870 : 3,09 / 1,05 / 5,29 / 2,13 / 2,41 / 2,72. Squee, Dubious Monarch, Vaan, Street Thief. Plusieurs impressions et un gabarit modeste.

Groupe 4, n = 1 449 : 3,81 / 27,87 / 4,79 / 2,76 / 3,15 / 3,29. Graveborn Muse, Kalemne, Disciple of Iroas, Michiko Konda, Truth Seeker. Le gabarit moyen est ordinaire : mana 3,81 et force 2,76. La moyenne de prix à 27,87 est tirée par une distribution très dissymétrique. L'ACP elle-même travaille avec le logarithme du prix. On ne donne pas de médiane, puisqu'elle n'apparaît pas dans le journal.

Le groupe cher n'est donc pas le groupe des grosses créatures. Dim1 porte surtout le groupe 0, tandis que Dim2 porte le prix du groupe 4 et les rééditions du groupe 3.

## CAH

CAH réalisée sur un échantillon de 3 000 créatures, avec graine 0 et troncature au niveau 4. Le plus grand espace vertical du dendrogramme sépare deux grandes familles. On ne force pas ce découpage à correspondre à cinq groupes.

## Supervisé

Cinq quantiles pour créer les classes de prix, avec une classe majoritaire à 0,200. Les prédicteurs n'utilisent pas le prix. Dix découpes 80/20.

* kNN, k = 3 : 0,383 (0,008)
* kNN, k = 5 : 0,394 (0,011)
* kNN, k = 7 : 0,409 (0,010)
* kNN, k = 11 : 0,420 (0,005)
* kNN, k = 15 : 0,425 (0,005)

L'exactitude augmente avec k. L'écart-type est plus faible à k = 11 et k = 15 qu'à k = 3. Un voisinage plus large fonctionne donc mieux qu'un petit voisinage. Le signal semble plutôt grossier, notamment du côté de la rareté, qui corrèle à 0,50 avec le prix, que lié à un motif local de force et d'endurance.

Les arbres avec Gini et entropie donnent tous les deux 0,407. Le critère ne change donc pratiquement rien.

Avec 0,425 contre 0,200 pour la classe majoritaire, on dépasse le niveau d'une prédiction systématique de la classe la plus fréquente. À 42,5 % de cartes correctement classées, plus de la moitié des créatures de test restent cependant mal classées. Le gabarit ne suffit donc pas à deviner le prix. C'est cohérent avec la lecture de l'ACP.

## Ce que le rapport doit dire, et ne pas surinterpréter

La taille, le mana et l'endurance vont ensemble. Le prix est surtout lié à la rareté, et un peu aux rééditions. Les groupes séparent notamment les grosses créatures et les créatures chères.

Certains types sont fortement associés à une couleur : Goblin, Druid, Merfolk, Zombie, Elf ou Vampire. Les Humains sont présents dans toutes les couleurs, avec le blanc comme plus grande case. Les Dragons ne se résument pas au rouge.

Dim3 n'est pas retenue. B.F.M. étire fortement l'échelle du premier plan. Le coude du k-means reste mou. La CAH n'est pas réalisée sur les 18 025 créatures, mais sur un échantillon de 3 000. Les parts de ligne de l'AFC ne représentent pas des cartes comptées une seule fois.

## Groupe

Keren Courtois et Célestin Cécilien.
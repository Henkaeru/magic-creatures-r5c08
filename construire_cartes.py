#!/usr/bin/env python3
"""Télécharge les données de MTGJSON et génère `data/cards.csv`.

Les sources, disponibles sur `https://mtgjson.com/api/v5/`, sont
`AllPrintings.sqlite`, qui contient les cartes et leurs éditions, et
`AllPricesToday.json.gz`, qui contient le dernier prix de vente au détail
pour chaque impression.

Chaque ligne du CSV correspond à un nom de carte. Les caractéristiques
d'édition sont récupérées à partir de l'impression la plus récente. Les
légalités, le rang EDHREC, le statut de *game changer* et les rôles de
commandant sont regroupés par nom de carte, car certaines impressions
promotionnelles ou certaines faces peuvent ne pas contenir ces informations.

Le prix correspond à la moyenne, en dollars, du prix de vente au détail
des cartes physiques en finition normale chez TCGPlayer, Card Kingdom et
Mana Pool.
"""

import gzip
import json
import re
import sqlite3
import urllib.request
from datetime import date, datetime
from pathlib import Path

import pandas as pd


class ConstructeurCartes:
    """Construit `data/cards.csv` à partir des fichiers publics de MTGJSON."""

    ROOT = Path(__file__).resolve().parent
    DATA = ROOT / "data"
    CACHE = DATA / "cache"
    OUT = DATA / "cards.csv"
    NOTE = DATA / "extraction.txt"

    BASE = "https://mtgjson.com/api/v5"
    ALL_PRINTINGS = "AllPrintings.sqlite"
    ALL_PRICES_TODAY = "AllPricesToday.json.gz"
    PRINTINGS_URL = f"{BASE}/{ALL_PRINTINGS}"
    PRICES_URL = f"{BASE}/{ALL_PRICES_TODAY}"

    # Prix papier en dollars. Cardmarket est en euros, on ne le mélange pas.
    FOURNISSEURS_USD = {"tcgplayer", "cardkingdom", "manapool"}

    RARITY_RANK = {
        "common": 1.0,
        "uncommon": 2.0,
        "rare": 3.0,
        "mythic": 4.0,
        "special": 5.0,
        "bonus": 6.0,
    }

    # Colonnes de cardLegalities. Le statut vide des promos est ignore.
    FORMATS = (
        "alchemy",
        "brawl",
        "commander",
        "competitivebrawl",
        "duel",
        "future",
        "gladiator",
        "historic",
        "legacy",
        "modern",
        "oathbreaker",
        "oldschool",
        "pauper",
        "paupercommander",
        "penny",
        "pioneer",
        "predh",
        "premodern",
        "standard",
        "standardbrawl",
        "timeless",
        "tlr",
        "vintage",
    )

    # Cles du JSON leadershipSkills.
    LEADERSHIP = {
        "commander": "can_commander",
        "brawl": "can_brawl",
        "oathbreaker": "can_oathbreaker",
        "pauper_commander": "can_pauper_commander",
        "predh": "can_predh",
    }

    DRAPEAUX = (
        "is_reprint",
        "is_promo",
        "is_funny",
        "is_textless",
        "is_full_art",
        "is_oversized",
        "is_online_only",
        "is_alternative",
        "is_rebalanced",
        "is_timeshifted",
        "is_story_spotlight",
        "has_content_warning",
        "has_alternative_deck_limit",
        "is_game_changer",
        "is_reserved",
        *LEADERSHIP.values(),
    )

    def construire(self):
        """Télécharge les fichiers manquants et régénère `cards.csv`.

        Si les fichiers `AllPrintings` et `AllPricesToday` sont déjà en cache et
        datent du même jour, ils sont conservés. Sinon, `AllPricesToday` est
        remplacé par la version du jour.
        """
        self.telecharger(self.PRINTINGS_URL, self.CACHE / self.ALL_PRINTINGS)
        date_prix = self.assurer_prix_du_jour(self.CACHE / self.ALL_PRICES_TODAY)
        prix = self.charger_prix(self.CACHE / self.ALL_PRICES_TODAY)

        with sqlite3.connect(self.CACHE / self.ALL_PRINTINGS) as base:
            cartes = self.charger_cartes(base)
            legalites = self.charger_legalites(base)
            rulings = self.charger_rulings(base)
            identifiants = self.charger_identifiants(base)

        n_impressions = len(cartes)
        cartes["release_date"] = pd.to_datetime(cartes["release_date"], errors="coerce")
        agregats = self.agreger_nom(cartes)

        representative = cartes.sort_values(
            ["name", "release_date", "set_code", "uuid"],
            ascending=[True, False, False, False],
            na_position="last",
        ).drop_duplicates("name", keep="first")
        representative = representative.drop(
            columns=[
                "leadership_skills",
                "edhrec_rank",
                "edhrec_saltiness",
                "is_game_changer",
                "is_reserved",
            ]
        )
        representative = (
            representative.merge(agregats, on="name", how="left")
            .merge(legalites, on="name", how="left")
            .merge(rulings, on="name", how="left")
            .merge(identifiants, on="uuid", how="left")
        )

        prix_par_nom = (
            cartes[["name", "uuid"]]
            .assign(retail_price=lambda table: table["uuid"].map(prix))
            .dropna(subset=["retail_price"])
            .groupby("name")["retail_price"]
            .mean()
        )

        representative["retail_price"] = representative["name"].map(prix_par_nom)
        representative["rarity_rank"] = (
            representative["rarity"].astype("string").str.lower().map(self.RARITY_RANK)
        )
        representative["release_date"] = self.date_iso(representative["release_date"])
        representative["first_release_date"] = self.date_iso(
            representative["first_release_date"]
        )
        representative["edhrec_rank"] = (
            pd.to_numeric(representative["edhrec_rank"], errors="coerce")
            .round()
            .astype("Int64")
        )
        representative["ruling_count"] = (
            representative["ruling_count"].fillna(0).astype(int)
        )
        representative["face_count"] = (
            representative["face_count"].fillna(1).astype(int)
        )
        representative["printing_count"] = (
            representative["printing_count"].fillna(0).astype(int)
        )
        for colonne in self.DRAPEAUX:
            representative[colonne] = self.comme_booleen(representative[colonne])

        colonnes = [
            "name",
            "scryfall_oracle_id",
            "uuid",
            "face_name",
            "side",
            "face_count",
            "mana_cost",
            "mana_value",
            "colors",
            "color_identity",
            "color_indicator",
            "produced_mana",
            "supertypes",
            "types",
            "subtypes",
            "type_line",
            "keywords",
            "text",
            "power",
            "toughness",
            "loyalty",
            "defense",
            "hand_modifier",
            "life_modifier",
            "set_code",
            "set_name",
            "set_type",
            "set_block",
            "collector_number",
            "release_date",
            "first_release_date",
            "original_release_date",
            "printing_count",
            "rarity",
            "rarity_rank",
            "layout",
            "language",
            "artist",
            "availability",
            "finishes",
            "border_color",
            "frame_version",
            "frame_effects",
            "promo_types",
            "security_stamp",
            "watermark",
            "retail_price",
            "edhrec_rank",
            "edhrec_saltiness",
            "ruling_count",
            *self.DRAPEAUX,
            *[f"legality_{fmt}" for fmt in self.FORMATS],
        ]
        exporte = representative[colonnes].sort_values("name")

        self.OUT.parent.mkdir(exist_ok=True)
        exporte.to_csv(self.OUT, index=False)
        self._ecrire_note(exporte, n_impressions, date_prix)
        print(f"CSV: {self.OUT.name} ({self.OUT.stat().st_size} octets)")
        return self.OUT

    def telecharger(self, url, destination, forcer=False):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not forcer and destination.exists() and destination.stat().st_size > 0:
            print(f"Deja telecharge : {destination.name}")
            return

        temporaire = destination.with_suffix(destination.suffix + ".part")
        print(f"Telechargement de {url}")
        requete = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; cards-csv-builder/1.0)"},
        )

        with (
            urllib.request.urlopen(requete) as reponse,
            open(temporaire, "wb") as sortie,
        ):
            total = int(reponse.headers.get("Content-Length") or 0)
            recu = 0
            dernier_affichage = 0
            while True:
                bloc = reponse.read(1024 * 1024)
                if not bloc:
                    break
                sortie.write(bloc)
                recu += len(bloc)
                if total and recu - dernier_affichage >= 50 * 1024 * 1024:
                    print(
                        f"  {recu / 1_000_000:.0f} / {total / 1_000_000:.0f} Mo",
                        flush=True,
                    )
                    dernier_affichage = recu

        temporaire.replace(destination)
        print(f"Enregistre : {destination.name}")

    def date_des_prix(self, chemin):
        """Retourne la date publiée par MTGJSON dans `meta.date`, ou `None` si le fichier est absent."""
        if not chemin.exists() or chemin.stat().st_size == 0:
            return None
        try:
            with gzip.open(chemin, "rt", encoding="utf-8") as fichier:
                entete = fichier.read(80)
        except (OSError, EOFError, gzip.BadGzipFile):
            return None
        trouve = re.match(r'\{"meta":\{"date":"(\d{4}-\d{2}-\d{2})"', entete)
        return trouve.group(1) if trouve else None

    def assurer_prix_du_jour(self, destination):
        """Conserve le cache lorsque les prix correspondent à ceux du jour et le remplace sinon."""
        aujourdhui = date.today().isoformat()
        date_cache = self.date_des_prix(destination)
        if date_cache == aujourdhui:
            print(f"Prix du jour deja en cache ({date_cache})")
            return date_cache

        if date_cache is None:
            print(f"Telechargement des prix du {aujourdhui}")
        else:
            print(f"Prix en cache du {date_cache}, mise a jour vers le {aujourdhui}")
        self.telecharger(self.PRICES_URL, destination, forcer=True)

        date_cache = self.date_des_prix(destination)
        if date_cache == aujourdhui:
            print(f"Prix du {date_cache} enregistres")
        else:
            print(f"MTGJSON publie encore les prix du {date_cache}")
        return date_cache

    def prix_retail_normal(self, fiche):
        """Calcule le prix moyen de vente au détail des cartes physiques, en finition normale et en dollars."""
        papier = fiche.get("paper") if isinstance(fiche, dict) else None
        if not isinstance(papier, dict):
            return None

        valeurs = []
        for fournisseur, formats in papier.items():
            if fournisseur not in self.FOURNISSEURS_USD or not isinstance(
                formats, dict
            ):
                continue
            if formats.get("currency") not in (None, "USD"):
                continue
            normal = (formats.get("retail") or {}).get("normal") or {}
            if not isinstance(normal, dict):
                continue
            for prix in normal.values():
                if isinstance(prix, (int, float)):
                    valeurs.append(float(prix))

        if not valeurs:
            return None
        return sum(valeurs) / len(valeurs)

    def charger_prix(self, chemin):
        print("Lecture des prix du jour...")
        with gzip.open(chemin, "rt", encoding="utf-8") as fichier:
            payload = json.load(fichier)

        prix = {}
        for uuid, fiche in payload["data"].items():
            valeur = self.prix_retail_normal(fiche)
            if valeur is not None:
                prix[uuid] = valeur
        print(f"Impressions avec un prix retail normal : {len(prix)}")
        return prix

    @staticmethod
    def comme_booleen(serie):
        return pd.to_numeric(serie, errors="coerce").fillna(0).astype(int).clip(0, 1)

    def extraire_leadership(self, brut):
        drapeaux = {colonne: 0 for colonne in self.LEADERSHIP.values()}
        if not isinstance(brut, str) or not brut.strip():
            return drapeaux
        try:
            data = json.loads(brut)
        except json.JSONDecodeError:
            return drapeaux
        for cle, colonne in self.LEADERSHIP.items():
            drapeaux[colonne] = int(bool(data.get(cle)))
        return drapeaux

    def charger_cartes(self, base):
        print("Lecture des impressions...")
        return pd.read_sql_query(
            """
            SELECT
                c.name,
                c.uuid,
                c.setCode AS set_code,
                s.name AS set_name,
                s.type AS set_type,
                s.block AS set_block,
                s.releaseDate AS release_date,
                c.number AS collector_number,
                c.language,
                c.availability,
                c.borderColor AS border_color,
                c.finishes,
                c.frameVersion AS frame_version,
                c.frameEffects AS frame_effects,
                c.promoTypes AS promo_types,
                c.securityStamp AS security_stamp,
                c.watermark,
                c.artist,
                c.layout,
                c.side,
                c.faceName AS face_name,
                c.manaCost AS mana_cost,
                c.manaValue AS mana_value,
                c.colors,
                c.colorIdentity AS color_identity,
                c.colorIndicator AS color_indicator,
                c.producedMana AS produced_mana,
                c.supertypes,
                c.types,
                c.subtypes,
                c.type AS type_line,
                c.keywords,
                c.text,
                c.power,
                c.toughness,
                c.loyalty,
                c.defense,
                c.hand AS hand_modifier,
                c.life AS life_modifier,
                c.rarity,
                c.edhrecRank AS edhrec_rank,
                c.edhrecSaltiness AS edhrec_saltiness,
                c.isGameChanger AS is_game_changer,
                c.isReserved AS is_reserved,
                c.isReprint AS is_reprint,
                c.isPromo AS is_promo,
                c.isFunny AS is_funny,
                c.isTextless AS is_textless,
                c.isFullArt AS is_full_art,
                c.isOversized AS is_oversized,
                c.isOnlineOnly AS is_online_only,
                c.isAlternative AS is_alternative,
                c.isRebalanced AS is_rebalanced,
                c.isTimeshifted AS is_timeshifted,
                c.isStorySpotlight AS is_story_spotlight,
                c.hasContentWarning AS has_content_warning,
                c.hasAlternativeDeckLimit AS has_alternative_deck_limit,
                c.leadershipSkills AS leadership_skills,
                c.originalReleaseDate AS original_release_date
            FROM cards c
            LEFT JOIN sets s ON s.code = c.setCode
            WHERE c.name IS NOT NULL
            """,
            base,
        )

    def charger_legalites(self, base):
        colonnes = ", ".join(
            f"MAX(NULLIF(l.{fmt}, '')) AS legality_{fmt}" for fmt in self.FORMATS
        )
        return pd.read_sql_query(
            f"""
            SELECT c.name, {colonnes}
            FROM cards c
            LEFT JOIN cardLegalities l ON l.uuid = c.uuid
            WHERE c.name IS NOT NULL
            GROUP BY c.name
            """,
            base,
        )

    def charger_rulings(self, base):
        return pd.read_sql_query(
            """
            SELECT c.name, COUNT(r.text) AS ruling_count
            FROM cards c
            LEFT JOIN cardRulings r ON r.uuid = c.uuid
            WHERE c.name IS NOT NULL
            GROUP BY c.name
            """,
            base,
        )

    @staticmethod
    def charger_identifiants(base):
        return pd.read_sql_query(
            """
            SELECT uuid, scryfallOracleId AS scryfall_oracle_id
            FROM cardIdentifiers
            """,
            base,
        )

    def agreger_nom(self, cartes):
        """Faits qui décrivent le nom, plutôt qu'une impression isolée."""
        agregats = cartes.groupby("name", as_index=False).agg(
            printing_count=("uuid", "count"),
            face_count=(
                "side",
                lambda valeurs: max(int(valeurs.nunique(dropna=True)), 1),
            ),
            first_release_date=("release_date", "min"),
            edhrec_rank=("edhrec_rank", "min"),
            edhrec_saltiness=("edhrec_saltiness", "max"),
            is_game_changer=("is_game_changer", "max"),
            is_reserved=("is_reserved", "max"),
        )

        leadership = pd.DataFrame(
            cartes["leadership_skills"].map(self.extraire_leadership).tolist()
        )
        leadership.insert(0, "name", cartes["name"].to_numpy())
        leadership = leadership.groupby("name", as_index=False).max()
        return agregats.merge(leadership, on="name", how="left")

    @staticmethod
    def date_iso(serie):
        dates = pd.to_datetime(serie, errors="coerce")
        return dates.dt.strftime("%Y-%m-%d")

    def _ecrire_note(self, exporte, n_impressions, date_prix):
        creatures = (
            exporte["types"]
            .fillna("")
            .map(
                lambda valeur: (
                    "Creature"
                    in [morceau.strip() for morceau in str(valeur).split(",")]
                )
            )
        )
        note = "\n".join(
            [
                "Construction de cards.csv",
                f"Date : {datetime.now().isoformat(timespec='seconds')}",
                f"Cartes : {self.PRINTINGS_URL}",
                f"Prix : {self.PRICES_URL}",
                f"Date des prix : {date_prix}",
                "",
                "Une ligne correspond à un nom de carte. La plupart des colonnes",
                "proviennent de l'impression la plus récente, choisie selon la date de sortie,",
                "puis le code d'édition et enfin l'UUID. Une carte à deux faces",
                "compte pour deux lignes dans printing_count. face_count indique le nombre",
                "de faces, tandis que face_name et side correspondent à la face conservée.",
                "",
                "Certaines colonnes sont agrégées sur l'ensemble des impressions du nom.",
                "legality_* vaut Legal, Banned ou Restricted ; les valeurs vides des impressions",
                "promotionnelles sont ignorées. can_commander, can_brawl, can_oathbreaker,",
                "can_pauper_commander et can_predh valent 1 si une face ou une impression",
                "autorise le format correspondant. is_game_changer et is_reserved valent 1",
                "si au moins une impression possède la propriété correspondante.",
                "Les variables edhrec_rank (plus petit lorsque la carte est plus jouée),",
                "edhrec_saltiness, first_release_date, ruling_count, printing_count et",
                "face_count sont également regroupées sur le nom de carte.",
                "",
                "retail_price correspond à la moyenne, en dollars, du prix de vente au détail",
                "des cartes physiques en finition normale chez TCGPlayer, Card Kingdom",
                "et Mana Pool. Cette moyenne est ensuite calculée entre les impressions",
                "de la carte disposant d'un prix. rarity_rank code common 1, uncommon 2,",
                "rare 3, mythic 4, special 5 et bonus 6.",
                "Les autres indicateurs, comme is_promo ou is_funny, décrivent l'édition",
                "conservée.",
                "",
                f"Colonnes : {len(exporte.columns)}",
                f"Impressions lues : {n_impressions}",
                f"Noms de cartes : {len(exporte)}",
                f"Dont le type contient Creature : {int(creatures.sum())}",
                f"Sans prix retail normal : {int(exporte['retail_price'].isna().sum())}",
                f"Game changers : {int(exporte['is_game_changer'].sum())}",
                f"Peuvent être commandants : {int(exporte['can_commander'].sum())}",
            ]
        )
        self.NOTE.write_text(note + "\n", encoding="utf-8")
        print(note)


if __name__ == "__main__":
    ConstructeurCartes().construire()

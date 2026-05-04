import csv


EMOJI_BY_KEYWORD = {
    "süt": "🥛",
    "ekmek": "🍞",
    "yumurta": "🥚",
    "peynir": "🧀",
    "yoğurt": "🥣",
    "krema": "🍶",
    "zeytin": "🫒",
    "salatalık": "🥒",
    "domates": "🍅",
    "patates": "🥔",
    "soğan": "🧅",
    "elma": "🍎",
    "muz": "🍌",
    "limon": "🍋",
    "yeşillik": "🥬",
    "tavuk": "🍗",
    "kıyma": "🥩",
    "sucuk": "🌭",
    "salam": "🥓",
    "makarna": "🍝",
    "pirinç": "🍚",
    "mercimek": "🫘",
    "nohut": "🫛",
    "şeker": "🍬",
    "un": "🌾",
    "yağ": "🫒",
    "tereyağı": "🧈",
    "çikolata": "🍫",
    "cips": "🍟",
    "bisküvi": "🍪",
    "çay": "🫖",
    "kahve": "☕",
    "maden suyu": "🧴",
    "meyve suyu": "🧃",
    "deterjan": "🧽",
    "tuvalet kağıdı": "🧻",
    "kağıt havlu": "🧻",
    "sabun": "🧼",
    "şampuan": "🧴",
    "diş macunu": "🪥",
}


def _get_emoji_for_item(item_name):
    lowered_name = item_name.casefold()

    for keyword, emoji in sorted(EMOJI_BY_KEYWORD.items(), key=lambda item: len(item[0]), reverse=True):
        if keyword in lowered_name:
            return emoji

    return "🛒"


def load_items(file_path):
    products = []

    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            raw_importance = row.get("importance", "").strip()
            importance = int(raw_importance) if raw_importance else 5
            item_name = row["name"].strip()
            emoji = _get_emoji_for_item(item_name)

            products.append({
                "name": f"{emoji} {item_name}",
                "price": int(float(row["price"])),
                "importance": importance
            })

    return products
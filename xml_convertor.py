import xmltodict, json

music_db = {}

# i have no idea what's going on with the encodings here...
# copied from link: https://github.com/22vv0/asphyxia_plugins/issues/14
# thank you @norikawa!

def fix_bad_utf8(title: str) -> str:
    replacements = {
        "齷": "é",
        "鬮": "¡",
        "齶": "♡", 
        "ケロH": "ケロ⑨",
        "曦": "à",
        "曩": "è",
        "龕": "€",
        "壬": "ê",
        "驩": "Ø",
        "=墸Σ≡=｡ﾟ:*.:+｡.☆": "=͟͟͞ Σ≡=｡ﾟ:*.:+｡.☆",
        "鹹": "Ĥ",
        "闃": "Ā",
        "饌": "²",
        "煢": "ø",
        "餮": "Ƶ",
        "蔕": "ῦ",
        "盥": "⚙︎",
        "頽": "ä",
        "隍": "Ü",
        "雋": "Ǜ",
        "鬻": "♃",
        "鬥": "Ã",
        "鬆": "Ý",
        "趁": "Ǣ",
        "驫": "ā",
        "騫": "á",
        "齲": "♥",
        "骭": "ü"
    }
    for (mojibake, correction) in replacements.items():
        title = title.replace(mojibake, correction)
    return title

with open("data/raw_music_db.xml" ,'r', encoding="utf_8_sig") as file:
    music_db = xmltodict.parse(file.read())

with open("data/canonical_music_db.json", 'w', encoding="utf_8_sig") as file:
    json.dump(music_db, file, indent=4, ensure_ascii=False)

for song in music_db["mdb"]["music"]:
    title = song["info"]["title_name"]
    title = fix_bad_utf8(title)
    song["info"]["title_name"] = title

with open("data/canonical_fixed_music_db.json", 'w', encoding="utf_8_sig") as file:
    json.dump(music_db, file, indent=4, ensure_ascii=False)
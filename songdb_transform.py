import json
import xmltodict

music_db = {}

# i have no idea what's going on with the encodings here...
# from link: https://github.com/22vv0/asphyxia_plugins/issues/14
# and merged with 22vv0's translation table: https://github.com/22vv0/asphyxia_plugins/blob/kfc/webui/asset/js/songslist.js#L48
# thank you @norikawa and @22vv0!

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
        "蔕": "ũ",
        "盥": "⚙︎",
        "頽": "ä",
        "隍": "︎Ü",
        "雋": "Ǜ",
        "鬻": "♃",
        "鬥": "Ã",
        "鬆": "Ý",
        "趁": "Ǣ",
        "驫": "ā",
        "騫": "á",
        "齲": "♥",
        "骭": "ü",
        "釁": "🍄",
        "彜": "ū",
        "罇": "ê",
        "黻": "*",
        "　H": "　⑨"
    }
    for (mojibake, correction) in replacements.items():
        if mojibake in title:
            print(f"Replacing {mojibake} -> {correction} in {title}")
        title = title.replace(mojibake, correction)
    return title

with open("data/raw_music_db.xml" ,'r', encoding="shift_jis", errors='ignore') as file:
    music_db = xmltodict.parse(file.read())
    print("Opened raw music DB")

with open("data/canonical_music_db.json", 'w', encoding="utf_8_sig") as file:
    json.dump(music_db, file, indent=4, ensure_ascii=False)
    print("Wrote JSON music DB")

for song in music_db["mdb"]["music"]:
    title = song["info"]["title_name"]
    title = fix_bad_utf8(title)
    song["info"]["title_name"] = title

with open("data/canonical_fixed_music_db.json", 'w', encoding="utf_8_sig") as file:
    json.dump(music_db, file, indent=4, ensure_ascii=False)
    print("Wrote fixed JSON music DB")

# quite a few songs are inconsistently stored - this adds some aliases
# mostly just to silence nuisance mismatches
# eg. both "Alice Maestera" and "Alice Maestera feat. nomico" are keyed to the same mID
# Key is the alias, value is the canonical name
# move this to a file eventually, it's getting rather long...
MANUAL_ALIASES = {
    "ARROW RAIN": "ARROW RAIN feat. ayame",
    "Alice Maestera": "Alice Maestera feat. nomico",
    "トーホータノシ feat. 抹": "トーホータノシ (feat. 抹)",
    "SACRIFICE feat.ayame": "SACRIFICE feat. ayame",
    "Dreaming feat.nomico": "Dreaming feat. nomico",
    "グレイスちゃんの超～絶!!グラビティ講座w ": "グレイスちゃんの超〜絶!!グラビティ講座w", #the tilde faces the other way LOL
    "Help me， ERINNNNNN!!": "Help me, ERINNNNNN!!",
    "Help me， ERINNNNNN!! -VENUS mix-": "Help me, ERINNNNNN!! -VENUS mix-",
    "Help me， ERINNNNNN!! - SH Style -": "Help me, ERINNNNNN!! - SH Style -",
    "Help me， ERINNNNNN!! -Cranky remix-": "Help me, ERINNNNNN!! -Cranky remix-",
    "Help me， ERINNNNNN!! #幻想郷ホロイズムver.": "Help me, ERINNNNNN!! #幻想郷ホロイズムver.",
     "おにいちゃんグリッチホップ ～eternal love remix～": "おにいちゃんグリッチホップ 〜eternal love remix〜", #these tildes my least favourite thing ever
     "おにいちゃんグリッチホップ ~eternal love remix~": "おにいちゃんグリッチホップ 〜eternal love remix〜"
}

mid_to_title = {}
title_to_mid = {}

for song in music_db["mdb"]["music"]:
    title = song["info"]["title_name"]
    id = song["@id"]
    mid_to_title[id] = title
    title_to_mid[title] = id

# copy the canonical (value) titles' mIDs to the aliases
# no need to do the opposite - mID should only key to the canonical title
for key, value in MANUAL_ALIASES.items():
    if value not in title_to_mid:
        print(f"Alias `{value}` for `{key}` was not in title_to_mid!")
        continue
    title_to_mid[key] = title_to_mid[value]

with open("data/mid_to_title.json", 'w', encoding="utf_8_sig") as file:
    json.dump(mid_to_title, file, indent=2, ensure_ascii=False)
    print("Wrote mid_to_title")
with open("data/title_to_mid.json", 'w', encoding="utf_8_sig") as file:
    json.dump(title_to_mid, file, indent=2, ensure_ascii=False)
    print("Wrote title_to_mid")
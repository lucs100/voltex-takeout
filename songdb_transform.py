import json

data = {}

# quite a few songs are inconsistently stored - this adds some aliases
# mostly just to silence nuisance mismatches
# eg. both "Alice Maestera" and "Alice Maestera feat. nomico" are keyed to the same mID
# move this to a file eventually, it's getting rather long...
MANUAL_ALIASES = {
    "ARROW RAIN": "ARROW RAIN feat. ayame",
    "Alice Maestera": "Alice Maestera feat. nomico",
    "トーホータノシ feat. 抹": "トーホータノシ (feat. 抹)",
    "SACRIFICE feat.ayame": "SACRIFICE feat. ayame",
    "Dreaming feat.nomico": "Dreaming feat. nomico",
    "グレイスちゃんの超～絶!!グラビティ講座w ": "グレイスちゃんの超～絶!!グラビティ講座w",
    "Help me， ERINNNNNN!!": "Help me, ERINNNNNN!!",
    "Help me， ERINNNNNN!! -VENUS mix-": "Help me, ERINNNNNN!! -VENUS mix-",
    "Help me， ERINNNNNN!! - SH Style -": "Help me, ERINNNNNN!! - SH Style -",
    "Help me， ERINNNNNN!! -Cranky remix-": "Help me, ERINNNNNN!! -Cranky remix-",
    "Help me， ERINNNNNN!! #幻想郷ホロイズムver.": "Help me, ERINNNNNN!! #幻想郷ホロイズムver."
}



with open("data/canonical_fixed_music_db.json", 'r', encoding="utf_8_sig") as file:
    data = json.load(file)

mid_to_title = {}
title_to_mid = {}

for song in data["mdb"]["music"]:
    title = song["info"]["title_name"]
    id = song["@id"]
    mid_to_title[id] = title
    title_to_mid[title] = id

# copy the canonical (value) titles' mIDs to the aliases
# no need to do the opposite - mID should only key to the canonical title
for key, value in MANUAL_ALIASES.items():
    title_to_mid[key] = title_to_mid[value]

with open("data/mid_to_title.json", 'w', encoding="utf_8_sig") as file:
    json.dump(mid_to_title, file, indent=2, ensure_ascii=False)
with open("data/title_to_mid.json", 'w', encoding="utf_8_sig") as file:
    json.dump(title_to_mid, file, indent=2, ensure_ascii=False)
import json

data = {}

with open("data/canonical_music_db.json", 'r', encoding="utf_8_sig") as file:
    data = json.load(file)

mid_to_title = {}
title_to_mid = {}

for song in data["mdb"]["music"]:
    title = song["info"]["title_name"]
    id = song["@id"]
    mid_to_title[id] = title
    title_to_mid[title] = id

with open("data/mid_to_title.json", 'w', encoding="utf_8_sig") as file:
    json.dump(mid_to_title, file, indent=2, ensure_ascii=False)
with open("data/title_to_mid.json", 'w', encoding="utf_8_sig") as file:
    json.dump(title_to_mid, file, indent=2, ensure_ascii=False)
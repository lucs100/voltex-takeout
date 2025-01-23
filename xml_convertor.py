import xmltodict, json

music_db = {}

# i have no idea what's going on with the encodings here...
# manually patched anything i could spot that didn't encode right
# usually just symbols like ♥ , emojis, latin accents, etc that shift-jis can't handle
# definitely missed a few though
with open("data/edited_music_db.xml" ,'r', encoding="utf_8_sig") as file:
    music_db = xmltodict.parse(file.read())

with open("data/canonical_fixed_music_db.json", 'w', encoding="utf_8_sig") as file:
    json.dump(music_db, file, indent=4, ensure_ascii=False)
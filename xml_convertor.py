import xmltodict, json

music_db = {}

with open("data/music_db.xml" ,'r', encoding="cp932") as file:
    music_db = xmltodict.parse(file.read())

with open("data/canonical_music_db.json", 'w', encoding="utf_8_sig") as file:
    json.dump(music_db, file, indent=4, ensure_ascii=False)
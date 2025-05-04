from string import ascii_letters, digits
from random import choices
import json
import shutil
from pathlib import Path
from datetime import datetime

ID_CHARS = ascii_letters + digits
def newID():
    return "".join(choices(ID_CHARS, k=16))

class SaveData:
    def __init__(self, fp: str|Path) -> bool:
        """
        Loads an Asphyxia CORE SDVX database to a SaveData object.
        
        Args:
            fp: The filepath of the database. Generally is .../SOUND VOLTEX EXCEED GEAR/contents/savedata/sdvx@asphyxia.db.
        """
        self.fp: Path = Path(fp) #safe for both strings and paths
        self.keys: list[dict] = []
        with open(self.fp, 'r') as file:
            for line in file:
                try:
                    self.keys.append(json.loads(line))
                except:
                    raise json.JSONDecodeError("Failed to decode line: " + line)

    def getProfiles(self) -> dict[str: str]:
        """
        Returns a dict of all profiles in a DB.
        Keys are __refid (internal ID), values are profile names.
        """
        return {x["__refid"]: x["name"] for x in self.keys if x.get("collection") == "profile"}

GRADE = {
    "D": 1,
    "C": 2,
    "B": 3,
    "A": 4,
    "A+": 5,
    "AA": 6,
    "AA+": 7,
    "AAA": 8,
    "AAA+": 9,
    "S": 10
}

CLEAR_LAMP = {
    "PLAYED": 1,
    "COMPLETE": 2,
    "EXCESSIVE": 3, #NOTE: note sure if this is correct.
    "ULTIMATE CHAIN": 4,
    "PERFECT ULTIMATE CHAIN": 5 #NOTE: note sure if this is correct.
}

DIFFICULTY = {
    "NOVICE": 0,
    "ADVANCED": 1,
    "EXHAUST": 2,
    "MAXIMUM": 3, #NOTE: all "apex" difficulties are 3
    "INFINITE": 3,
    "GRAVITY": 3,
    "HEAVENLY": 3,
    "VIVID": 3,
    "EXCEED": 3
}

def writeKeys(source_fp: str|Path, keys: list[dict], backup_fp: str|Path|None = None) -> None:
    """
    Writes a list of keys to an Asphyxia CORE SDVX database.
    Note this function simply appends a list of keys to a file.
    A backup will ALWAYS be created.

    Args:
        source_fp: Where to load the DB from.
        keys: The list of play data keys to append.
        backup_fp: Where to copy the DB file to before modifying it. Defaults to a timestamped sibling file.
    """
    # Backup the file
    if backup_fp is None:
        backup_fp: Path = Path(source_fp).parent / f"voltex_takeout_backup_{int(datetime.now().timestamp())}.db"
    else:
        backup_fp = Path(backup_fp)
    assert not backup_fp.exists(), "Backup already exists!"
    shutil.copy(source_fp, backup_fp)
    assert backup_fp.exists(), "Failed to copy a backup!"

    # Convert the keys into strings, in the format Asphyxia wants
    entries = []
    for key in keys:
        entry = str(key)
        entry = entry.replace(" ", "") #remove spaces
        entry = entry.replace("'", '"') #use double quotes instead of single
        entries.append(entry)
        # print(f"Added record: {row['title']} [{row['難易度']}] - {key['score']} ({row['スコアグレード']})")
    
    with open(source_fp, 'a') as file:
        file.write("\n") #MUST add a newline after the last key in the file!! otherwise, the first key will be corrupt
        file.write("\n".join(entries))

def getSaveDataFile(fp: Path, dbName: str = "sdvx@asphyxia.db") -> Path:
    saveDataPath = fp / dbName
    assert saveDataPath.exists(), f"{dbName} was not found in {fp}."
    return saveDataPath

# Song schema: 
# {
#   "collection": "music", #always "music"
#   "mid": 1070, #the mID (music ID) - see mid_to_title and title_to_mid
#   "type": 2, #the difficulty - NOV = 0, ADV = 1, EXH = 2, MXM/etc. = 3
#   "score": 6324186, #score
#   "exscore": 0, #EX score; 0 if EX score disabled
#   "clear": 1, #None (not played) = 0, Played (fail) = 1, Clear = 2, Excessive Clear* = 3, UC = 4, PUC = 5     *Excessive+ARS does not change this; if finished with Excessive then clear is 3, if demoted to Permissive then clear is 2, if failed clear is always 1 
#   "grade": 1, #D=1, C=2, B=3, A=4, A+=5, AA=6, AA+=7, AAA=8, AAA+=9, S=10
#   "buttonRate": 9, #??? seems to be the "performance" %, rounded and out of 10
#   "longRate": 9, #""
#   "volRate": 1, #""
#   "__s": "plugins_profile", #always "plugins_profile"
#   "__refid": "A59A6D749B842E3B", #The profile ID, not sure where this comes from but it's constant
#   "_id": "KBfNQaMl42soxhtH", #Random ID - 16 alphanumeric characters
#   "createdAt": {
#     "$$date": 1745775105070 #First play of the song
#   },
#   "updatedAt": {
#     "$$date": 1745775105070 #Time of record insert
#   }
# }
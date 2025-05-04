from string import ascii_letters, digits
from random import choices
import json, csv
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

CONFIDENT_MODE = 0

MIDS = {}
with open("data/title_to_mid.json", 'r', encoding="utf_8_sig") as file:
    MIDS = json.load(file)

all_titles = MIDS.keys() # for fuzzy search

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
            for idx, line in enumerate(file):
                try:
                    line = line.strip()
                    print(f"Line #{idx}: {str(line)}")
                    if line is None or line == "":
                        print("Line is None!!")
                        continue
                    self.keys.append(json.loads(line.strip()))
                except:
                    raise json.JSONDecodeError("Failed to decode line: " + line)

    def getProfiles(self) -> dict[str: str]:
        """
        Returns a dict of all profiles in a DB.
        Keys are __refid (internal ID), values are profile names.
        """
        return {x["__refid"]: x["name"] for x in self.keys if x.get("collection") == "profile"}

    def getPlayData(self) -> list[dict]:
        """
        Returns a list of all plays in a DB.
        """
        return [x for x in self.keys if x.get("collection") == "music"]

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

def getSaveDataPath(fp: str|Path, dbName: str = "sdvx@asphyxia.db") -> Path|None:
    """
    Checks if a savedata file exists in the given path.

    Args:
        fp: The folder to check in.
        dbName: The name of the file to check for.
    
    Returns:
        saveDataPath: The path to the file if found, otherwise None. 
    """
    saveDataPath = Path(fp) / dbName
    if saveDataPath.exists():
        return saveDataPath
    else: 
        return None

def getSongID(title) -> int:
    """
    Returns the mID of the passed title, or -1 if no match is found.
    If CONFIDENT_MODE is True, attempts to fuzzy match.
    """
    if title in MIDS.keys(): #exact match
        return int(MIDS[title])  
    if CONFIDENT_MODE:
        try:
            (match, score) = process.extractOne(title, all_titles, 
                                scorer=fuzz.token_set_ratio, score_cutoff=80)
            return MIDS[match]
        except TypeError: #no sufficient match
            return -1

def append_mIDs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a column to a SDVX data file (.csv) with the mID of each song.
    """
    dfTitles = df.iloc[:, 0]
    matching_mIDs = dfTitles.map(getSongID)
    df.insert(1, "mID", matching_mIDs)
    df.sort_values("mID", inplace=True)
    return df

def _getUnknownSongs(df: pd.DataFrame) -> list[str]:
    """
    Used for debugging.
    Gets all songs in a DataFrame which were not successfully matched to an mID.
    """
    songIsUnknown = df["mID"] == -1
    return [x[0] for x in df.loc[songIsUnknown, ['title']].values]

def _saveDF(df: pd.DataFrame, target: str|Path) -> None:
    """
    Used for debugging.
    Saves a DataFrame to an e-amuse SDVX data file (.csv). 
    """
    target = Path(target)
    df.to_csv(target, index=False)
    # quotes in some songs seem to be messing with csv output (for the csv-lint extension)
    # df.to_csv(target, index=False, quotechar="`")

def loadScores(source: str|Path) -> pd.DataFrame:
    """
    Loads an e-amuse SDVX data file (.csv) into a DataFrame.
    """
    source = Path(source)
    return pd.read_csv(source, encoding="utf_8_sig")

def generateKeysFromDF(df: pd.DataFrame, user_id: str) -> list[dict]:
    """
    Returns a list of Asphyxia CORE database keys based on play data from a DataFrame.

    Args:
        df: The DataFrame of play data.
        user_id: The Asphyxia CORE user ID (_refID) to associate each play key with. 
    """
    data = []

    for idx, row in df.iterrows():
        if row["mID"] is None:
            print(f"Warning: Couldn't find music ID for {row['title']}. Skipping.")
            continue
        insertTime = int(datetime.now().timestamp())
        key = {
            "collection": "music",
            "mid": int(row["mID"]), #Music ID
            "type": DIFFICULTY[row["難易度"]],
            "score": row["ハイスコア"], #High Score
            "exscore": row["EXスコア"], #EX Score
            "clear": CLEAR_LAMP[row["クリアランク"]], #Clear Rank 
            "grade": GRADE[row["スコアグレード"]], #Score Grade
            "buttonRate": 10, #just a 'score' for each hit type out of 10 - not actually used
            "longRate": 10,
            "volRate": 10,
            "__s": "plugins_profile",
            "__refid": user_id,
            "_id": newID(),
            "createdAt": {
                "$$date": insertTime #First play of the song 
                # TODO: investigate: does this do anything? will keys fail to load if times are changed?
                # ie. is this just used by the db schema, or does asphyxia actually look at it to determine when a song was
                # first played, when its best was updated, etc?
            },
            "updatedAt": {
                "$$date": insertTime #Time of record insert
            }
        }
        # print(f"Added record: {row['title']} [{row['難易度']}] - {key['score']} ({row['スコアグレード']})")
        data.append(key)
    
    return data

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

# Old songDB testing code from csv_translator.py:

## visual diagnostics
# mostly outdated, still works

# with open(fp, newline='', encoding="utf_8_sig") as csvfile:
#     sdvxreader = csv.DictReader(csvfile) #TODO: convert to pandas then refactor all this, should make mass-translation and csv copying easier
#     for row in sdvxreader:
#         title = row['title']
#         try: 
#             mid = mids[row['title']]
#         except KeyError:
#             fails.append(title)
#             try: 
#                 (match, score) = process.extractOne(title, all_titles, scorer=fuzz.token_set_ratio, score_cutoff=80)
#             except TypeError as e: #no result
#                 true_fails.append(title)
#                 missed_results = process.extract(title, all_titles, scorer=fuzz.token_set_ratio)
#                 miss_results.append( (title, missed_results) )
#             else: #this is a mess
#                 # print(title, mids[match])
#                 match_results.append( (title, match, score) )
#                 fuzzypasscnt += 1
#             finally:
#                 match = None
#                 score = None
#         else:
#             # print(title, mid)
#             passcnt += 1

# # --- diagnostics ---

# print("\n\n\n")
# print(f"--- FUZZY MATCH TABLE: ---")
# for (title, match, score) in sorted(match_results, key=lambda x: len(x[0])):
#     print(f"[{score}] \t {title}: \t {match}")
# print("\n\n\n")

# print(f"--- MISSED MATCH TABLE: ---")
# for (title, match) in sorted(miss_results, key=lambda x: len(x[0])):
#     print(f"{title}: \t {match}")
# print("\n")

# # print("\n\n\n")
# print(f"--- PASSED: {passcnt} + {fuzzypasscnt} ---")
# # print("\n\n")
# print(f"--- FAILED: {len(fails)} ---")
# # print(fails)
# # print("\n\n")
# print(f"--- TRULY FAILED: {len(true_fails)} ---")
# # print(true_fails)

# #sidenote: https://discord.com/channels/667043164434989061/667066735253520401/1239409904796565594
# # "currently almost all EG songs are set to hidden in music db" what is an eg song? i think this is why it doesn't appear - i followed up

# #sidenote - directly adding to the savegame file seems to be rejecting
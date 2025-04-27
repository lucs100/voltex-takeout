import csv, json
import pandas as pd
import asphyxia_db as db
from datetime import datetime
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

CONFIDENT_MODE = 0

FP_IN = "personal_data/my_sdvx_scores.csv"
FP_OUT = "edited_personal_data/my_sdvx_scores.csv"

MIDS = {}
with open("data/title_to_mid.json", 'r', encoding="utf_8_sig") as file:
    MIDS = json.load(file)

all_titles = MIDS.keys() # for fuzzy search

def getTitle(title) -> int:
    """
    Returns the mID of the passed title, or -1 if no match is found.
    If CONFIDENT_MODE is True, attempts to fuzzy match.
    """
    if title in MIDS.keys(): #exact match
        return MIDS[title]  
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
    matching_mIDs = dfTitles.map(getTitle)
    df.insert(1, "mID", matching_mIDs)
    return df

def getUnknownSongs(df: pd.DataFrame) -> list[str]:
    songIsUnknown = df["mID"] == -1
    return [x[0] for x in df.loc[songIsUnknown, ['title']].values]

def loadScores(source=FP_IN) -> pd.DataFrame:
    """
    Loads a SDVX data file (.csv) into a DataFrame.
    """
    return pd.read_csv(source, encoding="utf_8_sig")

def saveDF(df: pd.DataFrame, target=FP_OUT) -> None:
    """
    Saves a DataFrame to a SDVX data file (.csv). 
    df.to_csv(FP_OUT, index=False, quotechar="`")
    """
    df.to_csv(target, index=False)

if __name__ == "__main__":
    USER_ID = "ABCDEF0123456789"

    df = loadScores()
    df = append_mIDs(df)
    saveDF(df)

    data = []
    for idx, row in df.iterrows():
        if row["mID"] is None:
            print(f"Warning: Couldn't find music ID for {row['title']}. Skipping.")
            continue
        insertTime = int(datetime.now().timestamp())
        key = {
            "collection": "music",
            "mid": row["mID"], #Music ID
            "type": db.DIFFICULTY[row["難易度"]],
            "score": row["ハイスコア"], #High Score
            "exscore": row["EXスコア"], #EX Score
            "clear": db.CLEAR_LAMP[row["クリアランク"]], #Clear Rank 
            "grade": db.GRADE[row["スコアグレード"]], #Score Grade
            "buttonRate": 10, #idk, there is no documentation on this
            "longRate": 10, #idk
            "volRate": 10, #idk
            "__s": "plugins_profile",
            "__refid": USER_ID,
            "_id": db.newID(),
            "createdAt": {
                "$$date": insertTime #First play of the song
            },
            "updatedAt": {
                "$$date": insertTime #Time of record insert
            }
        }
        data.append(key)
        # print(f"Added record: {row['title']} [{row['難易度']}] - {key['score']} ({row['スコアグレード']})")
    
    with open("edited_personal_data/db_dump.db", "w") as file:
        file.write("\n".join([str(line) for line in data]))

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
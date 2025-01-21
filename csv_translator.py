import csv, json
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

mids = {}

fp = "my_sdvx_scores.csv"

with open("title_to_mid.json", 'r', encoding="utf_8_sig") as file:
    mids = json.load(file)

all_titles = mids.keys() # for fuzzy search

passcnt = 0
fuzzypasscnt = 0
fails = []
true_fails = []

with open(fp, newline='', encoding="utf_8_sig") as csvfile:
    sdvxreader = csv.DictReader(csvfile) 
    for row in sdvxreader:
        title = row['title']
        try: 
            mid = mids[row['title']]
        except KeyError:
            fails.append(title)
            mid = process.extractOne(title, all_titles, scorer=fuzz.token_set_ratio, score_cutoff=80)
            if mid is None:
                true_fails.append(title)
            else: #this is a mess
                print(title, mid)
                fuzzypasscnt += 1
        else:
            print(title, mid)
            passcnt += 1

print("\n\n\n")
print(f"--- PASSED: {passcnt} + {fuzzypasscnt} ---")
print("\n\n")
print(f"--- FAILED: {len(fails)} ---")
print(fails)
print("\n\n")
print(f"--- TRULY FAILED: {len(true_fails)} ---")
print(true_fails)

#sidenote: https://discord.com/channels/667043164434989061/667066735253520401/1239409904796565594
# "currently almost all EG songs are set to hidden in music db" what is an eg song? i think this is why it doesn't appear - i followed up

#sidenote - directly adding to the savegame file seems to be rejecting
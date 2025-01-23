import csv, json
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

mids = {}

fp = "personal_data/example_data.csv"

with open("data/title_to_mid.json", 'r', encoding="utf_8_sig") as file:
    mids = json.load(file)

all_titles = mids.keys() # for fuzzy search

passcnt = 0
fuzzypasscnt = 0
fails = []
true_fails = []
match_results = []
miss_results = []

with open(fp, newline='', encoding="utf_8_sig") as csvfile:
    sdvxreader = csv.DictReader(csvfile) #TODO: convert to pandas then refactor all this, should make mass-translation and csv copying easier
    for row in sdvxreader:
        title = row['title']
        try: 
            mid = mids[row['title']]
        except KeyError:
            fails.append(title)
            try: 
                (match, score) = process.extractOne(title, all_titles, scorer=fuzz.token_set_ratio, score_cutoff=80)
            except TypeError as e: #no result
                true_fails.append(title)
                missed_results = process.extract(title, all_titles, scorer=fuzz.token_set_ratio)
                miss_results.append( (title, missed_results) )
            else: #this is a mess
                # print(title, mids[match])
                match_results.append( (title, match, score) )
                fuzzypasscnt += 1
            finally:
                match = None
                score = None
        else:
            # print(title, mid)
            passcnt += 1

# --- diagnostics ---

print("\n\n\n")
print(f"--- FUZZY MATCH TABLE: ---")
for (title, match, score) in sorted(match_results, key=lambda x: len(x[0])):
    print(f"[{score}] \t {title}: \t {match}")
    print("\n")
print("\n\n\n")

print(f"--- MISSED MATCH TABLE: ---")
for (title, match) in sorted(miss_results, key=lambda x: len(x[0])):
    print(f"{title}: \t {match}")
    print("\n")

# print("\n\n\n")
print(f"--- PASSED: {passcnt} + {fuzzypasscnt} ---")
# print("\n\n")
print(f"--- FAILED: {len(fails)} ---")
# print(fails)
# print("\n\n")
print(f"--- TRULY FAILED: {len(true_fails)} ---")
# print(true_fails)

#sidenote: https://discord.com/channels/667043164434989061/667066735253520401/1239409904796565594
# "currently almost all EG songs are set to hidden in music db" what is an eg song? i think this is why it doesn't appear - i followed up

#sidenote - directly adding to the savegame file seems to be rejecting
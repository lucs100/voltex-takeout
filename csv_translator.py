import csv, json

mids = {}

fp = "example_data.csv"

with open("title_to_mid.json", 'r', encoding="utf_8_sig") as file:
    mids = json.load(file)

# with open(fp, newline='') as csvfile:
#     sdvxreader = csv.reader(csvfile, delimiter=',') 

fails = []

with open(fp, newline='', encoding="utf_8_sig") as csvfile:
    sdvxreader = csv.DictReader(csvfile) 
    for row in sdvxreader:
        title = row['title']
        try: mid = mids[row['title']]
        except KeyError:
            fails.append(title)
        else: print(row['title'], mids[row['title']])

print(fails)
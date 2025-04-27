from string import ascii_letters, digits
from random import choices

ID_CHARS = ascii_letters + digits
def newID():
    return "".join(choices(ID_CHARS, k=16))

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
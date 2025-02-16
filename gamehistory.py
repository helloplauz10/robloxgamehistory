import os
import sys
import re
try:
    import requests
except ImportError:
    os.system(f"{sys.exectable} -m pip install requests")
    import requests

def fetchDataFromPlaceId(placeId):
    universeId = requests.get(f"https://apis.roblox.com/universes/v1/places/{placeId}/universe").json()
    data = requests.get(f"https://games.roblox.com/v1/games?universeIds={universeId['universeId']}").json()
    try:
        return data["data"][0]
    except:
        raise Exception(f"Error while retriving data. Data:\n{data}")

GameJoiningEntryPattern = r"! Joining game '([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})' place (\d+)"
if sys.platform == "darwin":
    logFolder = os.path.expanduser("~/Library/Logs/Roblox")
elif sys.platform == "win32":
    logFolder = os.path.join(os.getenv('LOCALAPPDATA'), "Roblox", "logs")
else:
    print("Not supported in your OS")

if not os.path.exists(logFolder):
    print("Roblox logs cannot be found.")
    sys.exit()

logs = [os.path.join(logFolder, filteredLogs) for filteredLogs in os.listdir(logFolder) if "Player" in filteredLogs]

if len(logs) == 0:
    print("Logs dont exist.")
    sys.exit()

print("Reading logs")

fetchedPlaceIds = {} # ex: {12345: [9999, "Free Robux Simulator"]} 9999 is how many times the user played it
for logFile in logs:
    with open(logFile, "r", errors = "ignore") as file:
        linesRead = file.readlines()
        for line in linesRead:
            if "[FLog::Output] ! Joining game" in line:
                placeId = re.search(GameJoiningEntryPattern, line).group(2)
                if not placeId in fetchedPlaceIds:
                    fetchedPlaceIds[str(placeId)] = [0, fetchDataFromPlaceId(placeId)["name"]]
                fetchedPlaceIds[str(placeId)][0] += 1
text = ""
for games in sorted(list(fetchedPlaceIds.values()), key = lambda count: count[0], reverse = True):
    text += f"Played {games[1]} {games[0]} time{'s' if games[0] < 1 else ''}\n"
text = text.rstrip()
print(text)

if input("Save? (y/n) ").lower() == "y":
    with open("gamesplayed.txt", "w") as file:
        file.write(text)

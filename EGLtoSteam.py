import model
import shortcuts
import steam
import communityids
import urllib.request
import json
import tkinter as tk
from tkinter import filedialog
import os.path
from os import listdir
import glob

def findEpicGames():

    choice = ""

    epicPath = ""

    print("Would you like to (a) automatically or (b) manually locate your Epic Games library?\n")
    while choice.lower() != "a" and choice.lower() != "b":
        choice = input("(a/b): ")

    if choice.lower() == "a":
        print("\nAttempting to automatically find your games...\n")
        if os.path.exists("C:\Program Files\Epic Games"):
            if os.listdir("C:\Program Files\Epic Games"):
                print("Library located. It contains the following games:")
                print("\n".join(os.listdir("C:\Program Files\Epic Games")))
            else:
                print("Library located. It contains no games.")
            print()
            print("Would you like to (a) continue, or (b) manually locate a different library?\n")
            choice = ""
            while choice.lower() != "a" and choice.lower() != "b":
                choice = input("(a/b): ")
            if choice.lower() == "a":
                epicPath = "C:\Program Files\Epic Games"
            else:
                print("\nThe folder is likely named 'Epic Games'.")
                root = tk.Tk()
                root.withdraw()
                epicPath = filedialog.askdirectory()
        else:
            print("Your library was not located. Please select it manually. The folder is likely named 'Epic Games'.")
            root = tk.Tk()
            root.withdraw()
            epicPath = filedialog.askdirectory()
    else:
        print("\nThe folder is likely named 'Epic Games'.")
        root = tk.Tk()
        root.withdraw()
        epicPath = filedialog.askdirectory()

    print()

    epicPath = epicPath.replace("/", "\\")

    epicGames = []

    for game in os.listdir(epicPath):
        if game == "Fortnite":
            pass
        else:
            exeLocation = epicPath+"\\"+game+"\\"+game+".exe"
            if os.path.exists(exeLocation):
                epicGames.append(model.Shortcut(
                    name = game,
                    exe = '"'+exeLocation+'"',
                    startdir = '"'+epicPath+"\\"+game+'"',
                    icon = '"'+exeLocation+'"',
                    tags = ["FromEpic"]
                ))
            else:
                exes =  glob.glob(epicPath+"\\"+game+"\\*.exe")
                if len(exes) == 1:
                    epicGames.append(model.Shortcut(
                        name = game,
                        exe = '"'+exes[0]+'"',
                        startdir = '"'+epicPath+"\\"+game+'"',
                        icon = '"'+exes[0]+'"',
                        tags = ["FromEpic"]
                    ))

    print("Located the following games:\n")
    print("\n".join([game.name for game in epicGames]))
    print("\nWould you like to add these games to your Steam library?\n")
    choice = ""
    while choice.lower() != "y" and choice.lower() != "n":
        choice = input("(y/n): ")
    if choice.lower() == "y":
        return epicGames
    else:
        return False

def addNonSteamGames(userContext):

    total_shortcuts = shortcuts.get_shortcuts(userContext)

    if None in total_shortcuts:
        total_shortcuts.remove(None)

    print()

    epicGames = findEpicGames()

    if not epicGames:
        return

    print()

    currentNames = [shortcut.name for shortcut in total_shortcuts]

    shortcutsToAdd = [shortcut for shortcut in epicGames if shortcut.name not in currentNames]

    print("Currently adding the following games:\n")
    
    print("\n".join(map(lambda shortcut : shortcut.name, shortcutsToAdd)))

    print()

    total_shortcuts = total_shortcuts+shortcutsToAdd

    shortcuts.set_shortcuts(userContext, total_shortcuts)

    print("Complete! Restart Steam to take effect.")

    input()

local_ids = steam.local_user_ids(steam.get_steam())

if '0' in local_ids:
    local_ids.remove('0')

if len(local_ids) == 1:
    # use the one id found
    addNonSteamGames(model.LocalUserContext(
        steam.get_steam(), 
        local_ids[0]
    ))
else:

    ids = list(map(lambda x : str(communityids.id64_from_id32(int(x))), steam.local_user_ids(steam.get_steam())))

    link = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=F43454CCD8828B3D538CA58CC05353DB&steamids=" + ",".join(ids)

    NamesWithIDs = {}

    try:
        with urllib.request.urlopen(link) as url:
            s = url.read()
            NamesWithIDs = dict([(user['personaname']+" (SteamID "+user['steamid']+")",user['steamid']) for user in json.loads(s)['response']['players']])
            #print(json.loads(s)['response']['players'])
    except:
        print("ERROR ACCESSING STEAM API")

    NumsWithNames = dict(zip(map(lambda x : str(x), range(1, len(NamesWithIDs)+1)), NamesWithIDs.keys()))
    
    #NumsWithNames = dict(zip(range(1, len(NamesWithIDs)+1), NamesWithIDs.keys()))

    print("Select Steam user\n")

    for num in NumsWithNames.keys():
        print(num + ": " + NumsWithNames[num])

    print()

    choice = ""

    while choice not in NumsWithNames.keys():
        choice = input("(1-"+str(len(NumsWithNames))+"): ")

    addNonSteamGames(model.LocalUserContext(
        steam.get_steam(),
        str(communityids.id32_from_id64(int(NamesWithIDs[NumsWithNames[choice]])))
    ))
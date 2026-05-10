from rich import print
from rich.panel import Panel
from rich.tree import Tree
import json
import curses
import random
import os
import time
from datetime import datetime
from cutscenes import basic_cutscene, epic_cutscene


def clear():
    os.system("clear")

def saveFile(p):
    with open("playerSave.json", "w") as f:
        json.dump(p, f, indent = 4)

DEFAULT_SAVE = {
    "name": "",
    "rebirth": 1,
    "talons": 100,
    "invcap": 80,
    "prism": {
    },
    "shardinv": {
    },
    "gear": {
    },
    "items": {

    }
}

try:
    with open("playerSave.json", "r") as f:
        playerData = json.load(f)
except:
    playerData = DEFAULT_SAVE
    with open("playerSave.json", "w") as f:
        json.dump(playerData,f,indent=4)


with open ("ratings.json", "r") as f:
    RARITIES = json.load(f)

with open ("enemies.json", "r") as f:
    ENEMIES = json.load(f)

def get_sorted_inv():
    return sorted(
        [(item, count) for item, count in playerData["shardinv"].items() if count > 0],
        key=lambda x: RARITIES.get(x[0], {"rarity": float("inf")})["rarity"]
    )


def roll_anim(key):
    for i in range (8):
        a = random.choice(list(RARITIES.keys()))
        print(f"> [{RARITIES[a]['hex']}] {RARITIES[a]['name']}[/] <")
        time.sleep(0.1)
        clear()
    for i in range (4):
        a = random.choice(list(RARITIES.keys()))
        print(f"> [{RARITIES[a]['hex']}] {RARITIES[a]['name']}[/] <")
        time.sleep(0.2)
        clear()
    for i in range(2):
        a = random.choice(list(RARITIES.keys()))
        print(f"> [{RARITIES[a]['hex']}] {RARITIES[a]['name']}[/] <")
        time.sleep(0.6)
        clear()
    print(f"> [{RARITIES[key]['hex']}] {RARITIES[key]['name']}[/] <")


def roll():
    a = ""
    count = 0
    while True:
        count += 1
        a = input("Enter to roll, q to quit: ")
        if a == "q":
            break
        while True:
            key = random.choice(list(RARITIES))
            rarity = RARITIES[key]["rarity"]
            if random.randint(1,rarity) <=1:
                roll_anim(key)
                if not RARITIES[key]["cutscene"]:
                    print(f"1 in {rarity} chance")
                else:
                    if RARITIES[key]["cutscene"] == "basic":
                        basic_cutscene(RARITIES[key]["hex"], RARITIES[key]["name"])
                    elif RARITIES[key]["cutscene"] == "epic":
                        epic_cutscene(RARITIES[key]["hex"], RARITIES[key]["name"])
                try:
                    playerData["shardinv"][key] += 1
                except:
                    playerData["shardinv"].update({key:1})
                break
    saveFile(playerData)

def inv():
    print("Inventory:")
    current_inv = get_sorted_inv()
    for i, (item, count) in enumerate(current_inv, start=1):
        print(f"{i}. {RARITIES[item]['name']}: {count}")
    ch = input("Press enter to go back or a the number to view details: ")
    if ch.isdigit() and 1 <= int(ch) <= len(current_inv):
        while True:
            clear()
            item, count = current_inv[int(ch) - 1]
            print(f"[{RARITIES[item]['hex']}] {RARITIES[item]['name']}[/]")
            print(f"Rarity: 1 in {RARITIES[item]['rarity']} chance")
            print(f"Description: {RARITIES[item]['desc']}")

            if RARITIES[item]['cutscene']:
                print("This item has a cutscene!")
                c = input("Press enter to go back or 'A' to view cutscene: ")
                if c.upper() == "A":
                    if RARITIES[item]['cutscene'] == "basic":
                        basic_cutscene(RARITIES[item]['hex'], RARITIES[item]['name'])
                        time.sleep(2)
                        clear()
                else:
                    break
            else:
                input("Press enter to go back: ")
                break

def combat():
    pass

def bounty_board():
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    round_minute = minute - (minute % 10)
    seed_string = f"{hour}{round_minute:02d}"
    seed_int = int(seed_string)
    seed = seed_int * 1000471 - 516637
    random.seed(seed)
    print("Bounty Board:")
    for i in range(3):
        enemy = random.choice(list(ENEMIES.keys()))
        print(f"{i+1}. {enemy}")
    c = input("Press enter to go back or the number to view details: ")
    if c.isdigit() and 1 <= int(c) <= 3:
        print(f"Enemy: {enemy}")
        print(f"Health: {ENEMIES[enemy]['health']}")
        print(f"{'★' * ENEMIES[enemy]['difficulty']}")
        a = input("Press enter to fight or Q to go back:")
        if a.upper() == "Q":
            return
        else:
            combat()

def forge():
    forg = []
    while True:
        print("[bold yellow] ⚔ Forge ⚔ [/]")
        print()
        print("Combine 4 or more shards to forge a weapon!")
        print("Only shards with the same elemental type can be forged together. However, shards wothout any type are compatible with any type.")
        for i in range(len(forg)+1):
            if i < len(forg):
                print(f"[{RARITIES[forg[i]]['hex']}] {i+1}. {RARITIES[forg[i]]['name']} [/]")
            else:
                print(f"{i+1}. [dim]Empty Slot[/]")
        print(f"{len(forg)+2}. Forge")
        choose = input("Press enter to go back or the number to view details and add, or Q to quit: ")
        if choose.upper() == "Q":
            break
        if choose.isdigit() and 1 <= int(choose) <= 4:
            while True:
                clear()
                print("Choose a shard to add:")
                current_inv = get_sorted_inv()
                for i, (item, count) in enumerate(current_inv, start=1):
                    print(f"[{RARITIES[item]['hex']}] {i}. {RARITIES[item]['name']} ({count}) [/]")
                c = input("Press enter to go back or the number to add: ")
                if c.isdigit() and 1 <= int(c) <= len(current_inv):
                    item, count = current_inv[int(c) - 1]
                    if count > 0:
                        forg.append(item)
                        print(f"Added {RARITIES[item]['name']} to forge!")
                        time.sleep(1)
                        break
                    else:
                        print("You don't have any of that shard!")
                        time.sleep(1)
                else:
                    break
        elif choose == str(len(forg)+2):
            if len(forg) < 4:
                print("You need at least 4 shards to forge!")
                time.sleep(1)
                return
            elements = set(RARITIES[item]['element'] for item in forg)
            if len(elements) > 2 or (len(elements) == 2 and "none" not in elements):
                print("Invalid combination of shards! All shards must share the same element or be non-elemental.")
                time.sleep(1)
                return
            for item in forg:
                playerData["shardinv"][item] -= 1
            saveFile(playerData)
            print("Forging weapon...")
            time.sleep(2)
            #MARK: forge logic
            forg.clear()
            print("Weapon forged! (not really, this is just a placeholder)")
            time.sleep(2)

def main():
    while True:
        clear()
        print("- Project Prism -")
        print("1. Roll")
        print("2. Inventory")
        print("3. Bounty Board")
        print("4. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            roll()
        elif choice == "2":
            inv()
        elif choice == "3":
            clear()
            bounty_board()
        elif choice == "4":
            print("Goodbye!")
            saveFile(playerData)
            break
        else:
            print("Invalid choice, try again.")
            time.sleep(1)
            clear()

forge()

from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
import json
import curses
import random
import os
import time
from datetime import datetime
from cutscenes import basic_cutscene, epic_cutscene

PREFIXES = {
    "none": ["Iron", "Steel", "Sturdy", "Flawless", "Polished"],
    "fire": ["Blazing", "Infernal", "Scorching", "Volcanic", "Ember"],
    "water": ["Tidal", "Aqueous", "Oceanic", "Abyssal", "Torrential"],
    "earth": ["Terra", "Seismic", "Crystalline", "Obsidian", "Tremor"],
    "ice": ["Glacial", "Frostbite", "Sub-zero", "Cryo", "Frozen"],
    "lightning": ["Voltaic", "Thundering", "Galvanic", "Storm", "Spark"],
    "hell": ["Demonic", "Nether", "Diabolic", "Soul-rending", "Inferno"],
    "darkness": ["Void", "Shadow", "Midnight", "Eclipse", "Abyssal"],
    "light": ["Radiant", "Luminous", "Divine", "Celestial", "Holy"]
}

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

console = Console()

# Example clear function as requested
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Prefix dictionary based on elements


def forge(playerData: dict, RARITIES: dict):
    clear()
    console.print(Panel.fit("[bold yellow]Welcome to the Forge![/bold yellow]\nCombine at least 4 compatible prisms to create a weapon.", border_style="yellow"))
    
    # Create a temporary inventory so we can deduct prisms as the player adds them to the forge
    temp_inv = {k: v for k, v in playerData.get("shardinv", {}).items()}
    
    selected_prisms = []
    current_element = "none" # Defaults to none until an elemental prism is added
    primary_hex = "#ffffff"  # Default color
    
    while True:
        # Display current forge status
        table = Table(title="Currently in Forge", show_header=True, header_style="bold magenta")
        table.add_column("Prism")
        table.add_column("Element")
        table.add_column("Power")
        
        total_power = 0
        for p_code in selected_prisms:
            p_data = RARITIES[p_code]
            table.add_row(p_data["name"], p_data["element"].title(), str(p_data["power"]))
            total_power += p_data["power"]
            
        console.print(table)
        console.print(f"[cyan]Current Forge Element Lock:[/] {current_element.title()}")
        console.print(f"[cyan]Total Power:[/] {total_power}")
        console.print(f"[cyan]Prisms Added:[/] {len(selected_prisms)}/4 minimum\n")
        
        # Display available inventory
        console.print("[bold green]Available Prisms in Inventory:[/bold green]")
        available_found = False
            
        for p_code, amount in playerData.get("shardinv", {}).items():
            if amount and int(amount) > 0 and p_code in RARITIES:
                p_data = RARITIES[p_code]
                color = p_data.get("hex", "#ffffff")
                console.print(f"- [{color}]{p_code}[/] ({p_data['name']}): x{amount} | Element: {p_data['element']} | Power: {p_data['power']}")
                available_found = True
                
        if not available_found:
            console.print("[red]No more prisms available![/red]")
            
        # Get player input
        console.print("\nType the [bold]code[/bold] of a prism to add it.")
        choice = Prompt.ask("Or type [bold yellow]'done'[/bold yellow] to forge, or [bold red]'cancel'[/bold red] to exit").lower().strip()
        
        if choice == "cancel":
            console.print("[red]Forging cancelled.[/red]")
            return
            
        if choice == "done":
            if len(selected_prisms) < 4:
                clear()
                console.print(f"[bold red]Not enough prisms! You need at least 4. You currently have {len(selected_prisms)}.[/bold red]\n")
                continue
            else:
                break
                
        # Validate chosen prism
        if choice not in temp_inv or temp_inv[choice] <= 0:
            clear()
            console.print(f"[bold red]You don't have any '{choice}' in your inventory![/bold red]\n")
            continue
            
        if choice not in RARITIES:
            clear()
            console.print(f"[bold red]Invalid prism code '{choice}'![/bold red]\n")
            continue
            
        # Check compatibility
        new_element = RARITIES[choice]["element"]
        if current_element == "none":
            # If forge is currently typeless, it takes on the new element (if the new one isn't typeless)
            if new_element != "none":
                current_element = new_element
                primary_hex = RARITIES[choice].get("hex", "#ffffff")
            is_compatible = True
        elif new_element == "none" or new_element == current_element:
            # Matches current element or is typeless
            is_compatible = True
        else:
            is_compatible = False
            
        if not is_compatible:
            clear()
            console.print(f"[bold red]Incompatible Elements![/bold red] You cannot mix {new_element.title()} with {current_element.title()}.\n")
            continue
            
        # Add to forge
        selected_prisms.append(choice)
        temp_inv[choice] -= 1
        clear()
        console.print(f"[green]Added {RARITIES[choice]['name']} to the forge![/green]\n")

    # --- FORGING CUTSCENE ---
    clear()
    console.print("[bold orange3]The forge begins to roar...[/bold orange3]")
    time.sleep(1.5)
    console.print(f"[{primary_hex}]Sparks of {current_element} magic fly into the air...[/{primary_hex}]")
    time.sleep(1.5)
    console.print("[bold yellow]The heavy hammer strikes the anvil![/bold yellow]")
    
    # Fake progress loading
    with console.status("[bold green]Forging weapon...", spinner="aesthetic"):
        time.sleep(3)
        
    clear()
    
    # --- WEAPON CALCULATION ---
    # Deduct permanently from actual playerSave now that forging is successful
    for p_code in selected_prisms:
        playerData["shardinv"][p_code] -= 1
        # Cleanup empty entries
        if playerData["shardinv"][p_code] <= 0:
            del playerData["shardinv"][p_code]

    # Calculate Type based on power
    if total_power < 100:
        wep_type = "Dagger"
        damage = int(total_power * random.uniform(0.8, 1.2))
    elif total_power < 250:
        wep_type = "Shortsword"
        damage = int(total_power * random.uniform(1.0, 1.4))
    elif total_power < 500:
        wep_type = "Longsword"
        damage = int(total_power * random.uniform(1.2, 1.6))
    elif total_power < 800:
        wep_type = "Warhammer"
        damage = int(total_power * random.uniform(1.5, 1.8))
    else:
        wep_type = "Greatsword"
        damage = int(total_power * random.uniform(1.8, 2.2))

    # Generate Name
    prefix = random.choice(PREFIXES.get(current_element, PREFIXES["none"]))
    weapon_name = f"{prefix} {wep_type}"
    weapon_id = f"wep_{int(time.time())}_{random.randint(100,999)}"
    
    # Create weapon dictionary
    new_weapon = {
        "name": weapon_name,
        "type": wep_type,
        "element": current_element,
        "power_rating": total_power,
        "damage": damage,
        "color": primary_hex
    }
    
    # Save to player gear
    playerData.setdefault("gear", {})[weapon_id] = new_weapon
    
    # Final display
    weapon_text = Text()
    weapon_text.append("Weapon Forged Successfully!\n\n", style="bold green")
    weapon_text.append(f"Name: {weapon_name}\n", style=f"bold {primary_hex}")
    weapon_text.append(f"Element: {current_element.title()}\n", style="italic")
    weapon_text.append(f"Damage: {damage}\n", style="bold red")
    weapon_text.append(f"Base Power: {total_power}", style="dim")
    
    console.print(Panel(weapon_text, border_style=primary_hex, expand=False))
    Prompt.ask("\nPress [bold]Enter[/bold] to continue")

def main():
    while True:
        clear()
        print("- Project Prism -")
        print("1. Roll")
        print("2. Inventory")
        print("3. Bounty Board")
        print("4. Forge")
        print("5. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            roll()
        elif choice == "2":
            inv()
        elif choice == "3":
            clear()
            bounty_board()
        elif choice == "4":
            forge()
        elif choice == "5":
            print("Goodbye!")
            saveFile(playerData)
            break
        else:
            print("Invalid choice, try again.")
            time.sleep(1)
            clear()

main()

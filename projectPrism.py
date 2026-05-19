from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.rule import Rule

console = Console()
#-------------------------

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual.reactive import reactive

#-------------------------

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
    "light": ["Radiant", "Luminous", "Divine", "Celestial", "Holy"],
    "time": ["Chrono", "Temporal", "Eternal", "Epoch", "Momentous"]
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
    "rolls": 0,
    "hp": 100,
    "startDate": (datetime.fromtimestamp(time.time())).strftime("%d-%m-%Y"),
    "shardinv": {
    },
    "weapons": {},
    "gear": {

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
    start = time.time()
    t = 0.02

    while time.time() - start < 3:
        time.sleep(t)
        console.clear()

        rarity = random.choice(list(RARITIES.values()))
        label = Text(f"✦  {rarity['name']}  ✦", style=f"bold {rarity['hex']}")

        console.print()
        console.print(Rule(style="dim white"))
        console.print(Align.center(
            Panel(
                Align.center(label),
                border_style=f"{rarity['hex']}",
                padding=(1, 6),
            )
        ))
        console.print(Rule(style="dim white"))

        t *= 1.2

    # Final reveal
    console.clear()
    winner = RARITIES[key]
    label = Text(f"★  {winner['name']}  ★", style=f"bold {winner['hex']}")

    console.print()
    console.print(Rule(f"[{winner['hex']}]Roll Result[/]", style=winner['hex']))
    console.print(Align.center(
        Panel(
            Align.center(label),
            border_style=f"bold {winner['hex']}",
            padding=(2, 8),
            subtitle=f"[{winner['hex']}]✦ 1 in {winner['rarity']} ✦[/]",
        )
    ))
    console.print(Rule(style=winner['hex']))


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
                if RARITIES[key]["cutscene"] == "basic":
                    basic_cutscene(RARITIES[key]["hex"], RARITIES[key]["name"], RARITIES[key]["rarity"])
                elif RARITIES[key]["cutscene"] == "epic":
                    epic_cutscene(RARITIES[key]["hex"], RARITIES[key]["name"], RARITIES[key]["rarity"])

                try:
                    playerData["shardinv"][key] += 1
                except:
                    playerData["shardinv"].update({key:1})
                break
    playerData['rolls'] += count
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
                        basic_cutscene(RARITIES[item]['hex'], RARITIES[item]['name'], RARITIES[item]['rarity'])
                        time.sleep(2)
                        clear()
                else:
                    break
            else:
                input("Press enter to go back: ")
                break

def draw_bar(current, maximum, length, color="#aaaaaa"):
    filled = int((current / maximum) * length)
    bar =  "█" * filled + "░" * (length - filled)
    bar = (f"[{color}] {bar} [/]")
    return bar


def combat(enem,playerData):
    if not playerData.get("weapons"):
        console.print("[red]You have no weapons to fight with![/red]")
        input("Press enter to go back: ")
        return
    current_equip = None
    def equip_weapon():
        weptable = Table(title="Weapons", show_header=True, header_style="#3581b8")
        weptable.add_column("No.", style="dim", width=6)
        weptable.add_column("Name")
        weptable.add_column("PR")
        weptable.add_column("Damage")
        weptable.add_column("Element")
        i = 1
        for code in playerData.get("weapons", {}):
            w = playerData["weapons"][code]
            weptable.add_row(str(i), w["name"], str(w["power_rating"]), str(w["damage"]), w["element"].title())
            i += 1
        console.print(weptable)
        choice = Prompt.ask("Type the no. of the weapon to equip: ").strip()
        if choice.isdigit() and 1 <= int(choice) < i:
            selected_code = list(playerData["weapons"].keys())[int(choice) - 1]
            nonlocal current_equip
            current_equip = playerData["weapons"][selected_code]
            console.print(f"You equipped [bold {current_equip['color']}]{current_equip['name']}[/bold {current_equip['color']}]!")
        
        return current_equip

    def equip_prism():
        tempinv = get_sorted_inv()
        equipped = []
        while len(equipped) < 3:
            equippedname = []
            if not tempinv:
                console.print("You have no prisms to bring into battle!")
                return
            for item in equipped:
                equippedname.append(RARITIES[item]["name"])
            prismtable = Table(title="Prisms", show_header=True, header_style="#5EA85C")
            prismtable.add_column("No.", style="dim", width=6)
            prismtable.add_column("Name")
            prismtable.add_column("Element")
            prismtable.add_column("Rarity (1 in _)")
            prismtable.add_column("Quantity")
            j = 1
            for code, qty in tempinv:
                rarity = RARITIES.get(code, {})
                name = rarity.get('name', code)
                element = rarity.get('element', 'Unknown').capitalize()
                rarity_rank = rarity.get('rarity', 'Unknown')
                prismtable.add_row(str(j), name, element, str(rarity_rank), str(qty))
                j += 1
            console.print(prismtable)
            print(f"Currently equipped: {", ".join(equippedname)}")
            c = input("Equip up to 3 prisms! Enter the number of the Prism you'd like to equip: ")
            if c.lower() == "q": 
                break
            if c.isdigit():
                choice = int(c)
                if 1 <= choice < j:
                    code, qty = tempinv[choice - 1]
                    if code not in equipped:
                        equipped.append(code)
                        if qty > 1:
                            tempinv[choice - 1] = (code, qty - 1)
                        else:
                            del tempinv[choice - 1]
                        continue
                    else:
                        print("[italic red]Cannot equip two of the same Prism at once![/]")
                        time.sleep(1)
                        clear()
                        continue
            print("[bold red]Invalid input! [/]")
            time.sleep(1)
            clear()
        playerData["shardinv"] = {code: qty for code, qty in tempinv}

        equippedname = []
        for item in equipped:
            equippedname.append(RARITIES[item]["name"])
        return equipped, equippedname
    playerwep = equip_weapon()
    equippedprisms, equippedprismsname = equip_prism()

    clear()
    print(f"Prisms equipped: {", ".join(equippedprismsname)}")
    enemy = ENEMIES[enem]
    if enemy["difficulty"] <= 5:
        star = "✦"*enemy["difficulty"]
    console.print(f"A [bold red] {enemy['name']} < {star} >[/] appeared!")

    turn = 1
    playerTurn = True

    def main_combat_loop(stdscr, playerData, enemyData, weapon, equippedprisms):

        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(30)

        player_health = playerData["hp"]
        enemy_health = enemyData["health"]
        current_phase = "player_attack"

        combo = 0
        damage = 0
        current_index = 0
        running = True

        while running:
            if player_health <= 0 or enemy_health <= 0:
                break

            if current_phase == "player_attack": #player attack phase
                time_limit = 5
                seq_start = time.time()
                combo_keys = ["z", "x", "c", "v"]
                atk_sequence = [random.choice(combo_keys) for _ in range (7)]

                while True:
                    remaining = round(time_limit - (time.time()-seq_start), 1)
                    if remaining <= 0:
                        break
                    
                    stdscr.clear()
                    stdscr.addstr(1,2,"== Offensive phase ==")
                    stdscr.addstr(3,2,f"{weapon["name"]}")
                    stdscr.addstr(5,2,f"Time remaining: {remaining}")

                    stdscr.addstr(8,2,f"Attack Sequence: ")

                    display = ""

                    for i, key in enumerate(atk_sequence):
                        if i < current_index:
                            display += f"[{key.upper()}] "
                        else:
                            display += f" {key.upper()}  "
                    
                    stdscr.addstr(10,2,display)
                    stdscr.addstr(12, 2, f"Combo: {combo}")
                    stdscr.addstr(13, 2, f"Damage: {damage}")

                    stdscr.refresh()

                    key = stdscr.getch()
                    if key == -1:
                        continue
                    
                    try:
                        pressed = chr(key).lower()
                    except:
                        continue
                    
                    if pressed == atk_sequence[current_index]:
                        damage += round(((weapon["damage"] + random.randint(-10,10)) / len(atk_sequence))) + combo * 2
                        current_index += 1

                        if current_index >= len(atk_sequence):
                            current_phase = "enemy_attack"
                            current_index = 0
                            break
                    else:
                        combo = 0
                damage = round(damage * random.random())
                enemy_health -= damage
                current_phase = "enemy_attack"

            if current_phase == "enemy_attack":
                attack_name, attack_power = random.choice(list(enemyData['attack'].items()))
                dodge_needed = enemyData['speed'] * 3
                dodge_count = 0

                time_limit = 5
                start_time = time.time()
                while True:
                    remaining = round(time_limit - (time.time() - start_time),1)

                    if remaining <= 0:
                        break

                    stdscr.refresh()
                    stdscr.clear()
                    stdscr.addstr(2,2,"== Defensive Phase ==")
                    stdscr.addstr(3,2,"Dodge by mashing A and D or hit a Perfect Parry for a counterrattack!")
                    bar = draw_bar(dodge_count,dodge_needed,30)
                    stdscr.addstr(5,2,f"Dodge meter: [{bar}]")

                    key = stdscr.getch()

                    if key == -1:
                        continue

                    try:
                        pressed = chr(key).lower()
                    except:
                        continue

                    if pressed == "a" or pressed == "d":
                        dodge_count += 1
                
                if dodge_count >= dodge_needed:
                    stdscr.addstr(3,2,"Dodge successful!")
                else:
                    dmg = round(2 * dodge_count / dodge_needed) * attack_power
                    stdscr.addstr(4,2,f"Took {dmg} damage!")
                current_phase = "player_attack"

    curses.wrapper(main_combat_loop, playerData, enemy, playerwep, None)

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
        print(f"{i+1}. {ENEMIES[enemy]['name']}")
    c = input("Press enter to go back or the number to view details: ")
    if c.isdigit() and 1 <= int(c) <= 3:
        print(f"Enemy: {ENEMIES[enemy]['name']}")
        print(f"Health: {ENEMIES[enemy]['health']}")
        print(f"{'★' * ENEMIES[enemy]['difficulty']}")
        a = input("Press enter to fight or Q to go back:")
        if a.upper() == "Q":
            return
        else:
            combat(enemy, playerData)


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
        
        # Display available inventory and build numbered list
        # Display available inventory and build numbered list
        console.print("[bold green]Available Prisms in Inventory:[/bold green]")
        
        # Create the Selection Table
        inv_table = Table(show_header=True, header_style="bold cyan")
        inv_table.add_column("#", style="dim", width=3)
        inv_table.add_column("Prism Name")
        inv_table.add_column("Element", justify="center")
        inv_table.add_column("Power", justify="right")
        inv_table.add_column("Stock", justify="right")

        available_choices = [] 
        
        for p_code, amount in temp_inv.items():
            if amount > 0 and p_code in RARITIES:
                available_choices.append(p_code)
                p_data = RARITIES[p_code]
                color = p_data.get("hex", "#ffffff")
                index_num = len(available_choices)
                
                # Add row to the selection table
                inv_table.add_row(
                    str(index_num),
                    Text(p_data['name'], style=color),
                    p_data['element'].title(),
                    str(p_data['power']),
                    f"x{amount}"
                )
                
        if not available_choices:
            console.print("[red]No more prisms available![/red]")
        else:
            console.print(inv_table)
            
        # Get player input
        console.print("\nType the [bold]number[/bold] of a prism to add it.")
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
                
        # Number Validation
        try:
            # Convert input to integer and adjust for 0-based indexing
            choice_idx = int(choice) - 1 
            
            # Check if the number is within the valid range
            if choice_idx < 0 or choice_idx >= len(available_choices):
                clear()
                console.print(f"[bold red]Invalid choice! Please pick a number between 1 and {len(available_choices)}.[/bold red]\n")
                continue
                
            # Map the valid number back to the actual prism code
            selected_code = available_choices[choice_idx]
            
        except ValueError:
            # Catches the error if they typed a random word instead of a number
            clear()
            console.print("[bold red]Invalid input! Please enter a valid number, 'done', or 'cancel'.[/bold red]\n")
            continue
            
        # Check compatibility using the selected_code
        new_element = RARITIES[selected_code]["element"]
        if current_element == "none":
            # If forge is currently typeless, it takes on the new element (if the new one isn't typeless)
            if new_element != "none":
                current_element = new_element
                primary_hex = RARITIES[selected_code].get("hex", "#ffffff")
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
        selected_prisms.append(selected_code)
        temp_inv[selected_code] -= 1
        clear()
        console.print(f"[green]Added {RARITIES[selected_code]['name']} to the forge![/green]\n")

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
    # Deduct permanently from actual playerData now that forging is successful
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
    playerData.setdefault("weapons", {})[weapon_id] = new_weapon
    
    # Final display
    weapon_text = Text()
    weapon_text.append("Weapon Forged Successfully!\n\n", style="bold green")
    weapon_text.append(f"Name: {weapon_name}\n", style=f"bold {primary_hex}")
    weapon_text.append(f"Element: {current_element.title()}\n", style="italic")
    weapon_text.append(f"Damage: {damage}\n", style="bold red")
    weapon_text.append(f"Base Power: {total_power}", style="dim")
    
    console.print(Panel(weapon_text, border_style=primary_hex, expand=False))
    Prompt.ask("\nPress [bold]Enter[/bold] to continue")

def stat(playerData):
    clear()
    console.print(Rule("[#8CD790] ✦ Player Stats ✦ [/]"))
    print(f"Lifetime rolls: {playerData['rolls']}")
    print(f"Start date: {playerData['startDate']}")
    input("Press enter to continue: ")

def main():
    while True:
        clear()
        print("- Project Prism -")
        print("1. Roll")
        print("2. Inventory")
        print("3. Bounty Board")
        print("4. Forge")
        print("5. Stats")
        print("6. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            roll()
        elif choice == "2":
            inv()
        elif choice == "3":
            clear()
            bounty_board()
        elif choice == "4":
            forge(playerData, RARITIES)
        elif choice == "5":
            stat(playerData)
        elif choice == "6":
            print("Goodbye!")
            saveFile(playerData)
            break
        else:
            print("Invalid choice, try again.")
            time.sleep(1)
            clear()

# pygame.mixer.music.load("music/tn-shi - Synthesis..mp3")
# pygame.mixer.music.play()

# while True:
#     pass

main()
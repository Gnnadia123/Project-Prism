print("Now loading...")

from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.layout import Layout
from rich.live import Live

from rich_gradient import Gradient

console = Console()

#-------------------------

import json
import string
import random
import os
import time
import threading
import readchar
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

RANK_COLORS = {
    "E": "bbcbcb",
    "D": "E6CCBE",
    "C": "83C5BE",
    "B": "95190C",
    "A": "228CDB",
    "S": "A846A0",
}

def clear():
    os.system("clear")

def reset():
    os.system("reset")

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
    "inv": {},
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

with open ("items.json", "r") as f:
    ITEMS = json.load(f)

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
        clear()

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
    clear()
    print("1. Prisms")
    print("2. Items")
    a = input("Enter choice: ")
    if a == "1":
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
    elif a == "2":
        for item in playerData['inv']:
            curItem = ITEMS[item]
            prin = ""
            prin += (f"[#{RANK_COLORS[curItem['rank']]}]{curItem['name']}[/]")
            prin += " | "
            prin += (f"[#{RANK_COLORS[curItem['rank']]}]Rank {curItem['rank']}[/]")
            print(prin)
        input("Press enter to continue: ")

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
    uniqueprisms = []
    for prism in playerData["shardinv"]:
        uniqueprisms.append(prism)
    if len(uniqueprisms) < 3:
        print("You do not have enough prisms to bring into combat!")
        time.sleep(2)
        return
    playerwep = equip_weapon()
    try:
        equippedprisms, equippedprismsname = equip_prism()
    except:
        return

    clear()
    print(f"Prisms equipped: {", ".join(equippedprismsname)}")
    enemy = ENEMIES[enem]
    if enemy["difficulty"] <= 5:
        star = "✦"*enemy["difficulty"]
    console.print(f"A [bold red] {enemy['name']} < {star} >[/] appeared!")

    combat_running = False
    last_key = None
    key_seq = []
    input_thread = None

    def listener():
        nonlocal combat_running
        nonlocal last_key
        nonlocal key_seq

        while combat_running:
            key = readchar.readkey()
            key_seq.append(key)
    
    def start_input_thread():
        nonlocal combat_running
        nonlocal input_thread

        combat_running = True
        input_thread = threading.Thread(
            target=listener,
            daemon=True
        )

        input_thread.start()
    
    def stop_input_thread():
        nonlocal combat_running
        nonlocal input_thread
        combat_running = False

        if input_thread is not None:
            input_thread.join(timeout=0.1)


    def draw_bar(remaining,total,w):
        n = int(max(0, remaining) / max(total, 1) * w)
        return str("[" + ("▰" * n + "▱" * (w - n) ) + "]")


    def main_combat_loop(playerData, enemyData, weapon, equippedprisms):
        combat_running = True
        PAUSE_MS = 0.03

        current_phase = "attack"
        usedprisms = {}

        for prism in equippedprisms:
            # `equippedprisms` is a list of prism codes (strings).
            # Initialize a small state dict for each equipped prism.
            usedprisms[prism] = {"used": False, "broken": False}


        phase_color = {
            "attack": "blue",
            "defence": "red",
            "quicktime rush": "green",
            "prism activation": "teal"
        }

        enemy_health = enemyData['health']
        player_health = playerData['hp']
        enemy_status_effect = ""
        player_status_effect = ""
        dodge_count = 0
        dodge_req = 0

        def dashboards() -> Layout:
            layout = Layout()
            layout.split_column(
                Layout(name="top", ratio=5),
                Layout(name="bottom", ratio=12)
            )
            layout["bottom"].split_row(
                Layout(name="left", ratio=7),
                Layout(name="right", ratio=5)
            )
            layout["right"].split_column(
                Layout(name="right_top", ratio=6),
                Layout(name="right_bottom", ratio=6)
            )
            return layout

        def update_box(layout, box_name, content, styl, title = "") -> None:
            layout[box_name].update(
                Panel(content, title=title, border_style=styl, title_align="center")
            )

        layout = dashboards()

        def panel_manager():
            top_text = f"[red]Enemy HP: {enemy_health}[{phase_color[current_phase]}] ── {current_phase.upper()} ── [green]Player HP: {player_health}[/]"
            update_box(layout, "top", top_text, "white")

            if current_phase == "attack":

                sequence_display = []
                for i, key in enumerate(atk_sequence):
                    if i < current_attack_index:
                        sequence_display.append(f"[bold blue]{key}[/]")
                    else:
                        sequence_display.append(key)
                display_seq = " ".join(sequence_display)
                left_text = f"Time Remaining: {time_remaining}\n\nAttack Sequence:\n{display_seq}"
                color = "#2cdb1f" if int(time_remaining * 10) % 2 == 0 else "#1f9100"
                update_box(layout, "left", left_text, color)

            elif current_phase == "defence":

                bar = draw_bar(dodge_count, dodge_req, 30)
                left_text = "Mash A/D to avoid attacks!\n\n" + bar + f" {dodge_count}/{dodge_req}" + "\n\n" + str(time_remaining) 
                color = "#db221f" if int(time_remaining * 10) % 2 == 0 else "#910000"
                update_box(layout, "left", left_text, color)

            prism_lines = []
            for prism in usedprisms:
                if usedprisms[prism]["used"]:
                    prism_lines.append(f"[{RARITIES[prism]['hex']}]< {RARITIES[prism]['name']} >[/]")
                elif usedprisms[prism]["broken"]:
                    prism_lines.append(f"[strike {RARITIES[prism]['hex']}]" + RARITIES[prism]['name'] + "[/]")
                else:
                    prism_lines.append(f"[{RARITIES[prism]['hex']}]" + RARITIES[prism]['name'] + "[/]")
            update_box(layout, "right_top", Align.center("\n".join(prism_lines)), "white")

            weapon_lines = [
                f"[{weapon['color']}] {weapon['name']} [/]",
                f"Element: {weapon['element'].capitalize()}",
                f"Damage: {weapon['damage']}",
                f"PR: {weapon['power_rating']}"
            ]
            update_box(layout, "right_bottom", "\n".join(weapon_lines), "white")

        start_input_thread()

        change = True
        atk_sequence = []
        time_limit = 5
        dodge_limit = ENEMIES[enem]['atktime']

        with Live(layout, refresh_per_second=30, screen=True) as live:
            while combat_running:
                if player_health <= 0 or enemy_health <= 0:
                    combat_running = False
                    break
                if current_phase == "attack":
                    if change:
                        atk_sequence = [random.choice(["Z", "X", "C", "V"]) for _ in range(7)]
                        current_attack_index = 0
                        change = False
                    start_time = time.time()
                    combo = 0
                    dmg_dealt = 0
                    while True:
                        time_remaining = round((time_limit - (time.time() - start_time)), 1)
                        if time_remaining <= 0 or current_attack_index >= len(atk_sequence):
                            current_phase = "defence"
                            break

                        if key_seq:
                            key = key_seq.pop(0)
                            if key.upper() == atk_sequence[current_attack_index]:
                                combo += 1
                                current_attack_index += 1
                                dmg_dealt = round((combo * weapon["damage"]) / len(atk_sequence), 1)
                            else:
                                combo = 0

                        panel_manager()
                        live.update(layout)
                        time.sleep(PAUSE_MS)
                    enemy_health = max(0, round(enemy_health - dmg_dealt,1))
                    current_phase = "defence"
                elif current_phase == "defence":
                    attack = random.choice(list(enemyData["attack"].keys()))
                    start_time = time.time()
                    dodge_req = random.randint(round(enemyData["speed"] * 2.5)-3, (round(enemyData["speed"] * 2.5)) + 5)
                    dodge_count = 0
                    dodge_success = False
                    while True:
                        time_remaining = round(dodge_limit - (time.time() - start_time), 1)
                        if dodge_count >= dodge_req or time_remaining <= 0:
                            dodge_success = True
                            break

                        if key_seq:
                            key = key_seq.pop(0)
                            if key.upper() in ["A", "D"]:
                                dodge_count += 1
                        panel_manager()
                        live.update(layout)
                        time.sleep(PAUSE_MS)
                    if dodge_success:
                        dmg_received = 0
                    else:
                        deficit = dodge_req - dodge_count
                        dmg_received = round(0.7 * deficit * enemyData[attack])
                    player_health = max(0, player_health - dmg_received)
                    change = True
                    current_phase = "attack"
                panel_manager()
                live.update(layout)

    main_combat_loop(playerData,enemy,playerwep,equippedprisms)
    stop_input_thread()
    print("Buffering... Give us a moment")
    time.sleep(1)
    reset()
    clear()
    winItems = []
    uniquewinItems = []
    console.print(Rule("[bold green] You win! [/]"))
    for i in range(random.randint(1,(ENEMIES[enem]['difficulty'])+2)):
        itemWon = random.choice(list(ENEMIES[enem]['drops']))
        winItems.append(itemWon)
    uniquewinItems = set(winItems)
    for item in uniquewinItems:
        talon = False
        count = 0
        for eac in winItems:
            if eac == item and eac != "talon":
                count += 1
                try:
                    playerData['inv'][eac] += 1 
                except: 
                    playerData['inv'][eac] = 1
            elif eac == item and eac == "talon":
                talon = True
                count += random.randint(ENEMIES[enem]['difficulty']*10, ENEMIES[enem]['difficulty']*20)
                playerData['talons'] += count
        if talon:
            console.print(f"[italic yellow]{count}x Talons[/]")
        else:
            console.print(f"[italic]{count}x {ITEMS[item]['name']} | Rank {ITEMS[item]['rank']}[/]")
    input("Press enter to continue... ")



def bounty_board():
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    round_minute = minute - (minute % 10)
    seed_string = f"{hour}{round_minute:02d}"
    seed_int = int(seed_string)
    seed = seed_int * 1000471 - 516637
    enemies = []
    random.seed(seed)
    print("Bounty Board:")
    for i in range(3):
        enemy = random.choice(list(ENEMIES.keys()))
        enemies.append(enemy)
        print(f"{i+1}. {ENEMIES[enemy]['name']}")
    c = input("Press enter to go back or the number to view details: ")
    if c.isdigit() and 1 <= int(c) <= 3:
        c = int(c)
        c -= 1
        print(f"Enemy: {ENEMIES[enemies[int(c)]]['name']}")
        print(f"Health: {ENEMIES[enemies[int(c)]]['health']}")
        print(f"{'★' * ENEMIES[enemies[int(c)]]['difficulty']}")
        a = input("Press enter to fight or Q to go back:")
        if a.upper() == "Q":
            return
        else:
            combat(enemies[int(c)], playerData)
    random.seed()


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
    console.print(f"[{primary_hex}]Sparks of magic fly into the air...[/{primary_hex}]")
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
    print(f"[bold green]Lifetime rolls: {playerData['rolls']}[/]")
    print(f"[italic red]Start date: {playerData['startDate']}[/]")
    print(f"[bold yellow]Talons: {playerData['talons']}[/]")
    input("Press enter to continue: ")

def main():
    while True:
        clear()
        menu = Align.center("""
        1. Roll
        2. Inventory
        3. Bounty Board, Battle
        4. Weapon Forge
        5. Statistics
        """)
        print(Panel(menu,title=" ✦ Project Prism ✦ ",subtitle="6. Quit",style="#8CBCB9",border_style="#EAFFDA"))
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
            print("Saving...")
            saveFile(playerData)
            print("Saved!")
            break
        else:
            print("[red]Invalid choice, try again. [/]")
            time.sleep(1)
            clear()
reset()
main()
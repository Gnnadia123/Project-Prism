import time
from matplotlib.pyplot import draw
from matplotlib.pyplot import draw
from rich import print
import os
import math
from rich.console import Console
console = Console()

def clear(): 
    os.system("clear")


from rich.console import Console
import time
import math


def basic_cutscene(color,text):
    WIDTH = 40
    HEIGHT = 5

    # --- Phase 1: close into white ---
    for i in range(21):
        clear()

        for _ in range(HEIGHT):
            row = ""

            for k in range(WIDTH):
                if k < i or k >= WIDTH - i:
                    row += "[white]█[/]"
                else:
                    row += " "

            print(row)

        time.sleep(0.04)

    # --- Phase 2: blue paints from centre ---
    cx = WIDTH // 2
    cy = HEIGHT // 2
    max_radius = math.sqrt(cx**2 + cy**2)

    for frame in range(int(max_radius) + 2):
        clear()

        for y in range(HEIGHT):
            row = ""

            for x in range(WIDTH):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)

                if dist <= frame:
                    # blue wave
                    row += f"[{color}]█[/]"
                else:
                    # keep the white canvas
                    row += "[white]█[/]"

            print(row)

        time.sleep(0.04)
    
    # -- phase 3: open from centre into star --
    for frame in range(int(max_radius) + 2):
        clear()

        for y in range(HEIGHT):
            row = ""

            for x in range(WIDTH):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)

                if dist <= frame:
                    # cleared area (empty)
                    char = " "
                else:
                    # remaining blue
                    char = f"[{color}]█[/]"

                # ⭐ star stays in centre
                if x == cx and y == cy:
                    char = "[bold white]✦[/]"

                row += char

            print(row)

        time.sleep(0.04)
    
    # -- phase 4: star blink + horizontal expansion --

# ⭐ blink twice (same as before)
    for _ in range(3):
        clear()
        for y in range(HEIGHT):
            row = ""
            for x in range(WIDTH):
                if x == cx and y == cy:
                    row += "[bold white]✦[/]"
                else:
                    row += " "
            print(row)
        time.sleep(0.6)

        clear()
        for _ in range(HEIGHT):
            print(" " * WIDTH)
        time.sleep(0.6)


    # 🌊 expanding wave that reveals text (letters stay centered)
    text = f"> {text} <"
    text_x = cx - len(text)//2
    text_y = cy

    for offset in range(cx + 2):
        clear()

        for y in range(HEIGHT):
            row = ""

            for x in range(WIDTH):
                char = " "

                if y == cy:
                    left_edge = cx - offset
                    right_edge = cx + offset

                    # leading wave blocks
                    if x == left_edge or x == right_edge:
                        char = f"[bold {color}]█[/]"

                    # reveal letters AFTER wave passes
                    if text_x <= x < text_x + len(text):
                        if x >= left_edge and x <= right_edge:
                            # wave has passed → reveal letter
                            letter = text[x - text_x]
                            char = f"[{color}]{letter}[/]"

                row += char

            print(row)

        time.sleep(0.015)


#MARK: Epic

def epic_cutscene(color="bold cyan", msg="hello"):
    text="█"
    console = Console()
    
    # Configuration
    WIDTH = 60
    HEIGHT = 10
    
    # Starting positions for Phase 1
    h1_x, h1_y = 0, 1
    h2_x, h2_y = WIDTH - 1, 8
    
    trail1 = []
    trail2 = []
    MAX_TRAIL = 20 

    target_x, target_y = WIDTH // 2, HEIGHT // 2

    # ==========================================
    # PHASE 1: The Swirl
    # ==========================================
    def draw_phase1(h1, h2, t1, t2):
        clear()
        output = []
        for y in range(HEIGHT):
            line_chars = []
            for x in range(WIDTH):
                if (x == h1[0] and y == h1[1]) or (x == h2[0] and y == h2[1]) or (x, y) in t1 or (x, y) in t2:
                    line_chars.append(f"{text}")
                else:
                    line_chars.append(" ")
            output.append("".join(line_chars))
        console.print("\n".join(output))

    active = True
    while active:
        if h1_x == target_x and h1_y == target_y and h2_x == target_x and h2_y == target_y:
            if trail1:
                trail1.pop(0)
                trail2.pop(0)
            else:
                active = False
                break
        else:
            trail1.append((h1_x, h1_y))
            trail2.append((h2_x, h2_y))
            
            if len(trail1) > MAX_TRAIL: trail1.pop(0)
            if len(trail2) > MAX_TRAIL: trail2.pop(0)

            if h1_x < target_x: h1_x += 1
            elif h1_y < target_y: h1_y += 1
                
            if h2_x > target_x: h2_x -= 1
            elif h2_y > target_y: h2_y -= 1

        draw_phase1((h1_x, h1_y), (h2_x, h2_y), trail1, trail2)
        
        
        time.sleep(0.04)

    # Brief pause before the diamond expansion
    time.sleep(0.2)

    # ==========================================
    # PHASE 2: The Fading Diamond
    # ==========================================
    # A radius of 5 creates a 10x10 diamond (actually 11x11, fitting the 10 height perfectly)
    MAX_RADIUS = 5 
    
    # We loop past MAX_RADIUS to allow the fade wave to completely pass the screen edge

    for i in range (2):
        time.sleep(0.5)
        clear()
        for wave_front in range(1, MAX_RADIUS + 7): 
            clear()
            output = []
            
            for y in range(HEIGHT):
                line_chars = []
                for x in range(WIDTH):
                    # The center block remains unchanged eternally
                    if x == target_x and y == target_y:
                        line_chars.append(f"{text}")
                        continue

                    # Calculate Manhattan Distance to form the diamond
                    dist_from_center = abs(x - target_x) + abs(y - target_y)

                    # Only draw if within the max diamond size AND reached by the wave front
                    if dist_from_center <= MAX_RADIUS and dist_from_center <= wave_front:
                        
                        # Calculate how far this cell is behind the expanding edge
                        dist_from_edge = wave_front - dist_from_center
                        
                        if dist_from_edge <= 2:
                            char = text
                        elif dist_from_edge == 3:
                            char = "▓"
                        elif dist_from_edge == 4:
                            char = "▒"
                        elif dist_from_edge == 5:
                            char = "░"
                        else:
                            char = " " # Completely faded
                            
                        if char != " ":
                            line_chars.append(f"{char}")
                        else:
                            line_chars.append(" ")
                    else:
                        line_chars.append(" ")
                        
                output.append("".join(line_chars))
                
            console.print("\n".join(output))
            time.sleep(0.04) 

    #last diamond
    time.sleep(0.5)
    clear()
    for wave_front in range(1, MAX_RADIUS + 7): 
        clear()
        output = []
        
        for y in range(HEIGHT):
            line_chars = []
            for x in range(WIDTH):
                # The center block remains unchanged eternally
                if x == target_x and y == target_y:
                    line_chars.append(f"[{color}]{text}")
                    continue

                # Calculate Manhattan Distance to form the diamond
                dist_from_center = abs(x - target_x) + abs(y - target_y)

                # Only draw if within the max diamond size AND reached by the wave front
                if dist_from_center <= MAX_RADIUS and dist_from_center <= wave_front:
                    
                    # Calculate how far this cell is behind the expanding edge
                    dist_from_edge = wave_front - dist_from_center
                    
                    if dist_from_edge <= 2:
                        char = text
                    elif dist_from_edge == 3:
                        char = "▓"
                    elif dist_from_edge == 4:
                        char = "▒"
                    elif dist_from_edge == 5:
                        char = "░"
                    else:
                        char = " " # Completely faded
                        
                    if char != " ":
                        line_chars.append(f"[{color}]{char}")
                    else:
                        line_chars.append(" ")
                else:
                    line_chars.append(" ")
                    
            output.append("".join(line_chars))
            
        console.print("\n".join(output))
        time.sleep(0.06) 
    clear()

    time.sleep(0.5)

    cx = WIDTH // 2
    cy = HEIGHT // 2

    text = f"> {msg} <"
    text_x = cx - len(text)//2
    text_y = cy

    for offset in range(cx + 2):
        clear()

        for y in range(HEIGHT):
            row = ""

            for x in range(WIDTH):
                char = " "

                if y == cy:
                    left_edge = cx - offset
                    right_edge = cx + offset

                    # leading wave blocks
                    if x == left_edge or x == right_edge:
                        char = f"[{color}]█[/]"

                    # reveal letters AFTER wave passes
                    if text_x <= x < text_x + len(text):
                        if x >= left_edge and x <= right_edge:
                            # wave has passed → reveal letter
                            letter = text[x - text_x]
                            char = f"[{color}]{letter}[/]"

                row += char

            print(row)

        time.sleep(0.01)


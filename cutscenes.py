import time
from matplotlib.pyplot import draw
from matplotlib.pyplot import draw
from rich import print
import os
import math
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
console = Console()

def clear(): 
    os.system("clear")


from rich.console import Console
import time
import math


# ── shared renderer ────────────────────────────────────────────────────────────
def render_panel(lines: list[str], border_color: str, subtitle: str = ""):
    """Render a list of Rich markup strings inside the shared Panel border."""
    body = Text.from_markup("\n".join(lines))
    console.clear()
    console.print()
    console.print(Rule(style=f"dim {border_color}"))
    console.print(Align.center(
        Panel(
            Align.center(body),
            border_style=f"bold {border_color}",
            padding=(0, 6),
            subtitle=f"[dim {border_color}]{subtitle}[/]" if subtitle else "",
        )
    ))
    console.print(Rule(style=f"dim {border_color}"))


# ── cutscene ───────────────────────────────────────────────────────────────────
def basic_cutscene(color: str, text: str, rarity: int):
    WIDTH  = 40
    HEIGHT = 5
    cx, cy = WIDTH // 2, HEIGHT // 2

    # --- Phase 1: white bars close inward ---
    for i in range(21):
        lines = []
        for _ in range(HEIGHT):
            row = ""
            for k in range(WIDTH):
                row += "[white]█[/]" if (k < i or k >= WIDTH - i) else " "
            lines.append(row)
        render_panel(lines, "white")
        time.sleep(0.04)

    # --- Phase 2: colour floods from centre ---
    max_radius = math.sqrt(cx**2 + cy**2)
    for frame in range(int(max_radius) + 2):
        lines = []
        for y in range(HEIGHT):
            row = ""
            for x in range(WIDTH):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                row += f"[{color}]█[/]" if dist <= frame else "[white]█[/]"
            lines.append(row)
        render_panel(lines, color)
        time.sleep(0.04)

    # --- Phase 3: open from centre, star appears ---
    for frame in range(int(max_radius) + 2):
        lines = []
        for y in range(HEIGHT):
            row = ""
            for x in range(WIDTH):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                if x == cx and y == cy:
                    char = "[bold white]✦[/]"
                elif dist <= frame:
                    char = " "
                else:
                    char = f"[{color}]█[/]"
                row += char
            lines.append(row)
        render_panel(lines, color)
        time.sleep(0.04)

    # --- Phase 4a: star blinks ---
    blank = [" " * WIDTH] * HEIGHT
    for _ in range(3):
        star_lines = [" " * WIDTH] * HEIGHT
        star_row = " " * cx + "[bold white]✦[/]" + " " * (WIDTH - cx - 1)
        star_lines = blank[:cy] + [star_row] + blank[cy + 1:]
        render_panel(star_lines, color)
        time.sleep(0.6)
        render_panel(blank, color)
        time.sleep(0.6)

    # --- Phase 4b: wave expands and reveals text ---
    label   = f"> {text} <"
    text_x  = cx - len(label) // 2

    for offset in range(cx + 2):
        lines = []
        for y in range(HEIGHT):
            row = ""
            for x in range(WIDTH):
                char = " "
                if y == cy:
                    left_edge  = cx - offset
                    right_edge = cx + offset
                    if x == left_edge or x == right_edge:
                        char = f"[bold {color}]█[/]"
                    if text_x <= x < text_x + len(label):
                        if left_edge <= x <= right_edge:
                            letter = label[x - text_x]
                            char = f"[bold {color}]{letter}[/]"
                row += char
            lines.append(row)
        render_panel(lines, color, subtitle=f"✦ 1 in {rarity} ✦")
        time.sleep(0.015)


#MARK: Epic

def epic_cutscene(color,msg,rarity):
    BLOCK = "█"
    WIDTH  = 40   # inner canvas width (Panel adds padding on top)
    HEIGHT = 10

    h1_x, h1_y = 0, 1
    h2_x, h2_y = WIDTH - 1, 8
    trail1, trail2 = [], []
    MAX_TRAIL = 20
    target_x, target_y = WIDTH // 2, HEIGHT // 2

    # ── helpers ────────────────────────────────────────────────────────────────
    def blank_grid():
        return [[" "] * WIDTH for _ in range(HEIGHT)]

    def grid_to_lines(grid):
        return ["".join(row) for row in grid]

    # ==========================================
    # PHASE 1: The Swirl
    # ==========================================
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

        grid = blank_grid()
        for (x, y) in trail1 + trail2:
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                grid[y][x] = f"[dim white]{BLOCK}[/]"
        if 0 <= h1_y < HEIGHT and 0 <= h1_x < WIDTH:
            grid[h1_y][h1_x] = f"[white]{BLOCK}[/]"
        if 0 <= h2_y < HEIGHT and 0 <= h2_x < WIDTH:
            grid[h2_y][h2_x] = f"[white]{BLOCK}[/]"

        render_panel(grid_to_lines(grid), "white")
        time.sleep(0.04)

    time.sleep(0.2)

    # ==========================================
    # PHASE 2: Fading Diamond (×2 white, ×1 colour)
    # ==========================================
    MAX_RADIUS = 5

    def draw_diamond(wave_front, diamond_color):
        grid = blank_grid()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if x == target_x and y == target_y:
                    grid[y][x] = f"[{diamond_color}]{BLOCK}[/]"
                    continue
                dist  = abs(x - target_x) + abs(y - target_y)
                if dist <= MAX_RADIUS and dist <= wave_front:
                    behind = wave_front - dist
                    if   behind <= 2: char = BLOCK
                    elif behind == 3: char = "▓"
                    elif behind == 4: char = "▒"
                    elif behind == 5: char = "░"
                    else:             char = None
                    if char:
                        grid[y][x] = f"[{diamond_color}]{char}[/]"
        return grid_to_lines(grid)

    for _ in range(2):
        time.sleep(0.5)
        for wave_front in range(1, MAX_RADIUS + 7):
            render_panel(draw_diamond(wave_front, "white"), "white")
            time.sleep(0.04)

    # Final coloured diamond
    time.sleep(0.5)
    for wave_front in range(1, MAX_RADIUS + 7):
        render_panel(draw_diamond(wave_front, color), color)
        time.sleep(0.05)

    time.sleep(0.5)

    # ==========================================
    # PHASE 3: Wave reveals text
    # ==========================================
    cx, cy = WIDTH // 2, HEIGHT // 2
    label  = f"> {msg} <"
    text_x = cx - len(label) // 2

    for offset in range(cx + 2):
        grid = blank_grid()
        for x in range(WIDTH):
            left_edge  = cx - offset
            right_edge = cx + offset

            char = None
            if x == left_edge or x == right_edge:
                char = f"[bold {color}]{BLOCK}[/]"
            if text_x <= x < text_x + len(label) and left_edge <= x <= right_edge:
                letter = label[x - text_x]
                char = f"[bold {color}]{letter}[/]"

            if char:
                grid[cy][x] = char

        render_panel(grid_to_lines(grid), color, subtitle=f"✦ 1 in {rarity} ✦")
        time.sleep(0.01)
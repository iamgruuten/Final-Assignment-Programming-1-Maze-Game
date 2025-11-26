# Maze Game (Programming 1 Python Module)

## Overview

This Python-based maze game is a terminal application with optional Raspberry Pi SenseHAT support. Mazes are 2D grids using `'A'` (start/player), `'B'` (end), `'O'` (path), and `'X'` (wall). It features toroidal wrapping (edges connect opposite sides). Load mazes from files, create/configure them, play manually or via SenseHAT, view leaderboards, and compute shortest paths with BFS. Leaderboards track times per unique maze (MD5-hashed). Emphasizes OOP with classes for maze, player, and game logic.

## Requirements

- Python 3+ (uses standard libraries: `os`, `copy`, `json`, `hashlib`, `time`, `collections.deque`).
- For SenseHAT: Install `sense-hat` via pip (requires Raspberry Pi).
- Maze files: `.txt` or `.csv` (e.g., lines like `AOX\nOXX\nOBX`).
- Leaderboard: Stored in `data.json`.

## Installation and Setup

1. Download the script.
2. Run: `python maze_game.py`.
3. Place maze files in the same directory.
4. No maze loads initially; use menu options 1 or 6.

## How to Play the Game

1. **Load/Create Maze**:
   - Option 1: Load from file (e.g., `maze.txt`).
   - Option 6: Create empty maze by dimensions (e.g., `5,5`), then configure.

2. **View/Configure**:
   - Option 2: Display maze (colored: A=red, B=green, O=., X=X).
   - Option 4: Edit cells (X/O/A/B) via coordinates; ensures one A/B.

3. **Play Manually (Option 3)**:
   - View maze; input W/A/S/D to move, M to menu.
   - Wraps edges; blocks walls; trails O.
   - Reach B to win; time-based score; add name to leaderboard.
   - Validates solvability first.

4. **SenseHAT Play (Option 7)**:
   - 8x8 mazes only; LEDs show maze (red=player, green=end, grey=wall, black=path).
   - Joystick moves; middle quits.
   - Same win/leaderboard.

5. **Advanced**:
   - Option 9: Shows BFS shortest path (move sequence, e.g., `D -> S`).
   - Option 8: Top 10 scores (name, time) for current maze.
   - Option 5: Export maze to file.

6. **Winning/Leaderboard**:
   - Fastest times rank highest; anonymous OK.
   - Persists per maze hash.

Exit with Option 0. Handles errors (e.g., invalid mazes) with prompts.

## Available Options

Main menu (0-9):

- [0] Exit.
- [1] Load maze from file (validates format).
- [2] View current maze.
- [3] Play manually.
- [4] Configure (edit submenu).
- [5] Export to file (overwrite confirm).
- [6] Create new empty maze (optional save).
- [7] SenseHAT play (hardware required).
- [8] View leaderboard.
- [9] Find BFS shortest path.

Options 2-5/7-9 need a loaded maze.

## Game Mechanics and Features

- **Maze**: Nested lists; arbitrary sizes (8x8 for SenseHAT).
- **Movement**: Toroidal; no immediate backtracks in validation.
- **Validation**: Ensures A/B/O/X only, one start/end, solvable path (BFS-like).
- **Scoring**: Elapsed seconds; JSON-stored per hash.
- **SenseHAT**: Pixel rendering; joystick input.
- **File I/O**: Load/save mazes; persistent leaderboards.
- **Shortest Path**: BFS explores levels, returns minimal moves.

Extensible: Add mazes via files/config; repeatable play.

## Design and Implementation

The code uses object-oriented design for modularity and reusability:

- **Board Class**: Manages grid operations like loading, position updates, hashing, and configuration. Includes `find_shortest_path()` with BFS (queue-based, toroidal-aware) to compute minimal move sequences from start to end.

- **Player Class**: Handles position and movement, integrating with Board for checks and updates, separating player logic from maze.

- **Game Class**: Oversees validation, play sessions (timing, wins), and BFS display. Uses Player and Board for structured flow.

- **LeaderBoard**: JSON persistence for scores per maze.
- **Rashpi**: SenseHAT rendering/controls.

Global functions manage UI (menus, I/O), delegating to classes. Main loop handles options, initializing Game post-load. BFS uses level-order traversal on unweighted graph for shortest paths, with visited tracking to prevent cycles. Design allows easy extensions like alternative algorithms.

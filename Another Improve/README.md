# README.md

# Fishing Mania

Fishing Mania is a fun and engaging fishing simulation game where players can explore different locations, catch various types of fish, and upgrade their boats. This README provides instructions on how to set up and run the game.

## Project Structure

```
IMPROVE
├── assets
│   ├── Background
│   ├── Boat
│   ├── Fish
│   ├── UI
│   └── sounds
├── main.py
├── boat.py
├── camera_system.py
├── collection.py
├── config.py
├── fish.py
├── fishing_challenge.py
├── fishing_system.py
├── game_logic_integration.py
├── game_map.py
├── game.py
├── inventory.py
├── map_explore.py
├── market.py
├── menu.py
├── player.py
├── ui.py
└── README.md
```

## Setting Up Assets

To implement your assets, follow these steps:

1. Place your image files for backgrounds, boats, fish, and UI elements in their respective folders within the `assets` directory.
2. Place your sound files in the `assets/sounds` folder.
3. Ensure that the filenames match the expected names in the code (e.g., `boat_coast.png` for the boat image if the game is set in the "Coast" location).

## Running the Game

1. Make sure you have Python installed on your machine.
2. Install Pygame using pip:

   ```
   pip install pygame
   ```

3. After setting up the assets and installing Pygame, execute `main.py` to start the game:

   ```
   python main.py
   ```

Enjoy your fishing adventure!
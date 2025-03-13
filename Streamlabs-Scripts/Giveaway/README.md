# Streamlabs Chatbot Giveaway System

A persistent giveaway system for Streamlabs Chatbot that supports multiple entries, cooldowns, and customizable settings.

## Features

- Multiple entry support with points system
- Persistent data storage between bot restarts
- Cooldown system for winners
- Unique Game ID and Discord ID validation
- Customizable messages and commands
- Live-only mode option
- Automatic winner drawing (optional)
- Entry cost system
- Command permissions system

## Commands

- `!startgiveaway` - Start a new giveaway (Moderator only)
- `!giveaway <game_id> <discord_username> [entries]` - Enter the giveaway
- `!draw` - Draw a winner (Moderator only)
- `!resetgiveaway` - Reset giveaway data (Moderator only)
- `!reloadgiveaway` - Reload giveaway settings (Moderator only)
- `!entries` - Check your current entry details
- `!updategameid <new_game_id>` - Update your game ID
- `!updatediscordid <new_discord_id>` - Update your Discord ID

## Installation

1. Download the latest release
2. Place the files in your Streamlabs Chatbot Scripts folder:
   - `Giveaway_StreamlabsSystem.py`
   - `UI_Config.json`
   - `settings.json` (will be created automatically)
   - `giveaway_data.json` (will be created automatically)

## Configuration

The script can be configured through the Streamlabs Chatbot UI or by editing `settings.json`:

### General Settings
- `liveOnly`: Only allow entries when stream is live
- `useTimer`: Automatically draw winner after 24 hours
- `entryCost`: Points required per entry
- `cooldownDays`: Days before a winner can enter again

### Commands
- `command`: Main giveaway command
- `drawCommand`: Command to draw winner
- `resetCommand`: Command to reset giveaway
- `startCommand`: Command to start giveaway
- `reloadCommand`: Command to reload settings
- `entriesCommand`: Command to check entries
- `updateGameIdCommand`: Command to update game ID
- `updateDiscordIdCommand`: Command to update Discord ID

### Permissions
- `permission`: Permission required to enter
- `drawPermission`: Permission required to draw winner
- `resetPermission`: Permission required to reset giveaway
- `startPermission`: Permission required to start giveaway

## Usage

1. Start a giveaway:
   ```
   !startgiveaway
   ```

2. Enter the giveaway:
   ```
   !giveaway abc123 JohnDoe#1234 5
   ```
   - `abc123`: Your game ID
   - `JohnDoe#1234`: Your Discord username
   - `5`: Number of entries (optional, defaults to 1)

3. Check your entries:
   ```
   !entries
   ```

4. Update your details:
   ```
   !updategameid newgame123
   !updatediscordid NewUser#5678
   ```

5. Draw a winner:
   ```
   !draw
   ```

## Data Storage

The script stores data in two files:
- `settings.json`: Contains all customizable settings
- `giveaway_data.json`: Contains giveaway participants, winners, and cooldowns

## Limitations

 **Note:** The current implementation has basic validation for Game IDs and Discord IDs:
 - Game ID validation only checks if the input is a non-empty string
 - Discord ID validation currently accepts any input
 
 These validations are placeholders and do not perform any actual format checking. You may want to implement more strict validation rules based on your specific requirements.

## Requirements

- Streamlabs Chatbot
- Python 2.7 (included with Streamlabs Chatbot)

## Support

For issues and feature requests, please create an issue on the GitHub repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
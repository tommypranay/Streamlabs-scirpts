#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division  # For Python 2.7 compatibility
import clr
import sys
import json
import os
import time
import codecs
from datetime import datetime, timedelta
import random
import copy  # For deep copying in Python 2.7

ScriptName = "Persistent Giveaway System"
Website = "http://www.github.com/randm6uy"
Description = "A persistent giveaway system with multiple entries and cooldown"
Creator = "randm6uy"
Version = "1.0.0"

configFile = "settings.json"
dataFile = "giveaway_data.json"
settings = {}
giveawayData = {
    "participants": {},
    "active": False,
    "winners": [],
    "last_draw_time": None,
    "unique_game_ids": set(),
    "unique_discord_usernames": set(),
    "cooldowns": {
        "user_ids": {},
        "game_ids": {},
        "discord_usernames": {}
    }
}

def Init():
    global settings, giveawayData
    
    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), 'r', encoding='utf-8-sig') as file:
            settings = json.load(file)
    except:
        settings = {
            "liveOnly": True,
            "useTimer": False,
            "command": "!giveaway",
            "drawCommand": "!draw",
            "resetCommand": "!resetgiveaway",
            "startCommand": "!startgiveaway",
            "reloadCommand": "!reloadgiveaway",
            "entryCost": 800,
            "cooldownDays": 30,
            "permission": "Everyone",
            "drawPermission": "Moderator",
            "resetPermission": "Moderator",
            "startPermission": "Moderator",
            "startResponse": "Giveaway started! Use $command <game_id> <discord_username> [entries] to enter! Example: $command abc123 JohnDoe#1234 5",
            "startResponse2": "Discord username is compulsory! Make sure to provide your correct Discord username when entering!",
            "entryResponse": "$user entered the giveaway with $entries entries!",
            "updateResponse": "$user updated their entries to $entries!",
            "winnerResponse": "$user won the giveaway with $entries entries!",
            "alreadyWonResponse": "$user won recently and is on cooldown until $cooldown",
            "invalidDiscordResponse": "$user Invalid Discord username format. Please provide your Discord username(unique id).",
            "invalidEntriesResponse": "$user Invalid number of entries. Please provide a valid number.",
            "insufficientPointsResponse": "$user You need $cost points to enter the giveaway. You have $points points.",
            "noParticipantsResponse": "$user No participants in the giveaway!",
            "notStartedResponse": "$user Giveaway is not active right now!",
            "noPermissionResponse": "$user You don't have permission to draw the winner!",
            "resetSuccessResponse": "$user Giveaway data has been reset successfully!",
            "resetNoPermissionResponse": "$user You don't have permission to reset the giveaway!",
            "duplicateGameIdResponse": "$user This game ID is already registered by another user!",
            "duplicateDiscordResponse": "$user This Discord username is already registered by another user!",
            "gameIdOnCooldownResponse": "$user This game ID is on cooldown until $cooldown!",
            "discordOnCooldownResponse": "$user This Discord username is on cooldown until $cooldown!",
            "firstTimeEntryResponse": "$user To enter the giveaway for the first time, use: $command <game_id> <discord_username> [entries] Example: $command abc123 JohnDoe#1234 5",
            "reloadResponse": "$user Giveaway settings reloaded successfully!",
            "updateGameIdCommand": "!updategameid",
            "updateDiscordIdCommand": "!updatediscordid",
            "noExistingEntryResponse": "$user You don't have an existing entry for this command. Use: $command <new_game_id> or $command <new_discord_id>",
            "updateGameIdSuccess": "$user Game ID updated successfully! Old ID: $oldid, New ID: $newid",
            "updateDiscordIdSuccess": "$user Discord ID updated successfully! Old ID: $oldid, New ID: $newid",
            "entriesCommand": "!entries",
            "entriesResponse": "$user has $entries entries in the giveaway. Game ID: $gameid, Discord ID: $discordid",
            "noEntryResponse": "$user You haven't entered the giveaway yet! Use $command <game_id> <discord_username> [entries] to enter."
        }
    
    try:
        with codecs.open(os.path.join(path, dataFile), 'r', encoding='utf-8-sig') as file:
            loaded_data = json.load(file)
            giveawayData = loaded_data
            giveawayData["unique_game_ids"] = set(loaded_data.get("unique_game_ids", []))
            giveawayData["unique_discord_usernames"] = set(loaded_data.get("unique_discord_usernames", []))
            giveawayData["cooldowns"] = {
                "user_ids": loaded_data.get("cooldowns", {}).get("user_ids", {}),
                "game_ids": loaded_data.get("cooldowns", {}).get("game_ids", {}),
                "discord_usernames": loaded_data.get("cooldowns", {}).get("discord_usernames", {})
            }
            if not isinstance(giveawayData.get("winners", []), list):
                giveawayData["winners"] = []
    except:
        giveawayData = {
            "participants": {},
            "active": False,
            "winners": [],
            "last_draw_time": None,
            "unique_game_ids": set(),
            "unique_discord_usernames": set(),
            "cooldowns": {
                "user_ids": {},
                "game_ids": {},
                "discord_usernames": {}
            }
        }
        SaveData()

def SaveData():
    path = os.path.dirname(__file__)
    # Use deep copy for Python 2.7 compatibility
    save_data = copy.deepcopy(giveawayData)
    save_data["unique_game_ids"] = list(giveawayData["unique_game_ids"])
    save_data["unique_discord_usernames"] = list(giveawayData["unique_discord_usernames"])
    try:
        with codecs.open(os.path.join(path, dataFile), 'w', encoding='utf-8-sig') as file:
            json.dump(save_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        Parent.Log(ScriptName, "Failed to save data: %s" % str(e))

def ParseIsoDate(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        try:
            return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None

def CleanupOldWinners():
    global giveawayData
    current_time = datetime.now()
    cooldown_delta = timedelta(days=settings["cooldownDays"])
    
    giveawayData["winners"] = [
        winner for winner in giveawayData["winners"]
        if current_time - ParseIsoDate(winner["win_time"]) < cooldown_delta
    ]

def ResetData():
    global giveawayData
    giveawayData = {
        "participants": {},
        "active": False,
        "winners": [],
        "last_draw_time": None,
        "unique_game_ids": set(),
        "unique_discord_usernames": set(),
        "cooldowns": {
            "user_ids": {},
            "game_ids": {},
            "discord_usernames": {}
        }
    }
    SaveData()

def CheckCooldown(identifier, cooldown_type):
    if identifier in giveawayData["cooldowns"][cooldown_type]:
        cooldown_end = ParseIsoDate(giveawayData["cooldowns"][cooldown_type][identifier])
        if cooldown_end and datetime.now() < cooldown_end:
            return cooldown_end
    return None

def SetCooldown(identifier, cooldown_type):
    try:
        cooldown_end = datetime.now() + timedelta(days=int(settings["cooldownDays"]))  # Ensure int conversion
        giveawayData["cooldowns"][cooldown_type][identifier] = cooldown_end.isoformat()
    except Exception as e:
        Parent.Log(ScriptName, "Failed to set cooldown: %s" % str(e))

def ValidateDiscordUsername(username):
    return True

def ValidateGameId(game_id):
    try:
        return isinstance(game_id, str) and len(game_id.strip()) > 0
    except:
        return None

def ParseEntries(param):
    try:
        entries = int(param)
        if entries < 1:
            return None
        return entries
    except:
        return None

def Execute(data):
    if not data.IsChatMessage():
        return

    command = data.GetParam(0).lower()
    username = data.UserName  # Get username once at the start
    
    if command == settings["startCommand"]:
        if not Parent.HasPermission(data.User, settings["startPermission"], ""):
            outputMessage = settings["noPermissionResponse"].replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
        if giveawayData["active"]:
            outputMessage = "$user A giveaway is already active!"
            outputMessage = outputMessage.replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
        
        giveawayData["active"] = True
        giveawayData["participants"] = {}
        giveawayData["unique_game_ids"] = set()
        giveawayData["unique_discord_usernames"] = set()
        
        startMessage1 = settings["startResponse"]
        startMessage1 = startMessage1.replace("$command", settings["command"])
        startMessage1 = startMessage1.replace("$user", username)
        Parent.SendStreamMessage(startMessage1)
        
        startMessage2 = settings["startResponse2"]
        startMessage2 = startMessage2.replace("$user", username)
        Parent.SendStreamMessage(startMessage2)
        SaveData()
        return

    if command == settings["resetCommand"]:
        if not Parent.HasPermission(data.User, settings["resetPermission"], ""):
            outputMessage = settings["resetNoPermissionResponse"].replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
        ResetData()
        outputMessage = settings["resetSuccessResponse"].replace("$user", username)
        Parent.SendStreamMessage(outputMessage)
        return

    if command == settings["drawCommand"]:
        if not Parent.HasPermission(data.User, settings["drawPermission"], ""):
            outputMessage = settings["noPermissionResponse"].replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
        if not giveawayData["active"]:
            outputMessage = settings["notStartedResponse"].replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
        DrawWinner()
        return

    if command == settings["reloadCommand"]:
        if not Parent.HasPermission(data.User, settings["startPermission"], ""):
            outputMessage = settings["noPermissionResponse"].replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
        Init()
        outputMessage = settings["reloadResponse"].replace("$user", username)
        Parent.SendStreamMessage(outputMessage)
        return

    # Handle entries command
    if command == settings["entriesCommand"].lower():
        if not giveawayData["active"]:
            outputMessage = settings["notStartedResponse"].replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        userId = data.User
        if userId not in giveawayData["participants"]:
            outputMessage = settings["noEntryResponse"].replace("$user", username)
            outputMessage = outputMessage.replace("$command", settings["command"])
            Parent.SendStreamMessage(outputMessage)
            return
            
        user_data = giveawayData["participants"][userId]
        outputMessage = settings["entriesResponse"]
        outputMessage = outputMessage.replace("$user", username)
        outputMessage = outputMessage.replace("$gameid", user_data["game_id"])
        outputMessage = outputMessage.replace("$discordid", user_data["discord_username"])
        outputMessage = outputMessage.replace("$entries", str(user_data["entries"]))
        Parent.SendStreamMessage(outputMessage)
        return

    # Handle update game ID command
    if command == settings["updateGameIdCommand"].lower():
        if not giveawayData["active"]:
            outputMessage = settings["notStartedResponse"].replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        if data.GetParamCount() != 2:
            outputMessage = "$user Invalid format! Use: " + settings["updateGameIdCommand"] + " <new_game_id>"
            outputMessage = outputMessage.replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        userId = data.User
        if userId not in giveawayData["participants"]:
            outputMessage = settings["noExistingEntryResponse"].replace("$user", username)
            outputMessage = outputMessage.replace("$command", settings["command"])
            Parent.SendStreamMessage(outputMessage)
            return
            
        new_game_id = data.GetParam(1)
        
        # Validate new game ID
        if not ValidateGameId(new_game_id):
            outputMessage = "$user Invalid game ID format. Please provide a valid game ID."
            outputMessage = outputMessage.replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        # Check if new game ID is already taken by someone else
        if new_game_id in giveawayData["unique_game_ids"] and new_game_id != giveawayData["participants"][userId]["game_id"]:
            outputMessage = settings["duplicateGameIdResponse"].replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        # Update game ID
        old_game_id = giveawayData["participants"][userId]["game_id"]
        giveawayData["unique_game_ids"].remove(old_game_id)
        giveawayData["unique_game_ids"].add(new_game_id)
        giveawayData["participants"][userId]["game_id"] = new_game_id
        SaveData()
        
        outputMessage = settings["updateGameIdSuccess"]
        outputMessage = outputMessage.replace("$user", username)
        outputMessage = outputMessage.replace("$oldid", old_game_id)
        outputMessage = outputMessage.replace("$newid", new_game_id)
        Parent.SendStreamMessage(outputMessage)
        return

    # Handle update Discord ID command
    if command == settings["updateDiscordIdCommand"].lower():
        if not giveawayData["active"]:
            outputMessage = settings["notStartedResponse"].replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        if data.GetParamCount() != 2:
            outputMessage = "$user Invalid format! Use: " + settings["updateDiscordIdCommand"] + " <new_discord_id>"
            outputMessage = outputMessage.replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        userId = data.User
        if userId not in giveawayData["participants"]:
            outputMessage = settings["noExistingEntryResponse"].replace("$user", username)
            outputMessage = outputMessage.replace("$command", settings["command"])
            Parent.SendStreamMessage(outputMessage)
            return
            
        new_discord_id = data.GetParam(1)
        
        # Validate Discord ID format
        if not ValidateDiscordUsername(new_discord_id):
            outputMessage = settings["invalidDiscordResponse"].replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        # Check if new Discord ID is already taken by someone else
        if new_discord_id in giveawayData["unique_discord_usernames"] and new_discord_id != giveawayData["participants"][userId]["discord_username"]:
            outputMessage = settings["duplicateDiscordResponse"].replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        # Update Discord ID
        old_discord_id = giveawayData["participants"][userId]["discord_username"]
        giveawayData["unique_discord_usernames"].remove(old_discord_id)
        giveawayData["unique_discord_usernames"].add(new_discord_id)
        giveawayData["participants"][userId]["discord_username"] = new_discord_id
        SaveData()
        
        outputMessage = settings["updateDiscordIdSuccess"]
        outputMessage = outputMessage.replace("$user", username)
        outputMessage = outputMessage.replace("$oldid", old_discord_id)
        outputMessage = outputMessage.replace("$newid", new_discord_id)
        Parent.SendStreamMessage(outputMessage)
        return
    
    if command != settings["command"]:
        return
        
    if not Parent.HasPermission(data.User, settings["permission"], ""):
        return
        
    if settings["liveOnly"] and not Parent.IsLive():
        return

    # Check if giveaway is active before processing any giveaway commands
    if not giveawayData["active"]:
        outputMessage = settings["notStartedResponse"].replace("$user", username)
        Parent.SendStreamMessage(outputMessage)
        return

    userId = data.User
    points = Parent.GetPoints(userId)
    outputMessage = ""

    CleanupOldWinners()

    cooldown_end = CheckCooldown(userId, "user_ids")
    if cooldown_end:
        outputMessage = settings["alreadyWonResponse"]
        outputMessage = outputMessage.replace("$user", username)
        outputMessage = outputMessage.replace("$cooldown", cooldown_end.strftime("%Y-%m-%d %H:%M:%S"))
        Parent.SendStreamMessage(outputMessage)
        return
        
    if data.GetParamCount() == 1:
        if userId not in giveawayData["participants"]:
            outputMessage = settings["firstTimeEntryResponse"]
            outputMessage = outputMessage.replace("$command", settings["command"])
            outputMessage = outputMessage.replace("$user", username)
        else:
            entries = 1
            if points >= settings["entryCost"]:
                Parent.RemovePoints(userId, username, settings["entryCost"])
                giveawayData["participants"][userId]["entries"] += entries
                outputMessage = settings["updateResponse"]
                outputMessage = outputMessage.replace("$user", username)
                outputMessage = outputMessage.replace("$entries", str(giveawayData["participants"][userId]["entries"]))
                SaveData()
            else:
                outputMessage = settings["insufficientPointsResponse"]
                outputMessage = outputMessage.replace("$cost", str(settings["entryCost"]))
                outputMessage = outputMessage.replace("$points", str(points))

    elif data.GetParamCount() == 2:
        if userId not in giveawayData["participants"]:
            outputMessage = settings["firstTimeEntryResponse"]
            outputMessage = outputMessage.replace("$command", settings["command"])
            outputMessage = outputMessage.replace("$user", username)
        else:
            entries = ParseEntries(data.GetParam(1))
            if entries is None:
                outputMessage = settings["invalidEntriesResponse"]
            else:
                total_cost = settings["entryCost"] * entries
                if points < total_cost:
                    outputMessage = settings["insufficientPointsResponse"]
                    outputMessage = outputMessage.replace("$cost", str(total_cost))
                    outputMessage = outputMessage.replace("$points", str(points))
                else:
                    Parent.RemovePoints(userId, username, total_cost)
                    giveawayData["participants"][userId]["entries"] += entries
                    outputMessage = settings["updateResponse"]
                    outputMessage = outputMessage.replace("$user", username)
                    outputMessage = outputMessage.replace("$entries", str(giveawayData["participants"][userId]["entries"]))
                    SaveData()

    elif data.GetParamCount() >= 3:
        game_id = data.GetParam(1)
        discord_username = data.GetParam(2)
        entries = 1

        if not ValidateGameId(game_id):
            outputMessage = "$user Invalid game ID format. Please provide a valid game ID."
            outputMessage = outputMessage.replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        cooldown_end = CheckCooldown(game_id, "game_ids")
        if cooldown_end:
            outputMessage = settings["gameIdOnCooldownResponse"]
            outputMessage = outputMessage.replace("$cooldown", cooldown_end.strftime("%Y-%m-%d %H:%M:%S"))
            outputMessage = outputMessage.replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        cooldown_end = CheckCooldown(discord_username, "discord_usernames")
        if cooldown_end:
            outputMessage = settings["discordOnCooldownResponse"]
            outputMessage = outputMessage.replace("$cooldown", cooldown_end.strftime("%Y-%m-%d %H:%M:%S"))
            outputMessage = outputMessage.replace("$user", username)
            Parent.SendStreamMessage(outputMessage)
            return
            
        if not ValidateDiscordUsername(discord_username):
            outputMessage = settings["invalidDiscordResponse"]
        elif game_id in giveawayData["unique_game_ids"]:
            outputMessage = settings["duplicateGameIdResponse"]
        elif discord_username in giveawayData["unique_discord_usernames"]:
            outputMessage = settings["duplicateDiscordResponse"]
        else:
            if data.GetParamCount() > 3:
                parsed_entries = ParseEntries(data.GetParam(3))
                if parsed_entries is not None:
                    entries = parsed_entries
                else:
                    outputMessage = settings["invalidEntriesResponse"]
                    outputMessage = outputMessage.replace("$user", username)
                    Parent.SendStreamMessage(outputMessage)
                    return

            total_cost = settings["entryCost"] * entries
            if points < total_cost:
                outputMessage = settings["insufficientPointsResponse"]
                outputMessage = outputMessage.replace("$cost", str(total_cost))
                outputMessage = outputMessage.replace("$points", str(points))
            else:
                Parent.RemovePoints(userId, username, total_cost)
                
                if userId in giveawayData["participants"]:
                    giveawayData["participants"][userId]["entries"] += entries
                    outputMessage = settings["updateResponse"]
                else:
                    giveawayData["participants"][userId] = {
                        "username": str(username),
                        "game_id": str(game_id),
                        "discord_username": str(discord_username),
                        "entries": int(entries),
                        "last_win": None
                    }
                    giveawayData["unique_game_ids"].add(str(game_id))
                    giveawayData["unique_discord_usernames"].add(str(discord_username))
                    outputMessage = settings["entryResponse"]
                
                outputMessage = outputMessage.replace("$user", username)
                outputMessage = outputMessage.replace("$entries", str(giveawayData["participants"][userId]["entries"]))
                SaveData()

    if outputMessage:
        outputMessage = outputMessage.replace("$user", username)
        Parent.SendStreamMessage(outputMessage)

def Tick():
    global giveawayData
    
    if not giveawayData["active"]:
        return

    CleanupOldWinners()

    if settings["useTimer"] and giveawayData["last_draw_time"]:
        last_draw = ParseIsoDate(giveawayData["last_draw_time"])
        if datetime.now() >= last_draw + timedelta(hours=24):
            DrawWinner()

def DrawWinner():
    global giveawayData
    
    if not giveawayData["participants"]:
        # Send no participants message without a username since this isn't triggered by a user
        outputMessage = settings["noParticipantsResponse"].replace("$user", "")
        Parent.SendStreamMessage(outputMessage)
        return

    total_entries = sum(user["entries"] for user in giveawayData["participants"].values())
    winner_number = random.randint(1, total_entries)
    current_sum = 0
    
    for userId, user_data in giveawayData["participants"].items():
        current_sum += user_data["entries"]
        if current_sum >= winner_number:
            winner_info = {
                "userId": userId,
                "username": user_data["username"],
                "game_id": user_data["game_id"],
                "discord_username": user_data["discord_username"],
                "entries": user_data["entries"],
                "win_time": datetime.now().isoformat()
            }
            giveawayData["winners"].append(winner_info)
            
            SetCooldown(userId, "user_ids")
            SetCooldown(user_data["game_id"], "game_ids")
            SetCooldown(user_data["discord_username"], "discord_usernames")
            
            outputMessage = settings["winnerResponse"]
            outputMessage = outputMessage.replace("$user", user_data["username"])  # Use winner's username
            outputMessage = outputMessage.replace("$entries", str(user_data["entries"]))
            Parent.SendStreamMessage(outputMessage)
            
            giveawayData["participants"] = {}
            giveawayData["unique_game_ids"] = set()
            giveawayData["unique_discord_usernames"] = set()
            giveawayData["last_draw_time"] = datetime.now().isoformat()
            SaveData()
            break

def ReloadSettings(jsonData):
    """Reload settings from UI"""
    global settings
    
    try:
        # Parse the JSON data passed from the UI
        new_settings = json.loads(jsonData)
        # Update our settings
        settings.update(new_settings)
        # Save to file
        path = os.path.dirname(__file__)
        try:
            with codecs.open(os.path.join(path, configFile), 'w', encoding='utf-8-sig') as file:
                json.dump(settings, file, indent=4, ensure_ascii=False)
            # Log success
            Parent.Log(ScriptName, "Settings reloaded successfully")
        except Exception as e:
            Parent.Log(ScriptName, "Failed to save settings: %s" % str(e))
            Init()
    except Exception as e:
        # If there's an error, fall back to Init()
        Parent.Log(ScriptName, "Failed to reload settings: %s" % str(e))
        Init() 
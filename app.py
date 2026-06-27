"""
Highrise Room Management Bot - Updated
Functionality: Emotes, Welcome Greet (No Tips), Owner Commands (!help, !withdraw)
"""

import os
import sys
import time
import random
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from json import load, dump

from highrise import BaseBot, User, Position, AnchorPosition, SessionMetadata, CurrencyItem, Item
from highrise.__main__ import main, BotDefinition

sys.stdout.reconfigure(line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"

ROOM_ID = "6a08de7555cf5fcd2c74aa26"
API_TOKEN = "9f190f784462e76e40d1039060c85e2529983407f9f0f99c16889315a7c8acd3"
DATA_FILE = "./data.json"

TIP_MAP = {
    "1g": "gold_bar_1", "5g": "gold_bar_5", "10g": "gold_bar_10", 
    "50g": "gold_bar_50", "100g": "gold_bar_100", "500g": "gold_bar_500",
    "1k": "gold_bar_1k", "5k": "gold_bar_5k", "10k": "gold_bar_10k"
}

EMOTE_MAP = {
    "rest": {"id": "sit-open", "duration": 4.5}, 
    "zombie": {"id": "idle_zombie", "duration": 5.0},
    "relaxed": {"id": "idle_layingdown2", "duration": 5.5}, 
    "attentive": {"id": "idle_layingdown", "duration": 6.0},
    "sleepy": {"id": "idle-sleep", "duration": 5.0}, 
    "poutyface": {"id": "idle-sad", "duration": 5.0},
    "posh": {"id": "idle-posh", "duration": 5.0}, 
    "tired": {"id": "idle-loop-tired", "duration": 4.5},
    "taploop": {"id": "idle-loop-tapdance", "duration": 3.5}, 
    "sit": {"id": "idle-loop-sitfloor", "duration": 5.0},
    "shy": {"id": "idle-loop-shy", "duration": 4.0}, 
    "bummed": {"id": "idle-loop-sad", "duration": 3.5},
    "chillin": {"id": "idle-loop-happy", "duration": 4.5}, 
    "annoyed": {"id": "idle-loop-annoyed", "duration": 4.0},
    "aerobics": {"id": "idle-loop-aerobics", "duration": 4.0}, 
    "ponder": {"id": "idle-lookup", "duration": 5.0},
    "heropose": {"id": "idle-hero", "duration": 4.5}, 
    "relaxing": {"id": "idle-floorsleeping2", "duration": 4.0},
    "cozynap": {"id": "idle-floorsleeping", "duration": 3.5}, 
    "enthused": {"id": "idle-enthusiastic", "duration": 4.0},
    "feelthebeat": {"id": "idle-dance-headbobbing", "duration": 5.0}, 
    "irritated": {"id": "idle-angry", "duration": 5.0},
    "fastsing": {"id": "emote-sicklycute-sing-fast", "duration": 4.0}, 
    "slowsing": {"id": "emote-sicklycute-sing-slow", "duration": 4.0},
    "yes": {"id": "emote-yes", "duration": 1.5}, 
    "ibelieveicanfly": {"id": "emote-wings", "duration": 4.5},
    "thewave": {"id": "emote-wave", "duration": 1.5}, 
    "think": {"id": "emote-think", "duration": 2.0},
    "theatrical": {"id": "emote-theatrical", "duration": 4.0}, 
    "tapdance": {"id": "emote-tapdance", "duration": 4.5},
    "superrun": {"id": "emote-superrun", "duration": 3.0}, 
    "superpunch": {"id": "emote-superpunch", "duration": 2.0},
    "sumofight": {"id": "emote-sumo", "duration": 4.0}, 
    "thumbsuck": {"id": "emote-suckthumb", "duration": 2.2},
    "splitsdrop": {"id": "emote-splitsdrop", "duration": 2.5}, 
    "snowballfight": {"id": "emote-snowball", "duration": 2.5},
    "snowangel": {"id": "emote-snowangel", "duration": 3.0}, 
    "handshake": {"id": "emote-secrethandshake", "duration": 2.0},
    "sad": {"id": "emote-sad", "duration": 2.5}, 
    "pull": {"id": "emote-ropepull", "duration": 4.0},
    "roll": {"id": "emote-roll", "duration": 2.0}, 
    "rofl": {"id": "emote-rofl", "duration": 3.0},
    "robot": {"id": "emote-robot", "duration": 4.0}, 
    "rainbow": {"id": "emote-rainbow", "duration": 1.8},
    "proposing": {"id": "emote-proposing", "duration": 2.5}, 
    "peekaboo": {"id": "emote-peekaboo", "duration": 2.0},
    "peace": {"id": "emote-peace", "duration": 2.5}, 
    "panic": {"id": "emote-panic", "duration": 1.5},
    "no": {"id": "emote-no", "duration": 1.5}, 
    "ninjarun": {"id": "emote-ninjarun", "duration": 2.5},
    "nightfever": {"id": "emote-nightfever", "duration": 2.5}, 
    "monsterfail": {"id": "emote-monster_fail", "duration": 2.5},
    "model": {"id": "emote-model", "duration": 3.0}, 
    "levelup": {"id": "emote-levelup", "duration": 3.0},
    "amused": {"id": "emote-laughing2", "duration": 2.5}, 
    "laugh": {"id": "emote-laughing", "duration": 1.5},
    "kiss": {"id": "emote-kiss", "duration": 1.2}, 
    "superkick": {"id": "emote-kicking", "duration": 2.5},
    "jump": {"id": "emote-jumpb", "duration": 2.0}, 
    "judochop": {"id": "emote-judochop", "duration": 1.2},
    "jetpack": {"id": "emote-jetpack", "duration": 5.0}, 
    "hugyourself": {"id": "emote-hugyourself", "duration": 2.5},
    "sweating": {"id": "emote-hot", "duration": 2.2}, 
    "hello": {"id": "emote-hello", "duration": 1.5},
    "harlemshake": {"id": "emote-harlemshake", "duration": 5.0}, 
    "happy": {"id": "emote-happy", "duration": 1.8},
    "handstand": {"id": "emote-handstand", "duration": 2.2}, 
    "greedyemote": {"id": "emote-greedy", "duration": 2.5},
    "moonwalk": {"id": "emote-gordonshuffle", "duration": 3.5}, 
    "ghostfloat": {"id": "emote-ghost-idle", "duration": 5.0},
    "gangnamstyle": {"id": "emote-gangnam", "duration": 3.5}, 
    "faint": {"id": "emote-fainting", "duration": 5.0},
    "clumsy": {"id": "emote-fail2", "duration": 3.0}, 
    "fall": {"id": "emote-fail1", "duration": 2.5},
    "facepalm": {"id": "emote-exasperatedb", "duration": 1.5}, 
    "exasperated": {"id": "emote-exasperated", "duration": 1.2},
    "elbowbump": {"id": "emote-elbowbump", "duration": 2.0}, 
    "disco": {"id": "emote-disco", "duration": 2.5},
    "blastoff": {"id": "emote-disappear", "duration": 3.0}, 
    "faintdrop": {"id": "emote-deathdrop", "duration": 2.0},
    "collapse": {"id": "emote-death2", "duration": 2.5}, 
    "revival": {"id": "emote-death", "duration": 3.0},
    "dab": {"id": "emote-dab", "duration": 1.5}, 
    "curtsy": {"id": "emote-curtsy", "duration": 1.2},
    "confusion": {"id": "emote-confused", "duration": 4.0}, 
    "cold": {"id": "emote-cold", "duration": 2.0},
    "charging": {"id": "emote-charging", "duration": 3.5}, 
    "bunnyhop": {"id": "emote-bunnyhop", "duration": 4.5},
    "bow": {"id": "emote-bow", "duration": 1.8}, 
    "boo": {"id": "emote-boo", "duration": 2.2},
    "homerun": {"id": "emote-baseball", "duration": 3.0}, 
    "fallingapart": {"id": "emote-apart", "duration": 2.5},
    "thumbsup": {"id": "emoji-thumbsup", "duration": 1.5}, 
    "point": {"id": "emoji-there", "duration": 1.0},
    "sneeze": {"id": "emoji-sneeze", "duration": 1.5}, 
    "smirk": {"id": "emoji-smirking", "duration": 2.5},
    "sick": {"id": "emoji-sick", "duration": 2.5}, 
    "gasp": {"id": "emoji-scared", "duration": 1.5},
    "punch": {"id": "emoji-punch", "duration": 0.8}, 
    "pray": {"id": "emoji-pray", "duration": 2.5},
    "stinky": {"id": "emoji-poop", "duration": 2.5}, 
    "naughty": {"id": "emoji-naughty", "duration": 2.2},
    "mindblown": {"id": "emoji-mind-blown", "duration": 1.2}, 
    "lying": {"id": "emoji-lying", "duration": 3.0},
    "levitate": {"id": "emoji-halo", "duration": 2.8}, 
    "fireballlunge": {"id": "emoji-hadoken", "duration": 1.5},
    "giveup": {"id": "emoji-give-up", "duration": 2.5}, 
    "tummyache": {"id": "emoji-gagging", "duration": 2.5},
    "stunned": {"id": "emoji-dizzy", "duration": 2.0}, 
    "sob": {"id": "emoji-crying", "duration": 1.8},
    "clap": {"id": "emoji-clapping", "duration": 1.0}, 
    "raisetheroof": {"id": "emoji-celebrate", "duration": 1.8},
    "arrogance": {"id": "emoji-arrogance", "duration": 3.0}, 
    "angry": {"id": "emoji-angry", "duration": 2.5},
    "voguehands": {"id": "dance-voguehands", "duration": 4.0}, 
    "savagedance": {"id": "dance-tiktok8", "duration": 4.5},
    "dontstartnow": {"id": "dance-tiktok2", "duration": 4.0}, 
    "smoothwalk": {"id": "dance-smoothwalk", "duration": 3.0},
    "ringonit": {"id": "dance-singleladies", "duration": 5.0}, 
    "letsgoshopping": {"id": "dance-shoppingcart", "duration": 2.0},
    "russian": {"id": "dance-russian", "duration": 4.0}, 
    "pennywise": {"id": "dance-pennywise", "duration": 0.8},
    "orangejuicedance": {"id": "dance-orangejustice", "duration": 3.0}, 
    "rockout": {"id": "dance-metal", "duration": 5.0},
    "macarena": {"id": "dance-macarena", "duration": 5.0}, 
    "handsintheair": {"id": "dance-handsup", "duration": 5.0},
    "duckwalk": {"id": "dance-duckwalk", "duration": 4.5}, 
    "kpopdance": {"id": "dance-blackpink", "duration": 3.5},
    "pushups": {"id": "dance-aerobics", "duration": 4.0}, 
    "hyped": {"id": "emote-hyped", "duration": 3.5},
    "jinglebell": {"id": "dance-jinglebell", "duration": 4.5}, 
    "nervous": {"id": "idle-nervous", "duration": 5.0},
    "toilet": {"id": "idle-toilet", "duration": 6.0}, 
    "attention": {"id": "emote-attention", "duration": 2.0},
    "astronaut": {"id": "emote-astronaut", "duration": 4.5}, 
    "dancezombie": {"id": "dance-zombie", "duration": 4.5}
}

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot Engine Live")
            
    def log_message(self, format, *args):
        return

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None
        self.owner_username = "xRedFox"
        self.is_initialized = False 
        self.last_command_time = {} 
        self.tip_data = {}
        self.load_database_file()
        self.active_emote_loops = {}
        self.tip_queue = asyncio.Queue()

    def load_database_file(self) -> None:
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as file:
                dump({"users": {}, "bot_position": {"x": 0, "y": 0, "z": 0, "facing": "FrontRight"}}, file)
        with open(DATA_FILE, "r") as file:
            data = load(file)
            self.tip_data = data.get("users", {})

    def save_database_file(self) -> None:
        data = {"users": self.tip_data}
        with open(DATA_FILE, "w") as file:
            dump(data, file, indent=4)

    async def loop_emote_handler(self, user_id: str, emote_id: str, duration: float) -> None:
        while True:
            if user_id not in self.active_emote_loops or self.active_emote_loops[user_id]["emote_id"] != emote_id:
                break
            await self.highrise.send_emote(emote_id, user_id)
            await asyncio.sleep(duration)
        if user_id in self.active_emote_loops and self.active_emote_loops[user_id]["emote_id"] == emote_id:
            del self.active_emote_loops[user_id]

    async def stop_user_emote(self, user_id: str) -> None:
        if user_id in self.active_emote_loops:
            del self.active_emote_loops[user_id]

    async def process_tip_queue_worker(self):
        while True:
            target_id, gold_bar_tier, username = await self.tip_queue.get()
            try:
                await self.highrise.tip_user(target_id, gold_bar_tier)
                await asyncio.sleep(1.2)
            except Exception:
                pass
            self.tip_queue.task_done()

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        self.bot_id = session_metadata.user_id
        asyncio.create_task(self.process_tip_queue_worker())

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        if user.id == self.bot_id: return
        await self.highrise.chat(f"👋 Welcome to the room @{user.username}! Type '!help' for information.")

    async def on_user_leave(self, user: User) -> None:
        await self.stop_user_emote(user.id)

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
        if isinstance(tip, CurrencyItem) and receiver.id == self.bot_id:
            if sender.id not in self.tip_data:
                self.tip_data[sender.id] = {"username": sender.username, "total_tips": 0}
            self.tip_data[sender.id]['total_tips'] += tip.amount
            await self.highrise.chat(f"Thank you @{sender.username} for the tip!")
            self.save_database_file()

    async def on_chat(self, user: User, message: str) -> None:
        await self.command_handler(user, message, "chat")

    async def command_handler(self, user: User, message: str, source: str):
        if not message or not message.strip(): return
        clean_msg = message.lower().strip()
        is_owner = (user.username.lower() == self.owner_username.lower())
        
        normalized_msg = clean_msg.replace(" ", "")
        if normalized_msg in EMOTE_MAP:
            self.active_emote_loops[user.id] = {"emote_id": EMOTE_MAP[normalized_msg]["id"]}
            asyncio.create_task(self.loop_emote_handler(user.id, EMOTE_MAP[normalized_msg]["id"], EMOTE_MAP[normalized_msg]["duration"]))
            await self.respond(user, "🎭 Looping emote!", source)
            return

        if clean_msg == "!help":
            help_text = "⚡ Commands: !list | !stop"
            if is_owner:
                help_text += " | !withdraw | !giveall | !give | !top | !bal"
            await self.respond(user, help_text, source)
            return

        elif clean_msg == "!stop":
            await self.stop_user_emote(user.id)
            return

        if not is_owner: return

        if clean_msg.startswith("!withdraw "):
            amount = clean_msg.split(" ")[1]
            if amount in TIP_MAP:
                await self.highrise.tip_user(user.id, TIP_MAP[amount])
                await self.respond(user, f"💸 Withdrawn {amount}!", source)
        
        elif clean_msg.startswith("!giveall "):
            amount = clean_msg.split(" ")[1]
            if amount in TIP_MAP:
                users = await self.highrise.get_room_users()
                for u, _ in users.content:
                    if u.id != self.bot_id:
                        await self.tip_queue.put((u.id, TIP_MAP[amount], u.username))
                await self.respond(user, f"💸 Queued {amount} for all!", source)

        elif clean_msg == "!top":
            sorted_tippers = sorted(self.tip_data.items(), key=lambda x: x[1]['total_tips'], reverse=True)[:10]
            leaderboard = "\n".join([f"{i+1}. {d['username']} ({d['total_tips']}g)" for i, (_, d) in enumerate(sorted_tippers)])
            await self.respond(user, f"Top Tippers:\n{leaderboard}", source)

        elif clean_msg == "!bal":
            wallet = await self.highrise.get_wallet()
            gold = next((c.amount for c in wallet.content if c.type == 'gold'), 0)
            await self.respond(user, f"💰 Balance: {gold}g", source)

    async def respond(self, user: User, msg: str, source: str):
        if source == "chat": await self.highrise.chat(msg)
        else: await self.highrise.send_whisper(user.id, msg)

if __name__ == "__main__":
    asyncio.run(main([BotDefinition(Bot(), ROOM_ID, API_TOKEN)]))

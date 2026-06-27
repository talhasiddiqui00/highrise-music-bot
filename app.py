"""
Highrise Minimal Management Bot
Features:
- Welcome users
- Owner-only tipping
- Emote looping
- !list
- !stop
- Render health server
"""

import os
import sys
import json
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from highrise import (
    BaseBot,
    User,
    Position,
    AnchorPosition,
    SessionMetadata,
    CurrencyItem,
    Item
)

from highrise._main_ import main, BotDefinition

sys.stdout.reconfigure(line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"

ROOM_ID = "6a08de7555cf5fcd2c74aa26"

API_TOKEN = "9f190f784462e76e40d1039060c85e2529983407f9f0f99c16889315a7c8acd3"

OWNER_USERNAME = "xRedFox"

TIP_MAP = {
    "1g": "gold_bar_1",
    "5g": "gold_bar_5",
    "10g": "gold_bar_10",
    "50g": "gold_bar_50",
    "100g": "gold_bar_100",
    "500g": "gold_bar_500",
    "1k": "gold_bar_1k",
    "5k": "gold_bar_5k",
    "10k": "gold_bar_10k",
}
class HealthCheckHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot Online")

    def log_message(self, format, *args):
        return


class Bot(BaseBot):

    def _init_(self):
        super()._init_()

        self.bot_id = None
        self.active_emote_loops = {}

    async def on_start(self, session_metadata: SessionMetadata):

        print("Bot Connected!")

        self.bot_id = session_metadata.user_id

    async def on_user_join(
        self,
        user: User,
        position: Position | AnchorPosition,
    ):

        if user.id == self.bot_id:
            return

        try:
            await self.highrise.chat(
                f"👋 Welcome @{user.username}! Enjoy your stay!"
            )
        except Exception as e:
            print(e)

    async def on_user_leave(self, user: User):

        await self.stop_user_emote(user.id)
        async def stop_user_emote(self, user_id):

        if user_id not in self.active_emote_loops:
            return

        task = self.active_emote_loops[user_id]["task"]

        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        self.active_emote_loops.pop(user_id, None)


    async def loop_emote(self, user_id, emote_id, duration):

        try:

            while True:

                if user_id not in self.active_emote_loops:
                    break

                await self.highrise.send_emote(
                    emote_id,
                    user_id
                )

                await asyncio.sleep(duration)

        except asyncio.CancelledError:
            pass

        except Exception as e:
            print(e)

        finally:
            self.active_emote_loops.pop(user_id, None)


    async def start_emote(self, user: User, emote_name: str):

        emote_name = emote_name.lower().replace(" ", "")

        if emote_name not in EMOTE_MAP:
            return False

        await self.stop_user_emote(user.id)

        emote = EMOTE_MAP[emote_name]

        task = asyncio.create_task(
            self.loop_emote(
                user.id,
                emote["id"],
                emote["duration"]
            )
        )

        self.active_emote_loops[user.id] = {
            "task": task,
            "emote_id": emote["id"]
        }

        await self.highrise.chat(
            f"🎭 @{user.username} is now using {emote_name}!"
        )

        return True

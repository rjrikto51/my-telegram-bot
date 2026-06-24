from pyrogram import Client, filters
import sqlite3
import asyncio

# আপনার API ID এবং API HASH এখানে বসান
API_ID = 1234567          # আপনার আইডিটি এখানে লিখুন
API_HASH = "আপনার_hash_এখানে_লিখুন"

# ডাটাবেজ সেটআপ
conn = sqlite3.connect("my_groups.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY)")
conn.commit()

# ইউজারবট কানেকশন
app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.command("addgroup") & filters.me)
async def add_group(client, message):
    chat_id = message.chat.id
    cursor.execute("INSERT OR IGNORE INTO groups (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    await message.reply("এই গ্রুপটি আমার মার্কেটিং লিস্টে যুক্ত হয়েছে!")

@app.on_message(filters.channel) 
async def copy_posts(client, message):
    cursor.execute("SELECT chat_id FROM groups")
    groups = cursor.fetchall()
    
    for row in groups:
        try:
            # পোস্ট কপি করছে
            await message.copy(row[0])
            # প্রতিটি পোস্টের মাঝে ২০ সেকেন্ড বিরতি
            await asyncio.sleep(20) 
        except Exception as e:
            print(f"Error: {e}")

print("ইউজারবট চালু হয়েছে...")
app.run()

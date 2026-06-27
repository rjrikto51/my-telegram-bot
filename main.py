import os
import telebot
import sqlite3
from flask import Flask
from threading import Thread

API_TOKEN = '7536008073:AAGJDOATmdzsJh7SzKI3hO8uWnmqdZPyLFo'
bot = telebot.TeleBot(API_TOKEN)

# ডাটাবেস কানেকশন
conn = sqlite3.connect('customers.db', check_same_thread=False)
cursor = conn.cursor()
# কাস্টমার টেবিল তৈরি (নাম, মোবাইল নম্বর, বর্তমান ব্যালেন্স)
cursor.execute('''CREATE TABLE IF NOT EXISTS customers 
                  (name TEXT, contact TEXT PRIMARY KEY, amount REAL)''')
conn.commit()

# ফ্লাস্ক সার্ভার (Render-এর জন্য)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"

# ১. নতুন কাস্টমার প্রোফাইল তৈরি করা
@bot.message_handler(commands=['add_customer'])
def add_customer(message):
    try:
        parts = message.text.split() # /add_customer রহিম 01711
        cursor.execute("INSERT INTO customers (name, contact, amount) VALUES (?, ?, 0)", (parts[1], parts[2]))
        conn.commit()
        bot.reply_to(message, f"সফলভাবে {parts[1]} এর প্রোফাইল তৈরি হয়েছে।")
    except:
        bot.reply_to(message, "ভুল! এভাবে লিখুন: /add_customer [নাম] [নম্বর]")

# ২. ডেইলি ব্যালেন্স বা নতুন বাকি যোগ করা
@bot.message_handler(commands=['add_due'])
def add_due(message):
    try:
        parts = message.text.split() # /add_due 01711 500
        cursor.execute("UPDATE customers SET amount = amount + ? WHERE contact = ?", (parts[2], parts[1]))
        conn.commit()
        bot.reply_to(message, "নতুন অংক যোগ করা হয়েছে।")
    except:
        bot.reply_to(message, "ভুল! এভাবে লিখুন: /add_due [নম্বর] [পরিমাণ]")

# ৩. আংশিক বা ফুল পেমেন্ট নেওয়া (বাকি কমানো)
@bot.message_handler(commands=['pay_due'])
def pay_due(message):
    try:
        parts = message.text.split() # /pay_due 01711 200
        cursor.execute("UPDATE customers SET amount = amount - ? WHERE contact = ?", (parts[2], parts[1]))
        conn.commit()
        bot.reply_to(message, "পেমেন্ট আপডেট করা হয়েছে।")
    except:
        bot.reply_to(message, "ভুল! এভাবে লিখুন: /pay_due [নম্বর] [পরিমাণ]")

# ৪. ফুল ক্লিয়ার করা (ডিলিট করা)
@bot.message_handler(commands=['clear_history'])
def clear_history(message):
    try:
        parts = message.text.split() # /clear_history 01711
        cursor.execute("DELETE FROM customers WHERE contact = ?", (parts[1],))
        conn.commit()
        bot.reply_to(message, "ঐ কাস্টমারের সব হিসাব মুছে ফেলা হয়েছে।")
    except:
        bot.reply_to(message, "ভুল! এভাবে লিখুন: /clear_history [নম্বর]")

# ৫. সব কাস্টমারের সামারি দেখা
@bot.message_handler(commands=['show_summary'])
def show_summary(message):
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    if not rows:
        bot.reply_to(message, "কোনো কাস্টমার বা হিসাব নেই।")
        return
    summary = "--- হিসাবের তালিকা ---\n" + "\n".join([f"👤 {r[0]} ({r[1]}) -> 💰 বাকি: {r[2]} টাকা" for r in rows])
    bot.reply_to(message, summary)

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()

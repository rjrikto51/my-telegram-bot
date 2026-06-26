import sqlite3
import telebot

# আপনার প্রদত্ত API টোকেন
API_TOKEN = '7536008073:AAGJDOATmdzsJh7SzKI3hO8uWnmqdZPyLFo'
bot = telebot.TeleBot(API_TOKEN)

# ডাটাবেজ কানেকশন তৈরি
conn = sqlite3.connect('customer_dues.db', check_same_thread=False)
cursor = conn.cursor()

# কাস্টমার এবং ইতিহাস টেবিল তৈরি
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT UNIQUE,
        total_due REAL DEFAULT 0.0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact TEXT,
        amount REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "আপনার বাকি হিসাবের বটটি সচল হয়েছে!\n"
        "ব্যবহারের নিয়ম:\n"
        "/add_customer [নাম] [নাম্বার] - নতুন কাস্টমার যোগ করতে\n"
        "/add_due [নাম্বার] [টাকা] - বাকি যোগ করতে\n"
        "/pay_due [নাম্বার] [টাকা] - পেমেন্ট মাইনাস করতে\n"
        "/show_summary [নাম্বার] - হিসাব দেখতে\n"
        "/clear_history [নাম্বার] - ডিউ ক্লিয়ার করতে"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['add_customer'])
def add_customer(message):
    try:
        parts = message.text.split(maxsplit=2)
        name = parts[1]
        contact = parts[2]
        cursor.execute("INSERT INTO customers (name, contact) VALUES (?, ?)", (name, contact))
        conn.commit()
        bot.reply_to(message, "নতুন কাস্টমার সফলভাবে যুক্ত হয়েছে।")
    except:
        bot.reply_to(message, "ভুল ফরম্যাট! ব্যবহার করুন: /add_customer নাম নাম্বার")

@bot.message_handler(commands=['add_due'])
def add_due(message):
    try:
        parts = message.text.split(maxsplit=2)
        contact = parts[1]
        amount = float(parts[2])
        cursor.execute("UPDATE customers SET total_due = total_due + ? WHERE contact = ?", (amount, contact))
        cursor.execute("INSERT INTO history (contact, amount) VALUES (?, ?)", (contact, amount))
        conn.commit()
        bot.reply_to(message, "বাকি যোগ করা হয়েছে।")
    except:
        bot.reply_to(message, "ব্যবহার করুন: /add_due নাম্বার টাকা")

@bot.message_handler(commands=['pay_due'])
def pay_due(message):
    try:
        parts = message.text.split(maxsplit=2)
        contact = parts[1]
        amount = float(parts[2])
        cursor.execute("UPDATE customers SET total_due = total_due - ? WHERE contact = ?", (amount, contact))
        cursor.execute("INSERT INTO history (contact, amount) VALUES (?, -?)", (contact, amount))
        conn.commit()
        bot.reply_to(message, "পেমেন্ট আপডেট করা হয়েছে।")
    except:
        bot.reply_to(message, "ব্যবহার করুন: /pay_due নাম্বার টাকা")

@bot.message_handler(commands=['show_summary'])
def show_summary(message):
    try:
        contact = message.text.split()[1]
        cursor.execute("SELECT name, total_due FROM customers WHERE contact = ?", (contact,))
        customer = cursor.fetchone()
        if customer:
            cursor.execute("SELECT amount, date FROM history WHERE contact = ?", (contact,))
            history = cursor.fetchall()
            response = f"কাস্টমার: {customer[0]}\nমোট বাকি: {customer[1]} টাকা\n\nলেনদেন ইতিহাস:\n"
            for item in history:
                response += f"{item[1]} : {item[0]} টাকা\n"
            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "কাস্টমার পাওয়া যায়নি।")
    except:
        bot.reply_to(message, "সঠিক নাম্বার দিন।")

@bot.message_handler(commands=['clear_history'])
def clear_history(message):
    try:
        contact = message.text.split()[1]
        cursor.execute("UPDATE customers SET total_due = 0.0 WHERE contact = ?", (contact,))
        cursor.execute("DELETE FROM history WHERE contact = ?", (contact,))
        conn.commit()
        bot.reply_to(message, "হিসাব ক্লিয়ার করা হয়েছে।")
    except:
        bot.reply_to(message, "সঠিক নাম্বার দিন।")

bot.infinity_polling()

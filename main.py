import os
import telebot
from flask import Flask
from threading import Thread

# আপনার নতুন টোকেনটি এখানে বসান (BotFather থেকে নতুন টোকেন নিয়ে নিন)
API_TOKEN = '7536008073:AAGJDOATmdzsJh7SzKI3hO8uWnmqdZPyLFo' 
bot = telebot.TeleBot(API_TOKEN)

# রেন্ডারে পোর্ট ধরে রাখার জন্য ওয়েব সার্ভার
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_server():
    # রেন্ডার সার্ভারের পোর্টে অ্যাপটি রান করবে
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- বটের কমান্ড লজিক ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "স্বাগতম! আমি আপনার হিসাব রাখার বট।")

@bot.message_handler(commands=['add_due'])
def add_due(message):
    bot.reply_to(message, "দয়া করে বাকি টাকার পরিমাণ ও কাস্টমারের নাম দিন।")

@bot.message_handler(commands=['pay_due'])
def pay_due(message):
    bot.reply_to(message, "পেমেন্ট কনফার্ম করার জন্য তথ্য দিন।")

@bot.message_handler(commands=['show_summary'])
def show_summary(message):
    bot.reply_to(message, "আপনার কাস্টমারদের বর্তমান হিসাবের তালিকা...")

@bot.message_handler(commands=['clear_history'])
def clear_history(message):
    bot.reply_to(message, "হিস্ট্রি ক্লিয়ার করার আগে নিশ্চিত করুন।")

# --- মূল রান প্রোগ্রাম ---

if __name__ == "__main__":
    # ওয়েব সার্ভার ব্যাকগ্রাউন্ডে চালু করা
    server_thread = Thread(target=run_server)
    server_thread.start()
    
    # বটের পোলিং শুরু করা
    print("Bot is starting...")
    bot.infinity_polling()

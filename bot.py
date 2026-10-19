#!/usr/bin/env python3
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import sqlite3
from datetime import datetime

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, joined_date TEXT, is_active INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date) VALUES (?, ?, ?, ?)', 
              (user_id, username, first_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    keyboard = [[InlineKeyboardButton("Help", callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Welcome {user.first_name}!", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands: /start /help /about /stats /broadcast")

def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found")
        return
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    print("Bot started!")
    app.run_polling()

if __name__ == '__main__':
    main()

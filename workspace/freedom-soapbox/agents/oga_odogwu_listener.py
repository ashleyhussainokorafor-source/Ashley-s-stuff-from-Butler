#!/usr/bin/env python3
"""Standalone listener for @Oga_Odogwu_bot (my_G replacement)"""
import asyncio
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = "8874988834:AAEC8PHclE6wUQaXoTzCyYWW_BT25Uv17z8"

async def handle_message(update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text or "(non-text)"
    print(f"[{chat_id}] {user.first_name}: {text[:80]}")
    await update.message.reply_text(f"✅ Odogwu received: {text}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Starting @Oga_Odogwu_bot listener (standalone)...")
    app.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()

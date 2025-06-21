import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

SHEETDB_URL = "https://sheetdb.io/api/v1/17cwkibodi8t9" 

TOKEN = os.getenv("BOT_TOKEN")
risposte = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    volontario_id = user.id
    nome = user.full_name

    # Registra l’utente su Google Sheet via SheetDB
    data = {
        "data": {
            "id": str(volontario_id),
            "nome": nome
        }
    }

    try:
        response = requests.post(SHEETDB_URL, json=data)
        if response.status_code in [200, 201]:
            await update.message.reply_text("✅ Registrazione completata. Ora riceverai le allerte.")
            print(f"Registrato: {nome} - ID: {volontario_id}")
        else:
            await update.message.reply_text("⚠️ Errore durante la registrazione. Riprova più tardi.")
            print(f"Errore registrazione: {response.text}")
    except Exception as e:
        print(f"Errore SheetDB: {e}")
        await update.message.reply_text("⚠️ Errore di connessione. Contatta l’amministratore.")

async def allerta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(SHEETDB_URL)
        json_data = response.json()
        ids = [int(entry["id"]) for entry in json_data if "id" in entry]

        global risposte
        risposte = {v: None for v in ids}

        keyboard = [[
            InlineKeyboardButton("✅ Confermo", callback_data='confermo'),
            InlineKeyboardButton("❌ Rifiuto", callback_data='rifiuto')
        ]]
        markup = InlineKeyboardMarkup(keyboard)

        for vid in ids:
            await context.bot.send_message(chat_id=vid, text="🚨 CHIAMATA URGENTE 🚨", reply_markup=markup)

    except Exception as e:
        print(f"Errore durante allerta: {e}")
        await update.message.reply_text("⚠️ Impossibile inviare l’allerta. Verifica la connessione con SheetDB.")

async def risposta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    risposte[query.from_user.id] = query.data
    await query.edit_message_text(f"Hai risposto: {query.data}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("allerta", allerta))
app.add_handler(CallbackQueryHandler(risposta))
app.run_polling()

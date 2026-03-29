import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# 🔑 CONFIG
TOKEN = "8746072080:AAEyE68WihQNX2jsq-gwm1wceUob99mW2Zc"
ADMIN_ID = 7131169808  # your Telegram user ID
CHANNEL_LINK = "https://t.me/+9ff58gDubD5iNWJk"

MPESA_NUMBER = "0798724167"
MPESA_NAME = "JASPER NYABARO"

logging.basicConfig(level=logging.INFO)

# 🧠 TEMP STORAGE
pending_payments = {}

# 🚀 START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1 Week Premium @ KES 155", callback_data="week")],
        [InlineKeyboardButton("1 Month Premium @ KES 295", callback_data="month")],
        [InlineKeyboardButton("3 Months Premium @ KES 855", callback_data="3months")],
        [InlineKeyboardButton("6 Months Premium @ KES 1655", callback_data="6months")],
        [InlineKeyboardButton("1 Year Premium @ KES 2655", callback_data="year")],
    ]

    await update.message.reply_text(
        "🔔 Hello!\n🚀 Kindly choose your preferred VIP plan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 📦 PLAN SELECTED
async def plan_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    plan = query.data

    pending_payments[user_id] = plan

    await query.edit_message_text(
        text=f"""💳 PAYMENT INSTRUCTIONS

📌 Plan: {plan.upper()}

Send money via M-Pesa:
📱 Number: {MPESA_NUMBER}
👤 Name: {MPESA_NAME}

After payment, send your M-Pesa transaction code here."""
    )

# 💬 HANDLE PAYMENT CODE
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in pending_payments:
        await update.message.reply_text("❌ Please select a plan first using /start")
        return

    # Save transaction
    pending_payments[user_id] = {
        "plan": pending_payments[user_id],
        "code": text
    }

    # Notify admin
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"""📢 NEW PAYMENT REQUEST

👤 User ID: {user_id}
📦 Plan: {pending_payments[user_id]['plan']}
💳 Code: {text}
""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ Payment submitted! Waiting for admin approval...")

# ✅ ADMIN APPROVAL
async def admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, user_id = data.split("_")
    user_id = int(user_id)

    if user_id not in pending_payments:
        await query.edit_message_text("❌ Request expired")
        return

    if action == "approve":
        await context.bot.send_message(
            chat_id=user_id,
            text=f"""✅ PAYMENT CONFIRMED!

🎉 Welcome to VIP!

👉 Join here:
{CHANNEL_LINK}
"""
        )

        await query.edit_message_text("✅ Approved")

    else:
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Payment rejected. Please try again."
        )

        await query.edit_message_text("❌ Rejected")

    del pending_payments[user_id]

# ▶️ RUN BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(plan_selected, pattern="^(week|month|3months|6months|year)$"))
app.add_handler(CallbackQueryHandler(admin_actions, pattern="^(approve|reject)_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot is running...")
app.run_polling()

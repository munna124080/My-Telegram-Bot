from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime
import json
import os

BOT_TOKEN = "8172748805:AAFvn36FUurX0jGW9ZerIsiEoTExpclKd_E"
OWNER_ID = 8196800571  # বট ওনার আইডি

user_data = {}
min_withdraw = 1.0
CAPACITY_FILE = "capacity.json"
help_link = "@help"  # ডিফল্ট help লিংক

# 📥 capacity data লোড
def load_capacity():
    if not os.path.exists(CAPACITY_FILE):
        return {}
    with open(CAPACITY_FILE, "r") as f:
        return json.load(f)

# 💾 capacity data সেভ
def save_capacity(data):
    with open(CAPACITY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ✅ /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 Welcome to Robot!\n\nWe're glad you're here! Please send your phone number starting with the country code.\nExample: +880XXXXXXXXXX"
    )

# 💰 /balance কমান্ড
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {"total": 0, "pending": 0, "verified": 0, "balance": 0}
    now = datetime.now().strftime("%H:%M:%S - %Y/%m/%d")
    data = user_data[user_id]
    msg = f"""📝 User Information

▫️ ID: {user_id}
▫️ Total Accounts: {data['total']}
▫️ Pending: {data['pending']}
▫️ Verified: {data['verified']}
▫️ Balance: {data['balance']}$

⏰ {now}"""
    await update.message.reply_text(msg)

# 💵 /withdraw কমান্ড
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {"total": 0, "pending": 0, "verified": 0, "balance": 0}
    balance = user_data[user_id]["balance"]
    if balance < min_withdraw:
        await update.message.reply_text(f"❗ Error, the minimum withdrawal amount is {min_withdraw}$")
    else:
        await update.message.reply_text("✅ Withdrawal processing...")

# 🔧 /setmin (only owner)
async def setmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("⛔ You are not allowed to use this command.")
    try:
        new_min = float(context.args[0])
        global min_withdraw
        min_withdraw = new_min
        await update.message.reply_text(f"✅ Minimum withdrawal amount updated to {min_withdraw}$")
    except:
        await update.message.reply_text("❌ Usage: /setmin 1.0")

# 📊 /cap কমান্ড
async def cap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_capacity()
    if not data:
        return await update.message.reply_text("❌ No capacity data found.")
    lines = ["📊 Current Capacity Status\n"]
    for code, info in data.items():
        lines.append(f"☎️ {code} | 💵 {info['price']} $ | ⏳ {info['time']}s")
    lines.append(f"\n🌍 Total Countries: {len(data)}")
    await update.message.reply_text("\n".join(lines))

# ➕ /setcap <code> <price> <time> (owner only)
async def setcap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("⛔ You are not allowed to use this command.")
    try:
        code = context.args[0]
        price = context.args[1]
        time = context.args[2]
        data = load_capacity()
        data[code] = {"price": price, "time": time}
        save_capacity(data)
        await update.message.reply_text(f"✅ Updated: {code} → ${price}, {time}s")
    except:
        await update.message.reply_text("❌ Usage: /setcap 880 0.25 600")

# 🆘 /help কমান্ড
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💥 The explanation required in the robot channel is at the following address:\n\n{help_link}"
    )

# ✏️ /sethelp <@channel> (owner only)
async def sethelp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("⛔ You are not allowed to use this command.")
    try:
        global help_link
        help_link = context.args[0]
        await update.message.reply_text(f"✅ Help link updated to: {help_link}")
    except:
        await update.message.reply_text("❌ Usage: /sethelp @channel_username")

# 🟢 Bot Setup
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("withdraw", withdraw))
app.add_handler(CommandHandler("setmin", setmin))
app.add_handler(CommandHandler("cap", cap))
app.add_handler(CommandHandler("setcap", setcap))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("sethelp", sethelp))

print("✅ Bot is running...")
app.run_polling()
import os
import logging
import io
import re

from PIL import Image, ImageDraw, ImageFont
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID_RAW = os.getenv("ADMIN_ID", "")
try:
    ADMIN_ID = int(ADMIN_ID_RAW) if ADMIN_ID_RAW else 0
except ValueError:
    ADMIN_ID = 0
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")

SHOP_NAME = "Jannat Makon"

NAME, PHONE, ADDRESS, CONFIRM = range(4)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

PRODUCTS = {
    "shirt": {
        "name": "Klassik futbolka",
        "price": 89000,
        "sizes": ["S", "M", "L", "XL"],
        "color": "#4A90E2",
        "description": "Kundalik kiyish uchun qulay futbolka.",
    },
    "hoodie": {
        "name": "Qora huddi",
        "price": 219000,
        "sizes": ["M", "L", "XL", "XXL"],
        "color": "#292929",
        "description": "Zamonaviy va qulay qora huddi.",
    },
    "pants": {
        "name": "Klassik shim",
        "price": 179000,
        "sizes": ["S", "M", "L", "XL"],
        "color": "#34495E",
        "description": "Kundalik va klassik uslubga mos shim.",
    },
}


def money(amount):
    return f"{amount:,}".replace(",", " ") + " so'm"


def generate_product_card(product):
    image = Image.new("RGB", (900, 520), product["color"])
    draw = ImageDraw.Draw(image)

    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        text_font = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    draw.rounded_rectangle(
        (30, 30, 870, 490),
        radius=28,
        outline="white",
        width=4,
    )

    draw.text((70, 100), SHOP_NAME, font=text_font, fill="white")
    draw.text((70, 190), product["name"], font=title_font, fill="white")
    draw.text((70, 280), money(product["price"]), font=text_font, fill="white")
    draw.text(
        (70, 350),
        "O'lchamlar: " + ", ".join(product["sizes"]),
        font=text_font,
        fill="white",
    )

    output = io.BytesIO()
    output.name = "product.jpg"
    image.save(output, format="JPEG")
    output.seek(0)
    return output


def main_menu():
    keyboard = [
        ["🛍 Katalog", "📦 Buyurtma berish"],
        ["☎️ Aloqa", "ℹ️ Biz haqimizda"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def catalog_keyboard():
    buttons = []
    for product_id, product in PRODUCTS.items():
        buttons.append([
            InlineKeyboardButton(
                f'{product["name"]} — {money(product["price"])}',
                callback_data=f"product:{product_id}",
            )
        ])
    return InlineKeyboardMarkup(buttons)


def product_keyboard(product_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🛒 Shu mahsulotni buyurtma qilish",
                callback_data=f"order:{product_id}",
            )
        ],
        [
            InlineKeyboardButton("⬅️ Katalog", callback_data="catalog")
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Assalomu alaykum!\n\n"
        f"👕 {SHOP_NAME} do'koniga xush kelibsiz!\n"
        "Bu yerdan kiyimlarni ko'rishingiz va buyurtma berishingiz mumkin.",
        reply_markup=main_menu(),
    )


async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍 Katalogdan mahsulot tanlang:",
        reply_markup=catalog_keyboard(),
    )


async def catalog_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "catalog":
        await query.message.reply_text(
            "🛍 Mahsulotlar katalogi:",
            reply_markup=catalog_keyboard(),
        )
        return

    if query.data.startswith("product:"):
        product_id = query.data.split(":", 1)[1]
        product = PRODUCTS.get(product_id)

        if not product:
            await query.message.reply_text("Mahsulot topilmadi.")
            return

        caption = (
            f"👕 {product['name']}\n\n"
            f"📝 {product['description']}\n"
            f"💰 Narxi: {money(product['price'])}\n"
            f"📏 O'lchamlar: {', '.join(product['sizes'])}"
        )

        await query.message.reply_photo(
            photo=generate_product_card(product),
            caption=caption,
            reply_markup=product_keyboard(product_id),
        )


async def begin_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("order", None)
    await update.message.reply_text(
        "Buyurtma uchun katalogdan mahsulot tanlang:",
        reply_markup=catalog_keyboard(),
    )
    return ConversationHandler.END


async def order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = query.data.split(":", 1)[1]
    product = PRODUCTS.get(product_id)

    if not product:
        await query.message.reply_text("Mahsulot topilmadi.")
        return ConversationHandler.END

    context.user_data["order"] = {
        "product_id": product_id,
        "product_name": product["name"],
        "price": product["price"],
        "size": None,
    }

    buttons = [
        [
            InlineKeyboardButton(size, callback_data=f"size:{size}")
            for size in product["sizes"]
        ],
        [
            InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_order")
        ],
    ]

    await query.message.reply_text(
        f"📏 {product['name']} uchun o'lcham tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return ConversationHandler.END


async def size_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order = context.user_data.get("order")
    if not order:
        await query.message.reply_text(
            "Buyurtma ma'lumotlari topilmadi. Qaytadan boshlang: /start"
        )
        return

    size = query.data.split(":", 1)[1]
    product = PRODUCTS[order["product_id"]]

    if size not in product["sizes"]:
        await query.message.reply_text("Bu o'lcham mavjud emas.")
        return

    order["size"] = size
    await query.message.reply_text(
        f"Tanlangan mahsulot: {order['product_name']}\n"
        f"O'lcham: {size}\n"
        f"Narx: {money(order['price'])}\n\n"
        "Ism-familiyangizni yozing:"
    )


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()

    if len(name) < 2:
        await update.message.reply_text(
            "Iltimos, ism-familiyangizni to'g'ri kiriting:"
        )
        return NAME

    context.user_data["order"]["name"] = name
    await update.message.reply_text(
        "📞 Telefon raqamingizni yuboring yoki yozing.\n"
        "Masalan: +998901234567",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()

    digits = re.sub(r"\D", "", phone)
    if len(digits) < 9:
        await update.message.reply_text(
            "Telefon raqam noto'g'ri ko'rinmoqda. Qayta kiriting:"
        )
        return PHONE

    context.user_data["order"]["phone"] = phone
    await update.message.reply_text(
        "📍 Yetkazib berish manzilingizni yozing:",
        reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
    )
    return ADDRESS


async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text.strip()
    if len(address) < 5:
        await update.message.reply_text(
            "Iltimos, manzilni batafsilroq kiriting:"
        )
        return ADDRESS

    context.user_data["order"]["address"] = address
    order = context.user_data["order"]

    summary = (
        "🧾 Buyurtmangizni tekshiring:\n\n"
        f"👕 Mahsulot: {order['product_name']}\n"
        f"📏 O'lcham: {order['size']}\n"
        f"💰 Narx: {money(order['price'])}\n"
        f"👤 Ism: {order['name']}\n"
        f"📞 Telefon: {order['phone']}\n"
        f"📍 Manzil: {order['address']}\n\n"
        "Buyurtmani tasdiqlaysizmi?"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_order"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_order"),
        ]
    ])

    await update.message.reply_text(summary, reply_markup=keyboard)
    return CONFIRM


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order = context.user_data.get("order")
    if not order:
        await query.message.reply_text("Buyurtma topilmadi. /start orqali qayta boshlang.")
        return ConversationHandler.END

    user = query.from_user
    admin_text = (
        "🛒 YANGI BUYURTMA!\n\n"
        f"👕 Mahsulot: {order['product_name']}\n"
        f"📏 O'lcham: {order['size']}\n"
        f"💰 Narx: {money(order['price'])}\n"
        f"👤 Ism: {order['name']}\n"
        f"📞 Telefon: {order['phone']}\n"
        f"📍 Manzil: {order['address']}\n"
        f"🆔 Telegram ID: {user.id}\n"
        f"🔗 Username: @{user.username or 'mavjud emas'}"
    )

    try:
        if ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
        else:
            logger.warning("ADMIN_ID sozlanmagan. Buyurtma admin chatiga yuborilmadi.")
    except Exception:
        logger.exception("Adminga buyurtma yuborilmadi.")
        await query.message.reply_text(
            "Buyurtma qabul qilindi, ammo admin bilan bog'lanishda texnik xatolik yuz berdi. Iltimos, do'kon bilan aloqaga chiqing.",
            reply_markup=main_menu(),
        )
        return ConversationHandler.END

    await query.message.reply_text(
        "✅ Buyurtmangiz qabul qilindi!\nTez orada siz bilan bog'lanamiz.\n\nJannat Makon do'konini tanlaganingiz uchun rahmat!",
        reply_markup=main_menu(),
    )

    context.user_data.pop("order", None)
    return ConversationHandler.END


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("order", None)
    await query.message.reply_text("❌ Buyurtma bekor qilindi.", reply_markup=main_menu())
    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("order", None)
    await update.message.reply_text("Buyurtma bekor qilindi.", reply_markup=main_menu())
    return ConversationHandler.END


async def contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "☎️ Jannat Makon bilan aloqa\n\n"
        f"Admin: @{ADMIN_USERNAME.lstrip('@')}\n"
        "Savollaringiz bo'lsa, admin bilan bog'laning.",
        reply_markup=main_menu(),
    )


async def about_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👕 {SHOP_NAME}\n\n"
        "Siz uchun zamonaviy va qulay kiyimlar!\n"
        "🛍 Katalogdan mahsulot tanlang.\n"
        "📦 Buyurtma bering.\n"
        "☎️ Savollar uchun admin bilan bog'laning.",
        reply_markup=main_menu(),
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Botda xatolik yuz berdi:", exc_info=context.error)


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is required.")

    app = Application.builder().token(BOT_TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(order_callback, pattern=r"^order:")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            CONFIRM: [
                CallbackQueryHandler(confirm_order, pattern=r"^confirm_order$"),
                CallbackQueryHandler(cancel_order, pattern=r"^cancel_order$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_conversation),
            MessageHandler(filters.Regex(r"^❌ Bekor qilish$"), cancel_conversation),
        ],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalog", show_catalog))
    app.add_handler(CommandHandler("cancel", cancel_conversation))
    app.add_handler(conversation)

    app.add_handler(
        CallbackQueryHandler(catalog_callback, pattern=r"^(catalog|product:)")
    )
    app.add_handler(CallbackQueryHandler(size_callback, pattern=r"^size:"))
    app.add_handler(CallbackQueryHandler(cancel_order, pattern=r"^cancel_order$"))

    app.add_handler(MessageHandler(filters.Regex(r"^🛍 Katalog$"), show_catalog))
    app.add_handler(MessageHandler(filters.Regex(r"^📦 Buyurtma berish$"), begin_order))
    app.add_handler(MessageHandler(filters.Regex(r"^☎️ Aloqa$"), contact_info))
    app.add_handler(MessageHandler(filters.Regex(r"^ℹ️ Biz haqimizda$"), about_shop))

    app.add_error_handler(error_handler)
    print(f"{SHOP_NAME} bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()

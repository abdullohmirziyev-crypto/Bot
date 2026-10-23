# Jannat Makon Telegram bot

Kiyim katalogi va buyurtma qabul qilish uchun Telegram bot. Buyurtmalar `ADMIN_ID` orqali ko'rsatilgan adminning Telegram akkauntiga yuboriladi.

## 1. BotFather orqali bot ochish

1. Telegramda `@BotFather` ni oching.
2. `/newbot` yuboring.
3. Bot nomi sifatida `Jannat Makon` yozing.
4. Username tanlang; oxiri `bot` bilan tugashi kerak, masalan `JannatMakonShopBot` (band bo'lishi mumkin).
5. BotFather bergan tokenni maxfiy saqlang. Uni hech kimga yubormang va GitHub'ga joylamang.

## 2. Telegram ID ni olish

1. Telegramda `@userinfobot` kabi ID ko'rsatuvchi botni oching.
2. `/start` yuboring va o'zingizning raqamli Telegram ID'ingizni oling.
3. Bu qiymatni `ADMIN_ID` sifatida kiriting. Botdan avval o'zingiz `/start` yuboring, aks holda bot sizga birinchi bo'lib xabar yubora olmaydi.

## 3. Windows kompyuterda ishga tushirish

1. Python 3.11 yoki undan yangi versiyasini o'rnating: https://www.python.org/downloads/
2. O'rnatishda **Add Python to PATH** belgisini yoqing.
3. ZIP faylni papkaga oching.
4. Shu papkada File Explorer manzil satriga `cmd` deb yozib Enter bosing.
5. Quyidagi buyruqlarni birma-bir bajaring:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
set BOT_TOKEN=BOTFATHER_BERGAN_TOKEN
set ADMIN_ID=TELEGRAM_RAQAMLI_ID
py bot.py
```

`BOTFATHER_BERGAN_TOKEN` va `TELEGRAM_RAQAMLI_ID` o'rniga o'zingizning qiymatlaringizni kiriting, misol matnlarini emas. Shu CMD oynasi ochiq turganida bot ishlaydi. Sinash uchun Telegramda botingizni ochib `/start` yuboring.

## 4. macOS/Linux terminalda

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export BOT_TOKEN='BOTFATHER_BERGAN_TOKEN'
export ADMIN_ID='TELEGRAM_RAQAMLI_ID'
python bot.py
```

## 5. Mahsulotlarni o'zgartirish

`bot.py` ichidagi `PRODUCTS` lug'atini tahrirlang. Har mahsulotda `name`, `price`, `sizes`, `description` bor. Narxlar so'mda butun son sifatida kiritiladi. Hozirgi katalog namuna ma'lumotlardan iborat.

## 6. 24/7 ishlatish

Botni 24/7 ishlatish uchun Python dasturini qo'llab-quvvatlaydigan doimiy ishlaydigan hostingga joylang. Hostingda `BOT_TOKEN` va `ADMIN_ID` ni environment variables/secrets bo'limida sozlang. Ishga tushirish buyrug'i: `python bot.py`. Bepul hostinglarning uyqu rejimi yoki foydalanish limitlari bo'lishi mumkin, shuning uchun 24/7 ishlash kafolatlanmasligi mumkin.

## Muhim xavfsizlik

- Bot tokenini hech kimga bermang; oshkor bo'lsa, BotFather orqali yangilang.
- Tokenni kodga yozmang va GitHub'ga joylamang.
- Bu boshlang'ich versiyada buyurtmalar ma'lumotlar bazasida saqlanmaydi; ular admin Telegramiga yuboriladi. Ishlab chiqarish uchun buyurtma tarixini saqlash, maxfiylik xabari va to'lovni tekshirish qo'shilishi tavsiya etiladi.

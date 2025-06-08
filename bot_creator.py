import os
import json
import base64
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# ━━━━━━━━━━━━━ [ إعدادات أساسية ] ━━━━━━━━━━━━━
TOKEN = os.getenv('8097983452:AAHeU42NBSWfjaOEAAHPiDNK1thYo1K4oYY')
ADMIN_IDS = [1467863908]  # قم بوضع آيديك هنا
BOT_CREATOR = "http://t.me/BotMaker1325_bot"

# قاعدة بيانات بسيطة للتخزين
try:
    with open('bot_database.json', 'r') as f:
        bot_database = json.load(f)
except:
    bot_database = {
        "users": {},
        "bots": {},
        "features": {
            "anime_converter": False,
            "xo_game": False,
            # ... جميع الميزات هنا
        }
    }

# ━━━━━━━━━━━━━ [ واجهة المستخدم ] ━━━━━━━━━━━━━
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🎮 الألعاب", callback_data='games')],
        [InlineKeyboardButton("🛠️ الأدوات", callback_data='tools')],
        [InlineKeyboardButton("🎨 التصميم", callback_data='design')],
        [InlineKeyboardButton("🤖 إنشاء بوت جديد", callback_data='create_bot')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        f"مرحباً {user.first_name}!\n"
        "أنا صانع البوتات المتكامل، يمكنني إنشاء بوت تليجرام لك بمجموعة كبيرة من الميزات.\n"
        "اختر التصنيف الذي تريده:",
        reply_markup=reply_markup
    )

# ━━━━━━━━━━━━━ [ معالجة الأزرار ] ━━━━━━━━━━━━━
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    
    if data == 'games':
        show_games_menu(query)
    elif data == 'tools':
        show_tools_menu(query)
    elif data == 'design':
        show_design_menu(query)
    elif data == 'create_bot':
        start_bot_creation(query)
    elif data.startswith('feature_'):
        toggle_feature(query, data.split('_')[1])
    elif data == 'confirm_bot':
        finalize_bot_creation(query)
    else:
        query.edit_message_text("خيار غير معروف، الرجاء المحاولة مرة أخرى.")

# ━━━━━━━━━━━━━ [ قوائم الميزات ] ━━━━━━━━━━━━━
def show_games_menu(query):
    keyboard = [
        [InlineKeyboardButton("🎲 لعبة XO", callback_data='feature_xo')],
        [InlineKeyboardButton("🎰 لعبة الروليت", callback_data='feature_roulette')],
        [InlineKeyboardButton("✂️ حجر ورقة مقص", callback_data='feature_rps')],
        [InlineKeyboardButton("🔮 البلورة السحرية", callback_data='feature_magic_ball')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("🕹️ اختر الألعاب التي تريدها في بوتك:", reply_markup=reply_markup)

def show_tools_menu(query):
    keyboard = [
        [InlineKeyboardButton("📸 تحويل الصور لأنمي", callback_data='feature_anime')],
        [InlineKeyboardButton("🔊 تحويل النص لصوت", callback_data='feature_tts')],
        [InlineKeyboardButton("📄 تحويل الصور لـ PDF", callback_data='feature_img2pdf')],
        [InlineKeyboardButton("🎵 إزالة صوت من الأغاني", callback_data='feature_remove_audio')],
        [InlineKeyboardButton("🧮 حساب العمر", callback_data='feature_age_calculator')],
        [InlineKeyboardButton("🌐 بروكسي", callback_data='feature_proxy')],
        [InlineKeyboardButton("📧 بريد مؤقت", callback_data='feature_temp_mail')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("🛠️ اختر الأدوات التي تريدها في بوتك:", reply_markup=reply_markup)

def show_design_menu(query):
    keyboard = [
        [InlineKeyboardButton("🎨 إنشاء لوجو", callback_data='feature_logo')],
        [InlineKeyboardButton("🖼️ صانع ملصقات", callback_data='feature_sticker')],
        [InlineKeyboardButton("✍️ زخرفة النصوص", callback_data='feature_text_decor')],
        [InlineKeyboardButton("📝 إنشاء منشورات", callback_data='feature_post_design')],
        [InlineKeyboardButton("©️ كتابة حقوق على الصور", callback_data='feature_watermark')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("🎨 اختر أدوات التصميم التي تريدها في بوتك:", reply_markup=reply_markup)

# ━━━━━━━━━━━━━ [ عملية إنشاء البوت ] ━━━━━━━━━━━━━
def start_bot_creation(query):
    user_id = query.from_user.id
    bot_database['users'][str(user_id)] = {"selected_features": []}
    
    keyboard = [
        [InlineKeyboardButton("🎮 الألعاب", callback_data='games')],
        [InlineKeyboardButton("🛠️ الأدوات", callback_data='tools')],
        [InlineKeyboardButton("🎨 التصميم", callback_data='design')],
        [InlineKeyboardButton("✅ تأكيد إنشاء البوت", callback_data='confirm_bot')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        "🚀 بدء إنشاء بوت جديد!\n"
        "اختر الميزات التي تريدها في بوتك من التصنيفات أدناه:",
        reply_markup=reply_markup
    )

def toggle_feature(query, feature_name):
    user_id = str(query.from_user.id)
    user_data = bot_database['users'].get(user_id, {"selected_features": []})
    
    if feature_name in user_data['selected_features']:
        user_data['selected_features'].remove(feature_name)
    else:
        user_data['selected_features'].append(feature_name)
    
    bot_database['users'][user_id] = user_data
    save_database()
    
    # تحديث الواجهة مع وضع علامة على الميزات المختارة
    selected = user_data['selected_features']
    feature_status = "✅" if feature_name in selected else "❌"
    
    if query.message.text.startswith("🕹️"):
        show_games_menu(query)
    elif query.message.text.startswith("🛠️"):
        show_tools_menu(query)
    elif query.message.text.startswith("🎨"):
        show_design_menu(query)

def finalize_bot_creation(query):
    user_id = str(query.from_user.id)
    user_data = bot_database['users'].get(user_id, {"selected_features": []})
    
    if not user_data['selected_features']:
        query.edit_message_text("⚠️ لم تختر أي ميزات! الرجاء اختيار ميزات على الأقل.")
        return
    
    # توليد كود البوت
    bot_code = generate_bot_code(user_data['selected_features'])
    
    # حفظ كود البوت
    bot_filename = f"bot_{user_id}.py"
    with open(bot_filename, 'w', encoding='utf-8') as f:
        f.write(bot_code)
    
    # إرسال ملف البوت
    with open(bot_filename, 'rb') as f:
        query.message.reply_document(
            document=f,
            caption="🎉 تم إنشاء بوتك بنجاح!\n\n"
                    "لتشغيل البوت:\n"
                    "1. احفظ هذا الملف\n"
                    "2. أنشئ بوت جديد على @BotFather واحصل على التوكن\n"
                    "3. انشر البوت على GitHub باستخدام التعليمات التالية\n\n"
                    "📚 دليل النشر:\n"
                    "https://github.com/your-repo/deployment-guide"
        )
    
    query.edit_message_text("✅ تم إنشاء بوتك بنجاح! تم إرسال ملف البوت في الدردشة.")

# ━━━━━━━━━━━━━ [ توليد كود البوت ] ━━━━━━━━━━━━━
def generate_bot_code(features):
    # القالب الأساسي للبوت
    base_code = """
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

# إعدادات البوت
TOKEN = os.getenv('BOT_TOKEN')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

{imports}

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("المساعدة", callback_data='help')],
        [InlineKeyboardButton("المطور", url='https://t.me/{dev_username}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        f"مرحباً {user.first_name}!\\nأنا بوتك المتعدد المهام.",
        reply_markup=reply_markup
    )

{feature_functions}

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    {feature_handlers}
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
""".strip()
    
    # توليد أجزاء الكود حسب الميزات المختارة
    imports = ""
    feature_functions = ""
    feature_handlers = []
    dev_username = BOT_CREATOR
    
    if 'anime' in features:
        imports += "import requests\nfrom PIL import Image\n"
        feature_functions += """
# ━━━━━━━━━━━━━ [ تحويل الصور لأنمي ] ━━━━━━━━━━━━━
def convert_to_anime(update: Update, context: CallbackContext):
    if not update.message.photo:
        update.message.reply_text("الرجاء إرسال صورة")
        return
    
    photo = update.message.photo[-1].get_file()
    photo.download('user_photo.jpg')
    
    # معالجة الصورة وتحويلها لأنمي
    update.message.reply_text("جارٍ تحويل الصورة لأنمي...")
    
    # هنا كود التحويل الفعلي
    
    update.message.reply_photo(photo=open('anime_photo.jpg', 'rb'))
"""
        feature_handlers.append("dp.add_handler(MessageHandler(Filters.photo, convert_to_anime))")
    
    if 'xo' in features:
        feature_functions += """
# ━━━━━━━━━━━━━ [ لعبة XO ] ━━━━━━━━━━━━━
xo_boards = {}

def xo_game(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    xo_boards[chat_id] = [' '] * 9
    
    keyboard = [
        [InlineKeyboardButton(" ", callback_data='xo_0'),
         InlineKeyboardButton(" ", callback_data='xo_1'),
         InlineKeyboardButton(" ", callback_data='xo_2')],
        [InlineKeyboardButton(" ", callback_data='xo_3'),
         InlineKeyboardButton(" ", callback_data='xo_4'),
         InlineKeyboardButton(" ", callback_data='xo_5')],
        [InlineKeyboardButton(" ", callback_data='xo_6'),
         InlineKeyboardButton(" ", callback_data='xo_7'),
         InlineKeyboardButton(" ", callback_data='xo_8')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('دورك: ❌', reply_markup=reply_markup)

def xo_button(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    
    if chat_id not in xo_boards:
        return
    
    index = int(data.split('_')[1])
    board = xo_boards[chat_id]
    
    if board[index] == ' ':
        board[index] = 'X'
        # هنا منطق اللعبة
        query.edit_message_text(text=f"اللعبة جارية...", reply_markup=query.message.reply_markup)
"""
        feature_handlers.append("dp.add_handler(CommandHandler('xo', xo_game))")
        feature_handlers.append("dp.add_handler(CallbackQueryHandler(xo_button, pattern='^xo_'))")
    
    # ... أضف المزيد من الميزات بنفس الطريقة
    
    # تجميع الكود النهائي
    return base_code.format(
        imports=imports,
        feature_functions=feature_functions,
        feature_handlers="\n    ".join(feature_handlers),
        dev_username=dev_username
    )

# ━━━━━━━━━━━━━ [ وظائف مساعدة ] ━━━━━━━━━━━━━
def save_database():
    with open('bot_database.json', 'w') as f:
        json.dump(bot_database, f, indent=2)

# ━━━━━━━━━━━━━ [ تشغيل البوت ] ━━━━━━━━━━━━━
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    # إضافة أوامر المساعدة للمطورين
    dp.add_handler(CommandHandler("admin", admin_panel, Filters.user(user_id=ADMIN_IDS)))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


import requests
import telebot

# رمز الوصول للبوت
TOKEN = '7761188365:AAGl-tdVAuMNfkgfWEgNovKHNXEqT3-Bsic'
bot = telebot.TeleBot(TOKEN)

# مفتاح API الخاص بـ LeakCheck
API_KEY = 'a2b67d7e2c37ee2f5946bb639c08f0c0dcb287dc'

# قائمة معرفات المستخدمين المصرح لهم
authorized_users = set()  # نستخدم مجموعة لتسهيل عمليات الإضافة والإزالة

# معرف المالك (يمكن تغييره إلى معرف المالك الحقيقي)
OWNER_ID = 6358035274

@bot.message_handler(commands=['add_user'])
def add_user(message):
    if message.from_user.id == OWNER_ID:
        try:
            parts = message.text.split()
            user_id = int(parts[1])
            authorized_users.add(user_id)
            bot.reply_to(message, f"User {user_id} added successfully.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Please provide a valid user ID to add.")
    else:
        bot.reply_to(message, "You are not authorized to add users.")

@bot.message_handler(commands=['remove_user'])
def remove_user(message):
    if message.from_user.id == OWNER_ID:
        try:
            parts = message.text.split()
            user_id = int(parts[1])
            authorized_users.discard(user_id)
            bot.reply_to(message, f"User {user_id} removed successfully.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Please provide a valid user ID to remove.")
    else:
        bot.reply_to(message, "You are not authorized to remove users.")

@bot.message_handler(commands=['Jid'])
def handle_allD_command(message):
    if message.from_user.id in authorized_users or message.from_user.id == OWNER_ID:
        try:
            parts = message.text.split()
            query = parts[1]  # البريد الإلكتروني أو اسم المستخدم
        except IndexError:
            bot.reply_to(message, "يرجى إدخال البريد الإلكتروني أو اسم المستخدم بعد الأمر.")
            return

        # إعداد الرؤوس للطلب
        headers = {
            'Accept': 'application/json',
            'X-API-Key': API_KEY
        }

        # إرسال طلب إلى LeakCheck API
        response = requests.get(f'https://leakcheck.io/api/v2/query/{query}', headers=headers)

        # التحقق من حالة الاستجابة ومعالجة البيانات
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success') and data['found'] > 0:
                    reply_message = f"🔍 نتائج البحث عن: {query}\n\n"
                    
                    for result in data['result']:
                        source = result.get('source', {})
                        source_name = source.get('name', 'Unknown')
                        breach_date = source.get('breach_date', 'None')
                        ip_address = result.get('ip', 'N/A')
                        origin = result.get('origin', 'N/A')

                        # إعداد الرسالة مع جميع الحقول الممكنة
                        result_message = (
                            f"📛 المصدر: {source_name}\n"
                            f"📅 تاريخ التسريب: {breach_date}\n"
                            f"🌐 عنوان IP: {ip_address}\n"
                            f"🌐 موقع التسريب: {origin}\n"
                            f"📧 البريد الإلكتروني: {result.get('email', 'N/A')}\n"
                            f"👤 اسم المستخدم: {result.get('username', 'N/A')}\n"
                            f"🔑 كلمة المرور: {result.get('password', 'N/A')}\n"
                            f"👥 الاسم الأول: {result.get('first_name', 'N/A')}\n"
                            f"👥 الاسم الأخير: {result.get('last_name', 'N/A')}\n"
                            f"🎂 تاريخ الميلاد: {result.get('dob', 'N/A')}\n"
                            f"🏠 العنوان: {result.get('address', 'N/A')}\n"
                            f"📦 الرمز البريدي: {result.get('zip', 'N/A')}\n"
                            f"📞 الهاتف: {result.get('phone', 'N/A')}\n"
                            f"📝 الاسم: {result.get('name', 'N/A')}\n"
                            "-----------------------------------\n\n"  # فاصلة بين التسريبات
                        )
                        reply_message += result_message
                    
                    bot.reply_to(message, reply_message)
                else:
                    bot.reply_to(message, "لم يتم العثور على شيء بخصوص هذا البحث.")
            except ValueError:
                bot.reply_to(message, "Received a non-JSON response.")
        else:
            # معالجة الأخطاء بناءً على رموز الحالة
            if response.status_code == 401:
                bot.reply_to(message, "Missing or invalid X-API-Key. Please check your API key.")
            elif response.status_code == 400:
                bot.reply_to(message, "Invalid request. Please check the query format and try again.")
            elif response.status_code == 403:
                bot.reply_to(message, "Access denied. Active plan required or limit reached.")
            elif response.status_code == 429:
                bot.reply_to(message, "Too many requests. Please try again later.")
            elif response.status_code == 422:
                bot.reply_to(message, "Could not determine search type automatically. Please specify the type.")
            else:
                bot.reply_to(message, f"Failed to connect to LeakCheck. Status code: {response.status_code}")
    else:
        bot.reply_to(message, "You are not authorized to perform this action.")

# بدء تشغيل البوت باستخدام polling
bot.polling()

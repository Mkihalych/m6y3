import telebot
from config import *
import threading
import time
import string
import os
import random
from translate import Translator
from collections import defaultdict
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from ai_logic import generate_image

bot = telebot.TeleBot(token)
user_states = {}

def create_inline_markup(buttons, row_width=2):
    markup = InlineKeyboardMarkup()
    markup.row_width = row_width
    markup.add(*buttons)
    return markup


def gen_markup_start():
    buttons = [
        InlineKeyboardButton('📋 Все команды', callback_data='show_help'),
        InlineKeyboardButton('ℹ️ Информация', callback_data='show_info'),
        InlineKeyboardButton('🎮 Игры', callback_data='games'),
        InlineKeyboardButton('🎨 ИИ генератор', callback_data='ai_image')
    ]
    return create_inline_markup(buttons)


def back_markup_start():
    buttons = [
        InlineKeyboardButton('🔙 К командам', callback_data='show_help'),
        InlineKeyboardButton('🏠 Главное меню', callback_data='back_to_menu')
    ]
    return create_inline_markup(buttons, row_width=1)

def gen_markup_comm():
    buttons = [
        InlineKeyboardButton('⏱️ Таймер', callback_data='timer'),
        InlineKeyboardButton('🌐 Переводчик', callback_data='translate'),
        InlineKeyboardButton('📊 Подсчеты', callback_data='count'),
        InlineKeyboardButton('🔐 Пароль', callback_data='gen_password'),
        InlineKeyboardButton('🎨 ИИ генератор', callback_data='ai_image'),
        InlineKeyboardButton('🎮 Игры', callback_data='games'),
        InlineKeyboardButton('🏠 Главное меню', callback_data='back_to_menu')
    ]
    return create_inline_markup(buttons, row_width=2)

def gen_markup_after_image():
    buttons = [
        InlineKeyboardButton('🎨 Сгенерировать ещё', callback_data='ai_image'),
        InlineKeyboardButton('🔙 К командам', callback_data='show_help'),
        InlineKeyboardButton('🏠 Главное меню', callback_data='back_to_menu')
    ]
    return create_inline_markup(buttons, row_width=2)

def gen_markup_text_ct():
    buttons = [
        InlineKeyboardButton('🔤 Символы', callback_data='count_symbols'),
        InlineKeyboardButton('📝 Слова', callback_data='count_words'),
        InlineKeyboardButton('🔙 Назад', callback_data='show_help')
    ]
    return create_inline_markup(buttons, row_width=2)


def gen_markup_games():
    buttons = [
        InlineKeyboardButton('🎲 Кубик d6', callback_data='cl_d6'),
        InlineKeyboardButton('🎲 Другие кубики', callback_data='all_dice'),
        InlineKeyboardButton('🪙 Монетка', callback_data='cl_coin'),
        InlineKeyboardButton('🔙 Назад', callback_data='show_help')
    ]
    return create_inline_markup(buttons, row_width=2)

def gen_markup_roll_dice_all():
    buttons = [
        InlineKeyboardButton('d4', callback_data='cl_d4'),
        InlineKeyboardButton('d6', callback_data='cl_d6'),
        InlineKeyboardButton('d8', callback_data='cl_d8'),
        InlineKeyboardButton('d10', callback_data='cl_d10'),
        InlineKeyboardButton('d12', callback_data='cl_d12'),
        InlineKeyboardButton('d20', callback_data='cl_d20'),
        InlineKeyboardButton('d100', callback_data='cl_d100'),
        InlineKeyboardButton('🔙 Назад', callback_data='games')
    ]
    return create_inline_markup(buttons, row_width=3)


def gen_markup_for_text():
    buttons = [
        InlineKeyboardButton('🇬🇧 Английский', callback_data='to_en'),
        InlineKeyboardButton('🇷🇺 Русский', callback_data='to_ru'),
        InlineKeyboardButton('🇩🇪 Немецкий', callback_data='to_de'),
        InlineKeyboardButton('🇫🇷 Французский', callback_data='to_fr'),
        InlineKeyboardButton('🔙 Отмена', callback_data='show_help')
    ]
    return create_inline_markup(buttons, row_width=2)

# Кнопки после перевода
def gen_markup_continue_or_exit():
    buttons = [
        InlineKeyboardButton('🔄 Ещё перевод', callback_data='continue_translate'),
        InlineKeyboardButton('🔙 К командам', callback_data='show_help')
    ]
    return create_inline_markup(buttons, row_width=1)

# Функции для создания кнопок кубиков
def create_dice_end_markup(dice_callback):
    buttons = [
        InlineKeyboardButton('🎲 Ещё раз', callback_data=dice_callback),
        InlineKeyboardButton('🎮 К играм', callback_data='games'),
        InlineKeyboardButton('🔙 К командам', callback_data='show_help')
    ]
    return create_inline_markup(buttons, row_width=1)

def end_roll_dice_d4():
    return create_dice_end_markup('cl_d4')

def end_roll_dice_d6():
    return create_dice_end_markup('cl_d6')

def end_roll_dice_d8():
    return create_dice_end_markup('cl_d8')

def end_roll_dice_d10():
    return create_dice_end_markup('cl_d10')

def end_roll_dice_d12():
    return create_dice_end_markup('cl_d12')

def end_roll_dice_d20():
    return create_dice_end_markup('cl_d20')

def end_roll_dice_d100():
    return create_dice_end_markup('cl_d100')

def markup_coin_end():
    buttons = [
        InlineKeyboardButton('🪙 Ещё раз', callback_data='cl_coin'),
        InlineKeyboardButton('🎮 К играм', callback_data='games'),
        InlineKeyboardButton('🔙 К командам', callback_data='show_help')
    ]
    return create_inline_markup(buttons, row_width=1)

def gen_markup_end_password():
    buttons = [
        InlineKeyboardButton('🔐 Ещё пароль', callback_data='gen_password'),
        InlineKeyboardButton('🔙 К командам', callback_data='show_help')
    ]
    return create_inline_markup(buttons, row_width=1)

def gen_markup_stop_timer():
    """Клавиатура для остановки таймера"""
    buttons = [
        InlineKeyboardButton('🛑 Остановить таймер', callback_data='stop_timer'),
        InlineKeyboardButton('🔙 К командам', callback_data='show_help')
    ]
    return create_inline_markup(buttons, row_width=1)

def gen_markup_end_timer():
    """Клавиатура после завершения таймера"""
    buttons = [
        InlineKeyboardButton('⏱️ Ещё раз', callback_data='timer'),
        InlineKeyboardButton('🔙 К командам', callback_data='show_help')
    ]
    return create_inline_markup(buttons, row_width=1)


def safe_edit_message(bot, chat_id, message_id, text, reply_markup=None, parse_mode=None):
    """Безопасное редактирование сообщения с обработкой ошибок"""
    try:
        bot.edit_message_text(
            text, 
            chat_id=chat_id, 
            message_id=message_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        return True
    except Exception as e:
        if "message is not modified" in str(e):

            return True
        elif "there is no text" in str(e) or "message to edit" in str(e):

            bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
            return True
        else:
            print(f"Ошибка редактирования: {e}")
            return False

# ======================
# генерация изображений
# ======================
def generate_image_handler(message, prompt):
    """Обработчик генерации изображения"""
    try:

        bot.send_chat_action(message.chat.id, 'typing')
        

        status_msg = bot.send_message(
            message.chat.id, 
            "🎨 Генерирую изображение по запросу:\n"
            f"`{prompt[:100]}`\n\n"
            "⏳ Процесс может занять до 30 секунд...",
            parse_mode="Markdown"
        )
        

        bot.send_chat_action(message.chat.id, 'upload_photo')
        

        image_path = generate_image(prompt, "images/generate_image.png")

        try:
            bot.delete_message(message.chat.id, status_msg.message_id)
        except:
            pass
        

        with open(image_path, "rb") as image:
            bot.send_photo(
                message.chat.id, 
                image,
                caption=f"🎨 **Сгенерировано по запросу:**\n_{prompt[:200]}_\n\n✨ Хотите еще? Нажмите на кнопку ниже!",
                parse_mode="Markdown",
                reply_markup=gen_markup_after_image()
            )
        

        try:
            os.remove(image_path)
        except:
            pass
        
    except Exception as e:
        error_msg = f"❌ **Ошибка генерации:**\n```\n{str(e)}```\n\nПопробуйте изменить запрос или повторить позже."
        try:
            bot.edit_message_text(
                error_msg,
                message.chat.id,
                status_msg.message_id,
                parse_mode="Markdown",
                reply_markup=gen_markup_after_image()
            )
        except:
            bot.send_message(
                message.chat.id,
                error_msg,
                parse_mode="Markdown",
                reply_markup=gen_markup_after_image()
            )

@bot.message_handler(commands=['generate', 'image', 'ai'])
def image_generate_command(message):
    """Обработчик команды /generate"""
    prompt = message.text.replace('/generate', '', 1).replace('/image', '', 1).replace('/ai', '', 1).strip()
    
    if prompt:
        generate_image_handler(message, prompt)
    else:
        bot.reply_to(
            message,
            "🎨 **ИИ Генератор изображений**\n\n"
            "Просто опишите что вы хотите увидеть.\n\n"
            "**Примеры запросов:**\n"
            "• `/generate красивый закат на море`\n"
            "• `/generate кот в космосе`\n"
            "• `/generate cyberpunk city neon lights`\n\n"
            "Или просто напишите описание в ответ на это сообщение.",
            parse_mode="Markdown",
            reply_markup=gen_markup_after_image()
        )
        user_states[message.chat.id] = 'waiting_image_prompt'

# ======================
# Таймер
# ======================

timer_events = {}

def start_timer(seconds, chat_id, bot, stop_markup=None, end_markup=None):
    """
    Запускает таймер
    stop_markup - клавиатура для кнопки остановки
    end_markup - клавиатура для завершения таймера
    """
    stop_event = threading.Event()
    timer_events[chat_id] = stop_event

    def timer_thread():
        if stop_markup:
            msg = bot.send_message(chat_id, f'⏱️ Таймер на {seconds} секунд запущен', reply_markup=stop_markup)
        else:
            msg = bot.send_message(chat_id, f'⏱️ Таймер на {seconds} секунд запущен')
        

        threading.Timer(seconds, lambda: bot.delete_message(chat_id, msg.message_id)).start()
        

        for i in range(seconds):
            if stop_event.is_set():
                return
            time.sleep(1)

        if end_markup:
            bot.send_message(chat_id, f'⏰ Таймер на {seconds} секунд завершился!', reply_markup=end_markup)
        else:
            bot.send_message(chat_id, f'⏰ Таймер на {seconds} секунд завершился!')
        
        timer_events.pop(chat_id, None)

    threading.Thread(target=timer_thread).start()

def stop_timer(chat_id):
    """Останавливает таймер"""
    event = timer_events.get(chat_id)
    if event:
        event.set()
        timer_events.pop(chat_id, None)
        return True
    return False

# ======================
# Анализ текста и перевод
# ======================

class TextAnalysis():
    memory = defaultdict(list)

    def __init__(self, text, owner):
        TextAnalysis.memory[owner].append(self)
        self.text = text
        self.translation = self.__translate(self.text, "ru", "en")
        self.translation_ru = self.__translate(self.text, "en", "ru")
        self.translation_de = self.__translate(self.text, "ru", "de")
        self.translation_fr = self.__translate(self.text, "ru", "fr")

    def __translate(self, text, from_lang, to_lang):
        try:
            translator = Translator(from_lang=from_lang, to_lang=to_lang)
            return f"⭐ Перевод: {translator.translate(text)}"
        except Exception as e:
            print(f"Ошибка перевода: {e}")
            return "❌ Перевод не удался"

# ======================
# Генерация пароля
# ======================

def generate_password(length=12, include_upper=True, include_lower=True, include_digits=True, include_special=False):
    """Генерирует случайный пароль заданной длины"""
    if length < 4:
        length = 4 
    
    characters = []
    
    if include_upper:
        characters += list(string.ascii_uppercase)
    if include_lower:
        characters += list(string.ascii_lowercase)
    if include_digits:
        characters += list(string.digits)
    if include_special:
        characters += list(string.punctuation)
    
    if not characters:
        characters = list(string.ascii_letters + string.digits)
    
    password_chars = []
    
    if include_upper:
        password_chars.append(random.choice(string.ascii_uppercase))
    if include_lower:
        password_chars.append(random.choice(string.ascii_lowercase))
    if include_digits:
        password_chars.append(random.choice(string.digits))
    if include_special:
        password_chars.append(random.choice(string.punctuation))
    
    while len(password_chars) < length:
        password_chars.append(random.choice(characters))
    

    random.shuffle(password_chars)
    
    return ''.join(password_chars)

# ======================
# Статистика текста
# ======================

def count_words(text):
    """Подсчитывает количество слов в тексте"""
    words = text.split()
    return len(words)

def count_symbols(text):
    """Подсчитывает количество символов без пробелов"""
    return len(text.replace(" ", ""))

# ======================
# Логика кубиков
# ======================

def logic_d4():
    return random.randint(1, 4)

def logic_d6():
    return random.randint(1, 6)

def logic_d8():
    return random.randint(1, 8)

def logic_d10():
    return random.randint(1, 10)

def logic_d12():
    return random.randint(1, 12)

def logic_d20():
    return random.randint(1, 20)

def logic_d100():
    return random.randint(1, 100)

def coin():
    """Подбрасывает монетку"""
    return random.choice(["Орел", "Решка"])


# ==================== CALLBACK HANDLER ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        # ==================== НАВИГАЦИЯ ====================
        if call.data == "show_help":
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                "📋 Вот все команды:",
                reply_markup=gen_markup_comm()
            )
        
        elif call.data == "show_info":
            info_text = """
ℹ️ **MultiToolBot v1.1**
Многофункциональный бот с 15+ полезными функциями.

**Функции:**
✅ Таймер 
✅ Переводчик (en/ru/de/fr)
✅ Подсчет слов и символов
✅ Генератор паролей
✅ **ИИ Генератор изображений** 🆕
✅ Игры (кубики, монетка)

Используйте кнопки или команды для управления! /help
"""
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                info_text,
                reply_markup=back_markup_start(),
                parse_mode="Markdown"
            )
        
        elif call.data == "back_to_menu":
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                "🤖 MultiToolBot\n\nВыберите действие:",
                reply_markup=gen_markup_start()
            )
        
        # ==================== ИИ ГЕНЕРАТОР ====================
        elif call.data == "ai_image":
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                "🎨 **ИИ Генератор изображений**\n\n"
                "Отправьте текстовое описание того, что хотите увидеть.\n\n"
                "**Примеры:**\n"
                "• красивый закат на море\n"
                "• кот в космическом скафандре\n"
                "• cyberpunk city at night\n\n"
                "Чем подробнее описание, тем лучше результат!",
                parse_mode="Markdown"
            )
            user_states[call.message.chat.id] = 'waiting_image_prompt'
        
        # ==================== ИГРЫ ====================
        elif call.data == "games":
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                "🎮 Выберите игру:",
                reply_markup=gen_markup_games()
            )
        
        elif call.data == "all_dice":
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                "🎲 Выберите кубик:",
                reply_markup=gen_markup_roll_dice_all()
            )
        
        # ==================== КУБИКИ ====================
        elif call.data == "cl_d4":
            try:
                safe_edit_message(
                    bot, call.message.chat.id, call.message.message_id,
                    f"🎲 {logic_d4()}",
                    reply_markup=end_roll_dice_d4()
                )
            except:
                bot.send_message(call.message.chat.id, f"🎲 {logic_d4()}", reply_markup=end_roll_dice_d4())
        
        elif call.data == "cl_d6":
            try:
                safe_edit_message(
                    bot, call.message.chat.id, call.message.message_id,
                    f"🎲 {logic_d6()}",
                    reply_markup=end_roll_dice_d6()
                )
            except:
                bot.send_message(call.message.chat.id, f"🎲 {logic_d6()}", reply_markup=end_roll_dice_d6())
        
        elif call.data == "cl_d8":
            try:
                safe_edit_message(
                    bot, call.message.chat.id, call.message.message_id,
                    f"🎲 {logic_d8()}",
                    reply_markup=end_roll_dice_d8()
                )
            except:
                bot.send_message(call.message.chat.id, f"🎲 {logic_d8()}", reply_markup=end_roll_dice_d8())
        
        elif call.data == "cl_d10":
            try:
                safe_edit_message(
                    bot, call.message.chat.id, call.message.message_id,
                    f"🎲 {logic_d10()}",
                    reply_markup=end_roll_dice_d10()
                )
            except:
                bot.send_message(call.message.chat.id, f"🎲 {logic_d10()}", reply_markup=end_roll_dice_d10())
        
        elif call.data == "cl_d12":
            try:
                safe_edit_message(
                    bot, call.message.chat.id, call.message.message_id,
                    f"🎲 {logic_d12()}",
                    reply_markup=end_roll_dice_d12()
                )
            except:
                bot.send_message(call.message.chat.id, f"🎲 {logic_d12()}", reply_markup=end_roll_dice_d12())
        
        elif call.data == "cl_d20":
            try:
                safe_edit_message(
                    bot, call.message.chat.id, call.message.message_id,
                    f"🎲 {logic_d20()}",
                    reply_markup=end_roll_dice_d20()
                )
            except:
                bot.send_message(call.message.chat.id, f"🎲 {logic_d20()}", reply_markup=end_roll_dice_d20())
        
        elif call.data == "cl_d100":
            try:
                safe_edit_message(
                    bot, call.message.chat.id, call.message.message_id,
                    f"🎲 {logic_d100()}",
                    reply_markup=end_roll_dice_d100()
                )
            except:
                bot.send_message(call.message.chat.id, f"🎲 {logic_d100()}", reply_markup=end_roll_dice_d100())
        
        # ==================== МОНЕТКА ====================
        elif call.data == "cl_coin":
            bot.send_message(
                call.message.chat.id,
                f"🪙 Выпало: {coin()}",
                reply_markup=markup_coin_end()
            )
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
        
        # ==================== ТАЙМЕР ====================
        elif call.data == "timer":
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                "⏱️ Пожалуйста, введите число секунд (например: 15):"
            )
            user_states[call.message.chat.id] = 'waiting_timer'
        
        elif call.data == "stop_timer":
            stop_timer(call.message.chat.id)
            bot.send_message(
                call.message.chat.id,
                "🛑 Таймер остановлен!",
                reply_markup=back_markup_start()
            )
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
        
        # ==================== ПЕРЕВОДЧИК ====================
        elif call.data == "translate":
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                "🌐 Пожалуйста, введите текст для перевода:"
            )
            user_states[call.message.chat.id] = 'waiting_translate'
        
        elif call.data == "to_en":
            if call.from_user.id in TextAnalysis.memory and TextAnalysis.memory[call.from_user.id]:
                obj = TextAnalysis.memory[call.from_user.id][-1]
                bot.send_message(
                    call.message.chat.id,
                    f"🇬🇧 {obj.translation}",
                    reply_markup=gen_markup_continue_or_exit()
                )
            else:
                bot.send_message(call.message.chat.id, "❌ Сначала введите текст для перевода.")
        
        elif call.data == "to_ru":
            if call.from_user.id in TextAnalysis.memory and TextAnalysis.memory[call.from_user.id]:
                obj = TextAnalysis.memory[call.from_user.id][-1]
                bot.send_message(
                    call.message.chat.id,
                    f"🇷🇺 {obj.translation_ru}",
                    reply_markup=gen_markup_continue_or_exit()
                )
            else:
                bot.send_message(call.message.chat.id, "❌ Сначала введите текст для перевода.")
        
        elif call.data == "to_de":
            if call.from_user.id in TextAnalysis.memory and TextAnalysis.memory[call.from_user.id]:
                obj = TextAnalysis.memory[call.from_user.id][-1]
                bot.send_message(
                    call.message.chat.id,
                    f"🇩🇪 {obj.translation_de}",
                    reply_markup=gen_markup_continue_or_exit()
                )
            else:
                bot.send_message(call.message.chat.id, "❌ Сначала введите текст для перевода.")
        
        elif call.data == "to_fr":
            if call.from_user.id in TextAnalysis.memory and TextAnalysis.memory[call.from_user.id]:
                obj = TextAnalysis.memory[call.from_user.id][-1]
                bot.send_message(
                    call.message.chat.id,
                    f"🇫🇷 {obj.translation_fr}",
                    reply_markup=gen_markup_continue_or_exit()
                )
            else:
                bot.send_message(call.message.chat.id, "❌ Сначала введите текст для перевода.")
        
        # ==================== ПОДСЧЕТЫ ====================
        elif call.data == "count":
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                "📊 Что посчитать?",
                reply_markup=gen_markup_text_ct()
            )
        
        elif call.data == "count_words":
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                "📝 Отправьте текст для подсчета слов:"
            )
            user_states[call.message.chat.id] = 'waiting_count_words'
        
        elif call.data == "count_symbols":
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                "🔤 Отправьте текст для подсчета символов:"
            )
            user_states[call.message.chat.id] = 'waiting_count_symbols'
        
        # ==================== ГЕНЕРАТОР ПАРОЛЯ ====================
        elif call.data == "gen_password":
            safe_edit_message(
                bot, call.message.chat.id, call.message.message_id,
                "🔐 Введите длину пароля (например: 12):"
            )
            user_states[call.message.chat.id] = 'waiting_gen_password'
        
        # ==================== КНОПКИ ПРОДОЛЖЕНИЯ ====================
        elif call.data == "continue_translate":
            bot.send_message(call.message.chat.id, "🌐 Введите следующий текст для перевода:")
            user_states[call.message.chat.id] = 'waiting_translate'
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
        
        bot.answer_callback_query(call.id)
    
    except Exception as e:
        print(f"Ошибка в callback: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка", show_alert=False)

# ==================== КОМАНДЫ ====================

# Главное меню
@bot.message_handler(commands=['start', 'menu'])
def start(message):
    bot.reply_to(message, "🤖 MultiToolBot\n\nВыберите действие:", reply_markup=gen_markup_start())

# Справка по командам
@bot.message_handler(commands=['help', 'commands'])
def show_commands(message):
    commands_text = """
📋 **Доступные команды:**

/start - Главное меню
/help - Показать это сообщение
/info - Информация о боте

⏱️ **Утилиты:**
/timer [секунд] - Установить таймер
/translate [текст] - Перевести текст
/wordcount [текст] - Подсчитать слова
/symbolcount [текст] - Подсчитать символы
/password [длина] - Сгенерировать пароль

🎨 **ИИ Функции:**
/generate [описание] - Сгенерировать изображение

🎮 **Игры и развлечения:**
/games - Меню игр
/roll - Бросить кубик d6
/coin - Подбросить монетку
"""
    bot.reply_to(message, commands_text, parse_mode="Markdown")

# Информация о боте
@bot.message_handler(commands=['info', 'about'])
def show_info(message):
    info_text = """
ℹ️ **MultiToolBot v1.1**

Многофункциональный бот с 15+ полезными функциями.

**Функции:**
✅ Таймер
✅ Переводчик (en/ru/de/fr)
✅ Подсчет слов и символов
✅ Генератор паролей
✅ **ИИ Генератор изображений** 🆕
✅ Игры (кубики, монетка)

Используйте кнопки или команды для управления! /help
"""
    bot.reply_to(message, info_text, parse_mode="Markdown")

# Таймер
@bot.message_handler(commands=['timer'])
def timer_command(message):
    try:
        parts = message.text.split()
        if len(parts) > 1:
            seconds = int(parts[1])
            start_timer(seconds, message.chat.id, bot)
        else:
            bot.reply_to(message, "Пожалуйста, введите число секунд:")
            user_states[message.chat.id] = 'waiting_timer'
    except ValueError:
        bot.reply_to(message, "❌ Введите число секунд (например: /timer 30)")

# Переводчик
@bot.message_handler(commands=['translate'])
def translate_command(message):
    text = message.text.replace('/translate', '', 1).strip()
    if text:
        TextAnalysis(text, message.from_user.id)
        bot.reply_to(message, "На какой язык переводим?", reply_markup=gen_markup_for_text())
    else:
        bot.reply_to(message, "Введите текст для перевода:")
        user_states[message.chat.id] = 'waiting_translate'

# Подсчет слов
@bot.message_handler(commands=['wordcount'])
def wordcount_command(message):
    text = message.text.replace('/wordcount', '', 1).strip()
    if text:
        count = count_words(text)
        bot.reply_to(message, f"📊 Количество слов: {count}", reply_markup=back_markup_start())
    else:
        bot.reply_to(message, "Введите текст для подсчета слов:")
        user_states[message.chat.id] = 'waiting_count_words'

# Подсчет символов
@bot.message_handler(commands=['symbolcount'])
def symbolcount_command(message):
    text = message.text.replace('/symbolcount', '', 1).strip()
    if text:
        count = count_symbols(text)
        bot.reply_to(message, f"📊 Количество символов (без пробелов): {count}", reply_markup=back_markup_start())
    else:
        bot.reply_to(message, "Введите текст для подсчета символов:")
        user_states[message.chat.id] = 'waiting_count_symbols'

# Генератор пароля
@bot.message_handler(commands=['password'])
def password_command(message):
    try:
        parts = message.text.split()
        if len(parts) > 1:
            length = int(parts[1])
            password = generate_password(length)
            bot.reply_to(message, f"🔐 Ваш пароль: `{password}`", parse_mode="Markdown", reply_markup=gen_markup_end_password())
        else:
            bot.reply_to(message, "Введите длину пароля:")
            user_states[message.chat.id] = 'waiting_gen_password'
    except ValueError:
        bot.reply_to(message, "❌ Введите число (например: /password 12)")

# Меню игр
@bot.message_handler(commands=['games'])
def games_command(message):
    bot.reply_to(message, "🎮 Выберите игру:", reply_markup=gen_markup_games())

# Кубики
@bot.message_handler(commands=['roll', 'dice'])
def roll_command(message):
    parts = message.text.lower().split()
    if len(parts) > 1:
        dice_type = parts[1]
        if dice_type == 'd4':
            bot.reply_to(message, f"🎲 {logic_d4()}", reply_markup=end_roll_dice_d4())
        elif dice_type == 'd6':
            bot.reply_to(message, f"🎲 {logic_d6()}", reply_markup=end_roll_dice_d6())
        elif dice_type == 'd8':
            bot.reply_to(message, f"🎲 {logic_d8()}", reply_markup=end_roll_dice_d8())
        elif dice_type == 'd10':
            bot.reply_to(message, f"🎲 {logic_d10()}", reply_markup=end_roll_dice_d10())
        elif dice_type == 'd12':
            bot.reply_to(message, f"🎲 {logic_d12()}", reply_markup=end_roll_dice_d12())
        elif dice_type == 'd20':
            bot.reply_to(message, f"🎲 {logic_d20()}", reply_markup=end_roll_dice_d20())
        elif dice_type == 'd100':
            bot.reply_to(message, f"🎲 {logic_d100()}", reply_markup=end_roll_dice_d100())
        else:
            bot.reply_to(message, "Неизвестный тип кубика. Используйте: d4, d6, d8, d10, d12, d20, d100")
    else:
        bot.reply_to(message, f"🎲 {logic_d6()}", reply_markup=end_roll_dice_d6())

@bot.message_handler(commands=['coin'])
def coin_command(message):
    bot.reply_to(message, f"🪙 Выпало: {coin()}", reply_markup=markup_coin_end())

# ==================== ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ ====================
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    state = user_states.get(message.chat.id)
    

    if state == 'waiting_image_prompt':
        if message.text and not message.text.startswith('/'):
            generate_image_handler(message, message.text)
            user_states.pop(message.chat.id, None)
        else:
            bot.reply_to(message, "❌ Пожалуйста, отправьте текстовое описание изображения")
        return

    if state == 'waiting_timer':
        try:
            sec = int(message.text)
            start_timer(sec, message.chat.id, bot,
                       stop_markup=gen_markup_stop_timer(),
                       end_markup=gen_markup_end_timer())
            user_states.pop(message.chat.id, None)
        except ValueError:
            bot.reply_to(message, '❌ Введите ЧИСЛО секунд (Пример: 15)')
    
    elif state == 'waiting_translate':
        TextAnalysis(message.text, message.from_user.id)
        bot.reply_to(message, "✅ Текст получен! На какой язык переводим?", reply_markup=gen_markup_for_text())
        user_states.pop(message.chat.id, None)
    
    elif state == 'waiting_count_words':
        count = count_words(message.text)
        bot.reply_to(message, f'📊 Количество слов: {count}', reply_markup=back_markup_start())
        user_states.pop(message.chat.id, None)
    
    elif state == 'waiting_count_symbols':
        count = count_symbols(message.text)
        bot.reply_to(message, f'📊 Количество символов (без пробелов): {count}', reply_markup=back_markup_start())
        user_states.pop(message.chat.id, None)
    
    elif state == 'waiting_gen_password':
        try:
            length = int(message.text)
            if length < 4:
                bot.reply_to(message, "❌ Пароль должен быть длиннее 4 символов")
                return
            password = generate_password(length)
            bot.reply_to(message, f"🔐 Ваш пароль: `{password}`", parse_mode="Markdown", reply_markup=gen_markup_end_password())
            user_states.pop(message.chat.id, None)
        except ValueError:
            bot.reply_to(message, '❌ Введите число, например: 12', reply_markup=gen_markup_end_password())
    
    else:
        if not message.text.startswith('/'):
            bot.reply_to(
                message,
                "❓ **Неизвестная команда**\n\n"
                "Используйте /help для списка всех команд.\n\n"
                "🎨 Для генерации изображений используйте /generate [описание]\n"
                "или нажмите кнопку 'ИИ генератор' в меню.",
                parse_mode="Markdown"
            )

# ==================== ЗАПУСК БОТА ====================
if __name__ == '__main__':

    if not os.path.exists('images'):
        os.makedirs('images')
    
    print("Бот запущен...")
    print("Доступные команды:")
    print("  /start - Главное меню")
    print("  /generate [описание] - Генерация изображения")
    print("  /help - Справка")

    try:
        bot.infinity_polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        time.sleep(5)

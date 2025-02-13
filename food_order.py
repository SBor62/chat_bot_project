import sqlite3
import telebot

bot = telebot.TeleBot('8190699316:AAFBvq0sYz6anRLNNk-4AstriKACER6hcRg')

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать в систему заказа еды! Используйте /menu для просмотра меню.")

# Команда /menu
@bot.message_handler(commands=['menu'])
def show_menu(message):
    conn = sqlite3.connect('food_ordering.db')
    cursor = conn.cursor()
    cursor.execute("SELECT category, name, price FROM menu")
    menu_items = cursor.fetchall()
    conn.close()

    if not menu_items:
        bot.reply_to(message, "Меню пока пусто.")
        return

    menu_text = "Меню:\n"
    for category, name, price in menu_items:
        menu_text += f"{category}: {name} - {price} руб.\n"

    bot.reply_to(message, menu_text)

# Команда /order
@bot.message_handler(commands=['order'])
def order_food(message):
    bot.reply_to(message, "Введите название блюда и количество через пробел (например: 'Пицца 2').")

# Обработка заказа
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_order(message):
    if message.text.startswith('/'):
        return  # Игнорируем команды, начинающиеся с '/'

    try:
        parts = message.text.split()
        if len(parts) < 2:
            raise ValueError

        dish_name = ' '.join(parts[:-1])
        quantity = int(parts[-1])

        conn = sqlite3.connect('food_ordering.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (user_id, dish_name, quantity) VALUES (?, ?, ?)",
                       (message.from_user.id, dish_name, quantity))
        conn.commit()
        conn.close()

        bot.reply_to(message, f"Заказ на {dish_name} в количестве {quantity} добавлен в корзину.")
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите название блюда и количество через пробел.")

# Команда /status
@bot.message_handler(commands=['status'])
def order_status(message):
    conn = sqlite3.connect('food_ordering.db')
    cursor = conn.cursor()
    cursor.execute("SELECT dish_name, quantity, status FROM orders WHERE user_id = ?",
                   (message.from_user.id,))
    orders = cursor.fetchall()
    conn.close()

    if not orders:
        bot.reply_to(message, "У вас нет активных заказов.")
        return

    status_text = "Ваши заказы:\n"
    for dish_name, quantity, status in orders:
        status_text += f"{dish_name} - {quantity} шт. - {status}\n"

    bot.reply_to(message, status_text)

# Команда /feedback
@bot.message_handler(commands=['feedback'])
def leave_feedback(message):
    bot.reply_to(message, "Пожалуйста, оставьте ваш отзыв.")

# Обработка отзыва
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_feedback(message):
    if message.text.startswith('/'):
        return  # Игнорируем команды, начинающиеся с '/'

    conn = sqlite3.connect('food_ordering.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedback (user_id, message) VALUES (?, ?)",
                   (message.from_user.id, message.text))
    conn.commit()
    conn.close()

    bot.reply_to(message, "Спасибо за ваш отзыв!")

# Запуск бота
bot.polling()


# Меню:
import sqlite3

def add_menu_items():
    conn = sqlite3.connect('food_ordering.db')
    cursor = conn.cursor()

    menu_items = [
        ('Пицца', 'Маргарита', 500),
        ('Пицца', 'Пепперони', 600),
        ('Напитки', 'Кола', 100),
        ('Напитки', 'Сок', 150),
    ]

    cursor.executemany("INSERT INTO menu (category, name, price) VALUES (?, ?, ?)", menu_items)
    conn.commit()
    conn.close()

add_menu_items()
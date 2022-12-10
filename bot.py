import telebot
from telebot import types
import sqlite3

bot= telebot.TeleBot('5502078138:AAGgHgfqoxGjMhrIKZjirLP2ZJQ8ajPbOJw')

db = sqlite3.connect('server.db',check_same_thread=False)
sql = db.cursor()
sql.execute(""" Create table if Not exists rating(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Summ DOUBLE NOT NULL,
    Rate DOUBLE NOT NULL,
    Count INTEGER NOT NULL
) """)
db.commit()

#это для вывода того что надо из базы
def output(table):
    i = 0
    catalogStr = []
    while i < len(table):
        j = 0
        rowStr = ''
        while j < len(table[i]):
            rowStr = rowStr + str(table[i][j]) + ", " 
            j += 1
        catalogStr.append(rowStr)
        i += 1
    return catalogStr

# обработчик команды /start
@bot.message_handler(commands = ['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btnHelp = types.KeyboardButton("/help")
    btnEstimate = types.KeyboardButton("/estimate")
    btnRating = types.KeyboardButton("/rating")
    markup.add(btnHelp, btnEstimate, btnRating)
    bot.send_message(message.from_user.id, "Привет", reply_markup=markup)

# обработчик команды /help, показывает все имеющиеся команды
@bot.message_handler(commands = ['help'])
def help(message):
    bot.send_message(message.from_user.id, 
    """
    /start-<b>Такая штука что бы начать и что бы кнопочки появились</b>
    /help-<b> Ну тут я надеюсь объяснений не надо</b>
    /estimate-<b>Ну это надо что бы оценить плюшки всякие, тыкни, там инструкция как оценивать</b>
    /rating-<b>Просто рейтинг всех плюшек, всё ясно и понятно</b>
    """, 
    parse_mode='html')

# обработчик команды /estimate, показывает инструкцию к оценке и кнопочку для вывода всего списка булочек
@bot.message_handler(commands = ['estimate'])
def estimate(message):
    inline = types.InlineKeyboardMarkup()
    btnEstimate = types.InlineKeyboardButton(text = "Тык", callback_data = "Список")
    inline.add(btnEstimate)
    bot.send_message( message.from_user.id, 
    "Для оценки пирожочка надо будет написать \n" +
    "/оценка <оценка>(1-5) <номер булочки>. \n" +
    "Например: \n" +
    "      /оценка 5 6 \n" +
    "Если понял(а) то тыкай кнопку снизу там список будет",
    reply_markup = inline )
#a = sql.execute("select id, Name from rating")

# обработчик кнопки под сообщением от команды /estimate, выводит пронумерованный список товаров
@bot.callback_query_handler(func=lambda message:True)
def inline(message):
    if message.data == 'Список':
        catalog = []
        catalog = list(sql.execute("select id, Name from rating"))
        bot.send_message(message.from_user.id, '\n'.join(output(catalog)))




# обработчик команды /оценка, позволяет поставить оценку определенному товару
@bot.message_handler(commands=['оценка'])
def evaluation(message):
    try:
        if len(message.text) > 7:
            mes=message.text.split(" ")
            if int(mes[1]) > 5 or int(mes[1]) < 0 :
              bot.send_message(message.from_user.id, "Поставте оценку от 1 до 5.")
            else:
              sql.execute(f"update rating set Count=Count+1, Summ=Summ+{round(float(mes[1]),1)} where id ={int(mes[2])}")
              db.commit()
              bot.send_message(message.from_user.id, "Принято")
        else:
               bot.send_message(message.from_user.id, "Писать нужно /оценка <номер булочки> <оценка>")
    except:
        bot.send_message(message.from_user.id, "Что-то поломалось. Проверьте написанное.")

# обработчик комманды /rating, выводит список булочек с их рейтингом
@bot.message_handler(commands=['rating'])
def rate(message):
    catalog=[]
    catalog = list(sql.execute("select Name, IFNULL(Summ/Count, 0) as Rating from rating"))
    
    bot.send_message(message.from_user.id, '\n'.join(output(catalog)))

bot.polling(non_stop=True)



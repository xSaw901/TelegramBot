import telebot
from telebot import types
import sqlite3

bot= telebot.TeleBot('5502078138:AAGgHgfqoxGjMhrIKZjirLP2ZJQ8ajPbOJw')

db= sqlite3.connect('server.db',check_same_thread=False)
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
def output(catalog):
    i=0
    while i<len(catalog):
        b=0
        nullstr=''
        while b< len(catalog[i]):
            nullstr=nullstr+str(catalog[i][b])+", "
            b=b+1
        catalog[i]=nullstr
        i+=1
    return catalog

# обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    murkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1= types.KeyboardButton("/help")
    btn2= types.KeyboardButton("/estimate")
    btn3= types.KeyboardButton("/rating")
    murkup.add(btn1, btn2, btn3)
    bot.send_message(message.from_user.id, "Привет", reply_markup=murkup)

# обработчик команды /help, показывает все имеющиеся команды
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, "/start-<b>Такая штука что бы начать и что бы кнопочки появились</b>  \n /help-<b> Ну тут я надеюсь объяснений не надо</b>\n /estimate-<b>Ну это надо что бы оценить плюшки всякие, тыкни, там инструкция как оценивать</b> \n /rating-<b>Просто рейтинг всех плюшек, всё ясно и понятно</b>  ", parse_mode='html')

# обработчик команды /estimate, показывает инструкцию к оценке и кнопочку для вывода всего списка булочек
@bot.message_handler(commands=['estimate'])
def estimate(message):
    inline= types.InlineKeyboardMarkup()
    btn1= types.InlineKeyboardButton(text="Тык", callback_data="Список")
    inline.add(btn1)
    bot.send_message(message.from_user.id, "Для оценки пирожочка надо будет написать /оценка <оценка>(1-5) <номер булочки>. Если понял(а) то тыкай кнопку снизу там список будет", reply_markup=inline)
a= sql.execute("select id, Name from rating")

# обработчик кнопки под сообщением от команды /estimate, выводит пронумерованный список товаров
@bot.callback_query_handler(func=lambda message:True)
def inlin(message):
    if message.data == 'Список':
        catalog=[]
        
        catalog = list(sql.execute("select id, Name from rating"))
        bot.send_message(message.from_user.id, '\n'.join(output(catalog)))




# обработчик команды /оценка, позволяет поставить оценку определенному товару
@bot.message_handler(commands=['оценка'])
def evaluation(message):
    try:
        if len(message.text)>7:
            mes=message.text.split(" ")
            if int(mes[1])>5 or int(mes[1])<0 :
              bot.send_message(message.from_user.id, "По русски же написал что от 1 до 5 оценку ставить 😡")
            else:
              sql.execute(f"update rating set Count=Count+1, Summ=Summ+{round(float(mes[1]),1)} where id ={int(mes[2])}")
              sql.execute(f"update rating set Rate=Summ/Count where id ={int(mes[2])}")
              db.commit()
              bot.send_message(message.from_user.id, "Принято")
        else:
               bot.send_message(message.from_user.id, "Понятия не имею что тебе надо, писать нужно /оценка <номер булочки> <оценка>")
    except:
        bot.send_message(message.from_user.id, "Что-то поломалось блин, даже не знаю что. Посмтри повнимательней что написал.")

# обработчик комманды /rating, выводит список булочек с их рейтингом
@bot.message_handler(commands=['rating'])
def rate(message):
    catalog=[]
    catalog = list(sql.execute("select Name, Rate from rating"))
    bot.send_message(message.from_user.id, '\n'.join(output(catalog)))

bot.polling(non_stop=True)



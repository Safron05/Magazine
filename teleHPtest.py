
import os
import telebot
from telebot import types
import const
from geopy.distance import geodesic
from flask import Flask, request
bot_type = 'online'

PORT = 0
TOKEN = '1601868112:AAG4PHbJ5IQY3R4SfdMAAn-ceEboKAeZfJA'
bot = telebot.TeleBot(TOKEN)
server = None

if bot_type == 'offline':
    bot.remove_webhook()
else:
    PORT = int(os.environ.get('PORT', 5000))
    server = Flask(__name__)

#создадим клавиатуру в меню
markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
btn_adress = types.KeyboardButton('Адреса магазинов', request_location=True)
btn_payment = types.KeyboardButton('Способы оплаты')
btn_delivery = types.KeyboardButton('Способы доставки')
btn_service = types.KeyboardButton('Наши услуги')
btn_sales = types.KeyboardButton('Акции')
markup_menu.add(btn_adress, btn_delivery, btn_payment,btn_service,btn_sales)

markup_inline_payment = types.InlineKeyboardMarkup()
btn_in_cash = types.InlineKeyboardButton('Наличные', callback_data='cash')
btn_in_card = types.InlineKeyboardButton('Картой', callback_data='card')
btn_in_invoice = types.InlineKeyboardButton('Qiwi', callback_data='invoice')

markup_inline_payment.add(btn_in_card, btn_in_cash, btn_in_invoice)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 'Привет!!', reply_markup=markup_menu)

@bot.message_handler(func=lambda message:True)
def echo_all(message):
    print(message)
    if message.text == 'Способы доставки':
        bot.reply_to(message, 'Доставка курьером, самовывоз, транспортной компанией', reply_markup=markup_menu)
    elif message.text == 'Способы оплаты':
        bot.reply_to(message, 'Выберайте', reply_markup=markup_inline_payment)
    else:
        bot.reply_to(message, message.text, reply_markup=markup_menu)

@bot.message_handler(func=lambda message:True, content_types=['location'])
def magazin_location(message):
    print(message)
    lon = message.location.longitude
    lat = message.location.latitude

    distance = []
    for m in const.MAGAZINE:
        result = geodesic((m['lonm'],m['latm']),(lat,lon)).kilometers
        distance.append(result)
    index = distance.index(min(distance))

    bot.send_message(message.chat.id, 'Ближайший магазин')
    bot.send_venue(message.chat.id, const.MAGAZINE[index]['lonm'],
                                    const.MAGAZINE[index]['latm'],
                                    const.MAGAZINE[index]['Title'],
                                    const.MAGAZINE[index]['adress'])

@bot.callback_query_handler(func=lambda call:True)
def call_back_payment(call):
    print(call)
    if call.data == 'cash':
        bot.send_message(call.message.chat.id, text='''
        Наличная оплата производится в рублях в наших магазинах''',
                         reply_markup=markup_inline_payment)


if bot_type == 'offline':
    bot.polling()
else:
    @server.route('/' + TOKEN, methods=['POST'])
    def getMessage():
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url='https://limitless-thicket-26129.herokuapp.com/' + TOKEN)
        return "!", 200
    webhook
    if __name__ == "__main__":
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

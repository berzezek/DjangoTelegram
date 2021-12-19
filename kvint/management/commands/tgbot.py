import telebot
from django.conf import settings
from django.core.management import BaseCommand
from kvint.utils import (
    start_dialog,
    continue_dialog,
    machine,
    get_current_order,
    get_count,
    get_info
)

bot = telebot.TeleBot(settings.TOKEN_TG)


@bot.message_handler(commands=[ 'start' ])
def send_welcome(message):
    bot.reply_to(message, "Привет, мы можем заказать пиццу!")


@bot.message_handler(commands=[ 'info' ])
def do_info(message):
    try:
        o = get_current_order(message.chat.id)
        c = get_count(message.chat.id)
        if o.order_msg != '' and o.payment_msg != '':
            bot.send_message(message.chat.id, f'{get_info(o)}\nВсего заказов: {c}.')
        elif o.order_msg == '':
            bot.send_message(message.chat.id, 'Вы не указали размер пиццы')
        elif o.payment_msg == '':
            bot.send_message(message.chat.id, 'Вы не указали способ оплаты')
    except Exception:
        bot.send_message(message.chat.id, 'Вы еще ничего не заказали')


@bot.message_handler(commands=[ 'order' ])
def do_order(message):
    text = start_dialog(message.chat.id, message.chat.first_name)
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: get_current_order(message.chat.id).order_state == 'order')
def user_order(message):
    text = continue_dialog(message.chat.id, machine.to_payment, 1, 'order_msg', message.text)
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: get_current_order(message.chat.id).order_state == 'payment')
def user_payment(message):
    text = continue_dialog(message.chat.id, machine.to_end, 2, 'payment_msg', message.text)
    bot.send_message(message.chat.id, f'{text}\n\nДля информации введите\n/info\nДля нового заказа\n/order')


class Command(BaseCommand):
    help = 'Телеграмм бот'

    def handle(*args, **kwargs):
        print('Бот запущен!')
        bot.infinity_polling()

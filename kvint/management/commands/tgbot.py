import telebot
from django.conf import settings
from django.core.management import BaseCommand
from kvint.models import Profile, Order
from kvint.utils import create_order, continue_order, machine, get_current_order

bot = telebot.TeleBot(settings.TOKEN_TG)


@bot.message_handler(commands=[ 'start' ])
def send_welcome(message):
    bot.reply_to(message, "Привет, мы можем заказать пиццу!")


@bot.message_handler(commands=[ 'info' ])
def do_info(message):
    try:
        p, _ = Profile.objects.get_or_create(
            external_id=message.chat.id,
            defaults={
                'name': message.chat.first_name
            }
        )
        o = Order.objects.get(profile=p)
        if o.order_msg != '' and o.payment_msg != '':
            bot.send_message(message.chat.id, Order.get_info(o))
        elif o.order_msg == '':
            bot.send_message(message.chat.id, 'Вы не указали размер пиццы\n/order')
        elif o.payment_msg == '':
            bot.send_message(message.chat.id, 'Вы не указали способ оплаты\n/order')
    except Order.DoesNotExist:
        p.save()
        bot.send_message(message.chat.id, 'Вы еще ничего не заказали')


@bot.message_handler(commands=[ 'order' ])
def do_order(message):
    text = create_order(message.chat.id, message.chat.first_name)
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: get_current_order(message.chat.id).order_state == 'order')
def user_order(message):
    text = continue_order(message.chat.id, machine.to_payment, 1, 'order_msg', message.text)
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: get_current_order(message.chat.id).order_state == 'payment')
def user_payment(message):
    text = continue_order(message.chat.id, machine.to_end, 2, 'payment_msg', message.text)
    bot.send_message(message.chat.id, f'{text}\nДля информации введите\n/info')


class Command(BaseCommand):
    help = 'Телеграмм бот'

    def handle(*args, **kwargs):
        print('Бот запущен!')
        bot.infinity_polling()

import telebot
from django.conf import settings
from django.core.management import BaseCommand
from kvint.models import Profile, Order, OrderManager

bot = telebot.TeleBot(settings.TOKEN_TG)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет, мы можем заказать пиццу!")


def get_current_order(profile):
    p = Profile.objects.get(external_id=profile)
    return Order.objects.get(profile=p)


@bot.message_handler(commands=['info'])
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


@bot.message_handler(commands=['order'])
def do_order(message):
    p, _ = Profile.objects.get_or_create(
        external_id=message.chat.id,
        defaults={
            'name': message.chat.first_name
        }
    )
    o, _ = Order.objects.get_or_create(
        profile=p,
    )
    Order.objects.create_order()
    bot.send_message(message.chat.id, OrderManager.dialog[0])


@bot.message_handler(func=lambda message: get_current_order(message.chat.id).order_state == 'order')
def user_order(message):
    Order.objects.create_order_msg(msg=message.text)
    bot.send_message(message.chat.id, OrderManager.dialog[1])
    Order.objects.create_payment()


@bot.message_handler(func=lambda message: get_current_order(message.chat.id).order_state == 'payment')
def user_payment(message):
    profile = Profile.objects.get(external_id=message.chat.id)
    Order.objects.create_payment_msg(msg=message.text)
    Order.objects.create_end()
    bot.send_message(message.chat.id, Order.get_info(Order.objects.get(profile=profile)))



class Command(BaseCommand):
    help = 'Телеграмм бот'

    def handle(*args, **kwargs):
        print('Бот запущен!')
        bot.infinity_polling()

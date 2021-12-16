from django.utils import timezone
from django.db import models
from transitions import Machine
from time import strftime


class Profile(models.Model):
    external_id = models.PositiveIntegerField(verbose_name='ID пользователя в сети', unique=True)
    name = models.CharField(verbose_name='Имя пользователя ', max_length=255)


class OrderManager(models.Manager):
    states = [
        'order',
        'payment',
        'end'
    ]
    dialog = [
        'Какую пиццу Вы желаете заказать? Большую или маленькую',
        'Как Вы собираетесь платить',
        'Спасибо за заказ!'
    ]
    machine = Machine(states=states)

    def create_order(self):
        self.machine.to_order()
        order_state = self.update(order_state=self.machine.state)
        return order_state

    def create_payment(self):
        self.machine.to_payment()
        order_state = self.update(order_state=self.machine.state)
        return order_state

    def create_end(self):
        self.machine.to_end()
        order_state = self.update(order_state=self.machine.state, created_at=timezone.now())
        return order_state

    def create_order_msg(self, msg):
        order_msg = self.update(order_msg=msg)
        return order_msg

    def create_payment_msg(self, msg):
        payment_msg = self.update(payment_msg=msg)
        return payment_msg


class Order(models.Model):
    profile = models.ForeignKey(Profile, verbose_name='Профиль', on_delete=models.PROTECT)
    order_state = models.CharField(verbose_name='Состояние', max_length=255, default='initial')
    created_at = models.DateTimeField(verbose_name='Время получения заказа', auto_now_add=True)
    order_msg = models.CharField(verbose_name='Размер пиццы', max_length=255, default='')
    payment_msg = models.CharField(verbose_name='Способ оплаты', max_length=255, default='')

    objects = OrderManager()

    def get_info(self):
        return f'Вы заказали: {self.order_msg} пиццу.\n' \
               f'Способ оплаты: {self.payment_msg}.\n' \
               f'{self.created_at.strftime("Дата заказа: %Y-%m-%d ... Время заказа: %H:%M")}.\n' \
               f'Номер заказа {self.created_at.strftime("%m%d")}{self.pk}'

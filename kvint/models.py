
from django.db import models
from time import strftime


class Profile(models.Model):

    external_id = models.PositiveIntegerField(verbose_name='ID пользователя в сети', unique=True)
    name = models.CharField(verbose_name='Имя пользователя ', max_length=255)


class Order(models.Model):

    profile = models.ForeignKey(Profile, verbose_name='Профиль', on_delete=models.PROTECT)
    order_state = models.CharField(verbose_name='Состояние', max_length=255, default='initial')
    created_at = models.DateTimeField(verbose_name='Время получения заказа', auto_now_add=True)
    order_msg = models.CharField(verbose_name='Размер пиццы', max_length=255, default='')
    payment_msg = models.CharField(verbose_name='Способ оплаты', max_length=255, default='')

    def get_info(self):
        return f'Вы заказали: {self.order_msg} пиццу.\n' \
               f'Способ оплаты: {self.payment_msg}.\n' \
               f'{self.created_at.strftime("Дата заказа: %Y-%m-%d ... Время заказа: %H:%M")}.\n' \
               f'Номер заказа {self.created_at.strftime("%m%d")}{self.pk}'

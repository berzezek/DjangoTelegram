from django.utils import timezone

from django.test import TestCase as TestCase
from .models import Profile, Order
from .utils import create_order, continue_order, machine


class ProfileCase(TestCase):

    def setUp(self):
        p, _ = Profile.objects.get_or_create(
            external_id=1,
            defaults={
                'name': 'foo'
            }
        )
        o, _ = Order.objects.get_or_create(
            profile=p,
            created_at=timezone.now()
        )
        create_order(1, machine.to_order)
        continue_order(1, machine.to_payment, 1, 'order_msg', 'foo')
        continue_order(1, machine.to_end, 1, 'payment_msg', 'foo')

    def test_create_order(self):
        c = create_order(1, machine.to_order)
        self.assertTrue(c.startswith('Какую'))

    def test_continue_order_payment(self):
        c = continue_order(1, machine.to_payment, 1, 'order_msg', 'foo')
        self.assertTrue(c.startswith('Как Вы'))

    def test_continue_order_end(self):
        c = continue_order(1, machine.to_end, 2, 'payment_msg', 'foo')
        self.assertTrue(c.startswith('Спасибо'))

    def test_get_info(self):
        c = Order.objects.get(profile=Profile.objects.get(pk=1)).get_info()
        self.assertTrue(c.startswith(f'Вы заказали'))

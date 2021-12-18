from django.utils import timezone

from django.test import TestCase as TestCase
from .models import Profile, Order
from .utils import start_dialog, continue_dialog, machine


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
        start_dialog(1, machine.to_order)
        continue_dialog(1, machine.to_payment, 1, 'order_msg', 'foo')
        continue_dialog(1, machine.to_end, 1, 'payment_msg', 'foo')

    def test_create_dialog(self):
        c = start_dialog(1, machine.to_order)
        self.assertTrue(c.startswith('Какую'))

    def test_continue_dialog_payment(self):
        c = continue_dialog(1, machine.to_payment, 1, 'order_msg', 'foo')
        self.assertTrue(c.startswith('Как Вы'))

    def test_continue_dialog_end(self):
        c = continue_dialog(1, machine.to_end, 2, 'payment_msg', 'foo')
        self.assertTrue(c.startswith('Спасибо'))

    def test_get_info(self):
        o = Order.objects.filter(order_state='end').first().get_info()
        self.assertTrue(o.startswith(f'Вы заказали'))

    def test_get_count(self):
        o = Order.objects.filter(order_state='end').count()
        self.assertIs(type(o), int)

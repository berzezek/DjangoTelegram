from django.test import TestCase as TestCase
from unittest import TestCase as UniTestCase
from .models import Profile, Order


class ProfileCase(DTestCase):

    def test_setUp(self):
        p1 = Profile.objects.create(name="foo", external_id=101)
        for i in range(20):
            p = Profile.objects.create(name="foo", external_id=i)
            o, _ = Order.objects.get_or_create(
                profile=p,
            )
            Order.objects.create_order()
            Order.objects.create_payment()
            Order.objects.create_end()
            Order.objects.create_order_msg(msg='foo')
            Order.objects.create_payment_msg(msg='foo')
            o.get_info()

class UtilTestCase(TestCase):

    def test_info(self):
        p = Profile.objects.create(name="foo", external_id=1001)
        o, _ = Order.objects.get_or_create(
            profile=p,
        )
        r = o.get_info()
        self.assertTrue(r.startswith('Вы заказали:'))
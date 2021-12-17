from transitions import Machine
from django.utils import timezone
from .models import Profile, Order

states = [
    'order',
    'payment',
    'end'
]
dialog = [
    'Какую пиццу Вы желаете заказать? Большую или маленькую?',
    'Как Вы собираетесь платить?',
    'Спасибо за заказ!'
]
machine = Machine(states=states)

"""!Для тестового задания заказ просто перезаписывается!"""

def create_order(chat_id: int, name: str):
    """
    1. Для начала заказа находим или создаем профиль (Profile, external_id=chat_id, name=name),
    2. Находим или создаем заказ (Order)
    3. Устанавливаем состояние перехода на 'order'
    4. Начинаем диалог с клиентом.

    :param chat_id: Profile.external_id
    :param name: Profile.name
    :return: Возвращаем диалог
    """
    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': name
        }
    )
    machine.to_order()
    o, _ = Order.objects.get_or_create(
        profile=p,
    )
    o.order_state = machine.state
    o.save()
    return dialog[ 0 ]


def continue_order(chat_id: int, func, index: int, order_field: str, msg: str):
    """
    1. Для продолжения заказа находим существующий профиль (параметр chat_id).
    2. Находим заказ по профилю.
    3. Инициализируем состояние перехода (параметр func).
    4. Устанавливаем состояние перехода в поле модели заказа (Order)
    5. Устанавливаем время совершения заказа (created_at)
    5. Устанавливаем значение в поля заказа сообщений (order_msg, payment_msg, ...)
    6. Записываем значения перехода и сообщение указывая нужное через параметр (order_field)
    7. Продолжаем диалог

    :param chat_id: Profile.external_id
    :param func: Метод смены состояния (to_<состояние>)
    :param index: Индекс строки диалога с клиентом (dialog[index])
    :param order_field: ПУказываем нужное поле (order_msg, payment_msg, ...) модели (Order)
    :param msg: Получаем от пользователя
    :return: Возвращаем диалог
    """
    p = Profile.objects.get(external_id=chat_id)
    o = Order.objects.get(profile=p)
    func()
    o.order_state = machine.state
    o.order_msg = msg
    o.payment_msg = msg
    o.created_at = timezone.now()
    o.save(update_fields=[order_field, 'order_state', 'created_at'])
    return dialog[ index ]


def get_current_order(profile):
    """
    Находим состояние заказа клиента
    :param profile: получаем из сообщения от пользователя.
    :return: Объект заказа.
    """
    p = Profile.objects.get(external_id=profile)
    return Order.objects.get(profile=p)
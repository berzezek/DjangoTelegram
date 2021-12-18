from transitions import Machine
from django.utils import timezone
from .models import Profile, Order

states = [
    'order',
    'payment',
    'end'
]
dialog = [
    'Какую пиццу Вы желаете заказать?\nБольшая или маленькая?',
    'Как Вы собираетесь платить?',
    'Спасибо за заказ!'
]
machine = Machine(states=states)


def create_new_order(profile: int, name: str):
    """
        Создаем новый заказ.
    :param profile: получаем из сообщения от пользователя.
    :param name: получаем из сообщения пользователя.
    :return: Объект заказа.
    """

    p, _ = Profile.objects.get_or_create(
        external_id=profile,
        defaults={
            'name': name
        }
    )
    o = Order.objects.create(profile=p)
    return o


def get_current_order(profile: int):
    """
        Находим существующий заказ клиента.
    :param profile: получаем из сообщения от пользователя.
    :return: Объект заказа.
    """
    p = Profile.objects.get(external_id=profile)
    o = Order.objects.filter(profile=p).order_by('-created_at').first()
    return o


def start_dialog(chat_id: int, name: str):
    """
    1. Находим или создаем профиль (Profile, external_id=chat_id, name=name), создаем заказ (Order)
    2. Устанавливаем состояние перехода на 'order'
    3. Начинаем диалог с клиентом.

    :param chat_id: Profile.external_id
    :param name: Profile.name
    :return: Возвращаем диалог
    """

    o = create_new_order(chat_id, name)
    machine.to_order()
    o.order_state = machine.state
    o.save()
    return dialog[ 0 ]


def continue_dialog(chat_id: int, func, index: int, order_field: str, msg: str):
    """
    1. Находим последний заказ по профилю (параметр chat_id).
    2. Инициализируем состояние перехода (параметр func).
    3. Устанавливаем состояние перехода в поле модели заказа (Order)
    4. Устанавливаем время совершения заказа (created_at)
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

    o = get_current_order(chat_id)
    func()
    o.order_state = machine.state
    o.order_msg = msg
    o.payment_msg = msg
    o.created_at = timezone.now()
    o.save(update_fields=[ order_field, 'order_state', 'created_at' ])
    return dialog[ index ]


def get_count(profile):
    p = Profile.objects.get(external_id=profile)
    o = Order.objects.filter(profile=p, order_state='end')
    return o.count()

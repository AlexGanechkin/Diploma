from typing import Callable, Any

from django.core.management import BaseCommand
from pydantic import BaseModel

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from goals.models import Goal, GoalCategory


class FSMData(BaseModel):
    next_handler: Callable
    data: dict[str, Any] = {}


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()
        self.clients: dict[int, FSMData] = {}

    def handle(self, *args, **options):
        offset = 0

        self.stdout.write(self.style.SUCCESS('Bot started'))
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg: Message):
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id)

        if tg_user.is_verified:
            self.handle_authorized_user(tg_user, msg)
        else:
            tg_user.update_verification_code()
            self.tg_client.send_message(tg_user.chat_id, f'Подтвердите, пожалуйста, свой аккаунт. \
                Для подтверждения необходимо ввести код: {tg_user.verification_code} на сайте')

    def handle_authorized_user(self, tg_user: TgUser, msg: Message):
        if msg.text.startswith('/'):
            if msg.text == '/goals':
                self.handle_goals_command(tg_user, msg)
            elif msg.text == '/create':
                self.handle_create_command(tg_user, msg)
            elif msg.text == '/cancel':
                self.clients.pop(tg_user.chat_id, None)
            else:
                self.tg_client.send_message(tg_user.chat_id, 'Неизвестная команда')
        elif tg_user.chat_id in self.clients:
            client = self.clients[tg_user.chat_id]
            client.next_handler(tg_user=tg_user, msg=msg, **client.data)

    def handle_goals_command(self, tg_user: TgUser, msg: Message):
        goals = Goal.objects.exclude(status=Goal.Status.archived).filter(user=tg_user.user)
        if goals:
            text = 'Ваши цели:\n' + '\n'.join([f'{goal.id}) {goal.title}' for goal in goals])
        else:
            text = 'У вас отсутствуют цели'

        self.tg_client.send_message(tg_user.chat_id, text)

    def handle_create_command(self, tg_user: TgUser, msg: Message):
        categories = GoalCategory.objects.filter(user=tg_user.user).exclude(is_deleted=True)
        if not categories:
            self.tg_client.send_message(tg_user.chat_id, 'У вас не созданы категории')

        text = 'Для создания цели выберите категорию:\n' + '\n'.join([f'{cat.id}) {cat.title}' for cat in categories])
        self.tg_client.send_message(tg_user.chat_id, text)
        self.clients[tg_user.chat_id] = FSMData(next_handler=self._get_category)

    def _get_category(self, tg_user: TgUser, msg: Message, **kwargs):
        try:
            category = GoalCategory.objects.get(pk=msg.text)
        except GoalCategory.DoesNotExist:
            self.tg_client.send_message(tg_user.chat_id, 'Категория не существует')
            return
        else:
            self.clients[tg_user.chat_id].next_handler = self._create_goal
            self.clients[tg_user.chat_id].data['category'] = category
            #self.clients[tg_user.chat_id] = FSMData(next_handler=self._create_goal, data={'category': category})
            self.tg_client.send_message(tg_user.chat_id, 'Введите название новой цели')

    def _create_goal(self, tg_user: TgUser, msg: Message, **kwargs):
        category = kwargs['category']
        Goal.objects.create(category=category, user=tg_user.user, title=msg.text)
        self.tg_client.send_message(tg_user.chat_id, 'Новая цель создана')
        self.clients.pop(tg_user.chat_id, None)

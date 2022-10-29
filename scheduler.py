from taskiq import InMemoryBroker
from taskiq.schedule_sources import LabelScheduleSource
from taskiq.scheduler import TaskiqScheduler

from model.db_work import get_data
from model.user_data_class import UserData
from view.main_menu.statistics import create_user_stats

from controller.bot_data_work import db_update_user_settings


broker = InMemoryBroker()

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)


@broker.task(schedule=[{"cron": "* */1 * * *"}])
async def autostat() -> bool:
    # await db_update_user_settings(user_id='369107121', new_settings={'autostat': True})
    # получает список юзеров
    raw_user_data = await get_data(db_name='user_data')
    # формируем список юзеров
    users = [UserData().from_raw_data(raw_data) for raw_data in raw_user_data]
    # запускаем расчет статистики для пользователей
    for user in users:
        if user.settings:
            print(f'Настройки пользователя {user.user_name}: {user.settings}')
            await create_user_stats(plot_needed=False, user_id=user.user_id)

    return True

import asyncio
from decimal import Decimal, InvalidOperation
from typing import Union

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from settings.api_key import APP_TOKEN

from controller.bot_data_work import get_user_total, add_user, get_user_data, update_user_total_info
from model.user_data_class import UserData
from controller.bot_redis_work import get_price, redis_get_currency_short_names, redis_get_crypto_short_names

from view.common.keyboard import get_start_menu
from view.main_menu.add import register_handlers_for_add_menu
from view.main_menu.statistics import create_user_stats


async def start_bot():
    bot = Bot(token=APP_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    dp.register_message_handler(send_welcome, commands=['start', 'help', 'Main menu'])
    dp.register_message_handler(show_user_statistic, Text(equals=['Statistics', 'stat', 'стат']))
    dp.register_message_handler(cmd_cancel, Text(equals=['Cancel', 'cancel', 'cl', 'Отмена', 'отмена']), state='*')

    register_handlers_for_add_menu(dp)

    await dp.skip_updates()
    print('Bot running...')
    await dp.start_polling()


async def send_welcome(mess: Message):
    print(f'Пользователь {mess.from_user.id} начал общение с ботом!')
    print(f'{mess.location=}')
    user_data: UserData = await get_user_data(str(mess.from_user.id))
    if user_data:
        await mess.answer(f'Hello, {mess.from_user.full_name}\nYour cash:\n{user_data.users_cash}',
                          reply_markup=get_start_menu())
    else:
        await add_user(user_id=str(mess.from_user.id),
                       user_name=mess.from_user.full_name)
        await mess.answer(text=f'Hello, {mess.from_user.full_name.title()}'
                               f'\nI am Sihe ^^'
                               f'\nI can help you with your investing!',
                          reply_markup=get_start_menu())


async def show_user_statistic(mess: Message):
    user_stats_parts = await create_user_stats(mess)
    await mess.answer(text='\n'.join(user_stats_parts),
                      reply_markup=get_start_menu())


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=get_start_menu())



async def create_user(user_id: str):
    if res:=await get_user_total(user_id):
        print('Пользователь есть в базе. Его данные:')
        print(res)
    return res


if __name__ == '__main__':
    asyncio.run(start_bot())

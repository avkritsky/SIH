import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from settings.api_key import APP_TOKEN

from controller.bot_data_work import db_get_user_total, db_add_user, db_get_user_data, db_create_tables
from model.user_data_class import UserData

from view.common.keyboard import get_start_menu
from view.main_menu.add import register_handlers_for_add_menu
from view.main_menu.del_transaction import register_handlers_for_del_menu
from view.main_menu.statistics import create_user_stats
from view.additional_menu.root_additional_menu import register_handlers_for_additional_menu


async def start_bot():

    await db_create_tables()

    bot = Bot(token=APP_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    dp.register_message_handler(send_welcome, commands=['start', 'help', 'Main menu'])
    dp.register_message_handler(show_user_statistic, Text(equals=['Statistics', 'stat', 'стат']))
    dp.register_message_handler(cmd_cancel, Text(equals=['Cancel', 'cancel', 'cl', 'Отмена', 'отмена']), state='*')

    # ADD menu button
    register_handlers_for_add_menu(dp)
    # DEL menu button
    register_handlers_for_del_menu(dp)
    # ADDITIONAL menu button
    register_handlers_for_additional_menu(dp)

    await dp.skip_updates()
    print('Bot running...')
    await dp.start_polling()


async def send_welcome(mess: Message):
    """Show hello message!"""
    print(f'Пользователь {mess.from_user.id} начал общение с ботом!')
    print(f'{mess.chat.id=}')
    user_data: UserData = await db_get_user_data(str(mess.from_user.id))
    if user_data:
        await mess.answer(f'Hello, {mess.from_user.full_name}\nYour cash:\n{user_data.users_cash}',
                          reply_markup=get_start_menu())
    else:
        await db_add_user(user_id=str(mess.from_user.id),
                          user_name=mess.from_user.full_name)
        await mess.answer(text=f'Hello, {mess.from_user.full_name.title()}'
                               f'\nI am Sihe ^^'
                               f'\nI can help you with your investing!',
                          reply_markup=get_start_menu())


async def show_user_statistic(mess: Message):
    """Show user stats. Main Menu button."""
    await create_user_stats(mess)


async def cmd_cancel(message: types.Message, state: FSMContext):
    """Canceled FSM automat and show Main Menu"""
    await state.finish()
    await message.answer("Действие отменено", reply_markup=get_start_menu())



async def create_user(user_id: str):
    if res:=await db_get_user_total(user_id):
        print('Пользователь есть в базе. Его данные:')
        print(res)
    return res


if __name__ == '__main__':
    asyncio.run(start_bot())

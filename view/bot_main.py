from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message

from settings.api_key import APP_TOKEN

from controller.bot_data_work import get_user_total, add_user

bot = Bot(token=APP_TOKEN)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(mess: Message):
    print(f'Пользователь {mess.from_user.id} начал общение с ботом!')
    user_total_info = await get_user_total(str(mess.from_user.id))
    if user_total_info:
        user_cash_str = '\n'.join((f'{key}:   {val}' for key, val in user_total_info.items()))
        await mess.answer(f'Hello, {mess.from_user.full_name}\nYour cash:\n{user_cash_str}',
                          reply_markup=get_start_menu())
    else:
        await add_user(user_id=str(mess.from_user.id),
                       user_name=mess.from_user.full_name)
        await mess.answer(text=f'Hello, {mess.from_user.full_name}'
                               f'\nI am Sihe ^^'
                               f'\nI can help you with your investing!',
                          reply_markup=get_start_menu())


async def create_user(user_id: str):
    if res:=await get_user_total(user_id):
        print('Пользователь есть в базе. Его данные:')
        print(res)
    return res


def get_start_menu():
    menu_titles = (
        'Добавить транзакцию',
        'Показать все транзакции',
        'Общая прибыль'
    )

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*menu_titles)

    return keyboard



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

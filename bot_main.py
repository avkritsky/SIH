from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message

from settings.api_key import APP_TOKEN

from controller.bot_data_work import get_user_total, add_user, get_user_data
from model.user_data_class import UserData

bot = Bot(token=APP_TOKEN)

dp = Dispatcher(bot)


# TODO:
#  на старте ничего не показывать, кроме основного меню,
#  Статистика - выводит все имеемые криптовалюты, их цену в основной валюте пользователя, общую прибль:
#  получает данные пользователя из БД (хранение в редисе по юзер-ид),
#  Добавить значения - добаляет транзакцию,
#  Настройки - выбор основной валюты / иное,


@dp.message_handler(commands=['start', 'help', 'Main menu'])
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
        'Statistics',
        'Add values',
        'Settings'
    )

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*menu_titles)

    return keyboard



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

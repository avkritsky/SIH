from decimal import Decimal

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message
from aiogram.dispatcher.filters import Text


from settings.api_key import APP_TOKEN

from controller.bot_data_work import get_user_total, add_user, get_user_data
from model.user_data_class import UserData
from controller.bot_redis_work import get_price

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


# @dp.message_handler(Text(equals='Statistics'))
# @dp.message_handler(commands='user_statistics')
@dp.callback_query_handler(text='user_statistics')
async def show_user_statistic(call: types.CallbackQuery):
    user_data: UserData = await get_user_data(str(call.from_user.id))

    if not user_data.total:
        await call.answer(text='Excuse me, You have not any valutes!')

    user_stats_parts = []

    spended = Decimal(user_data.total.get(user_data.default_value, 0)) * -1
    getted = Decimal(0)

    for valute_name, valute_val in user_data.total.items():
        if valute_name == user_data.default_value:
            continue
        valute_price_data = await get_price(valute_name.upper())
        raw_usd_price = await get_price('USD')
        usd_price = raw_usd_price.get('Value')
        if not valute_price_data:
            continue
        valute_price = valute_price_data.get('price', 0)

        if not valute_price:
            valute_price = valute_price_data.get('Value')

        usd_val = (Decimal(str(valute_val)) * Decimal(str(valute_price))).quantize(Decimal("1.00"))
        user_val = (usd_val * Decimal(str(usd_price))).quantize(Decimal('1.00'))
        getted += user_val

        user_stats_parts.append(
            f'{valute_name.upper()}:'
            f' {valute_val} '
            f'| {usd_val} $'
            f'| {user_val} {user_data.default_value}'
        )
    user_stats_parts.append(
        f'Profit: {getted - spended} or {(((getted - spended) / spended) * 100).quantize(Decimal("1.00"))} %'
    )

    await call.message.answer(text='\n'.join(user_stats_parts),
                                reply_markup=get_start_menu())


@dp.message_handler(Text(equals='Add ...'))
async def show_add_menu(mess: Message):
    add_menu_titles = (
        'Currency',
        'Transaction',
    )
    await mess.answer(text='', reply_markup=create_keyboard(add_menu_titles))



async def create_user(user_id: str):
    if res:=await get_user_total(user_id):
        print('Пользователь есть в базе. Его данные:')
        print(res)
    return res


def get_start_menu():
    menu_titles = (
        types.InlineKeyboardButton(text='Add...', callback_data='add_menu'),
        types.InlineKeyboardButton(text='Del...', callback_data='del_menu'),
        types.InlineKeyboardButton(text='Settings', callback_data='settings_menu'),
        types.InlineKeyboardButton(text='Clear', callback_data='clear_screen'),
        types.InlineKeyboardButton(text='Statistics', callback_data='user_statistics'),
    )

    # keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*menu_titles)
    # keyboard.add(*menu_titles)

    return keyboard


def create_keyboard(menu_titles: tuple):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*menu_titles)

    return keyboard




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

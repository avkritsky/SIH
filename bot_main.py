from decimal import Decimal

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from settings.api_key import APP_TOKEN

from controller.bot_data_work import get_user_total, add_user, get_user_data
from model.user_data_class import UserData
from controller.bot_redis_work import get_price


# TODO:
#  на старте ничего не показывать, кроме основного меню,
#  Статистика - выводит все имеемые криптовалюты, их цену в основной валюте пользователя, общую прибль:
#  получает данные пользователя из БД (хранение в редисе по юзер-ид),
#  Добавить значения - добаляет транзакцию,
#  Настройки - выбор основной валюты / иное,


bot = Bot(token=APP_TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())


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


@dp.message_handler(Text(equals=['Statistics', 'stat', 'стат']))
async def show_user_statistic(mess: Message):
    user_data: UserData = await get_user_data(str(mess.from_user.id))

    if not user_data.total:
        await mess.answer(text='Excuse me, You have not any valutes!')

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

    await mess.answer(text='\n'.join(user_stats_parts),
                      reply_markup=get_start_menu())



class AddMenuAutomat(StatesGroup):
    waiting_fot_spended_currency = State()
    waiting_fot_spended_currency_value = State()
    waiting_fot_received_currency = State()
    waiting_fot_received_currency_value = State()


# @dp.callback_query_handler(text='Add')
def register_handlers_for_add_menu(dp: Dispatcher):
    dp.register_message_handler(start_automat_for_add, commands='Add', state='*')
    dp.register_message_handler(automat_for_add_spended_currency, state=AddMenuAutomat.waiting_fot_spended_currency)
    dp.register_message_handler(automat_for_add_spended_value, state=AddMenuAutomat.waiting_fot_spended_currency_value)
    dp.register_message_handler(automat_for_add_received_currency, state=AddMenuAutomat.waiting_fot_received_currency)
    dp.register_message_handler(automat_for_add_received_value, state=AddMenuAutomat.waiting_fot_received_currency_value)


async def start_automat_for_add(mess: Message, state: FSMContext):
    await state.set_state(AddMenuAutomat.waiting_fot_spended_currency.state)
    await mess.answer('Введите название затраченной валюты (аббревиатуру):')


async def automat_for_add_spended_currency(mess: Message, state: FSMContext):
    print('her')
    # await mess.answer('Введите валюту которую вы потратили!')
    if mess.text.upper() not in ['RUB', ]:
        await mess.answer('Пока доступны только рубли для трат, введите RUB!')
        return
    print('Валюта принята')
    await state.update_data(spended_currency=mess.text.upper())

    # можно показать клаву

    await state.set_state(AddMenuAutomat.waiting_fot_spended_currency_value.state)
    await mess.answer('Теперь введите количество затраченной валюты')


async def automat_for_add_spended_value(mess: Message, state: FSMContext):
    if not mess.text.isdecimal():
        await mess.answer('Введите число или дробное число!')
        return

    print('Сумма принята')
    await state.update_data(spended_currency_val=mess.text)

    await state.set_state(AddMenuAutomat.waiting_fot_received_currency.state)
    await mess.answer('Введите валюту которую вы приобрели!')


async def automat_for_add_received_currency(mess: Message, state: FSMContext):
    if mess.text.upper() not in ['BTC', 'ETH']:
        await mess.answer('Пока доступны только битки и эфир для покупок, введите BTC или ETH!')
        return

    print('Полученная валюта принята')
    await state.update_data(received_currency=mess.text)

    await state.set_state(AddMenuAutomat.waiting_fot_received_currency_value.state)
    await mess.answer('Введите введите количество приобретенной валюты!')


async def automat_for_add_received_value(mess: Message, state: FSMContext):
    if not mess.text.isdecimal():
        await mess.answer('Введите число или дробное число!')
        return

    print('Полученное количество валюты принято')
    automat_data = await state.get_data()
    spended_cur = automat_data.get('spended_currency')
    spended_cur_val = automat_data.get('spended_currency_val')
    received_cur = automat_data.get('received_currency')

    await mess.answer(f'Вы фиктивно приобрели {mess.text} {received_cur} за жалкие {spended_cur_val} {spended_cur}!')
    await state.finish()




# @dp.message_handler(Text(equals='Add ...'))
# async def show_add_menu(mess: Message):
#     add_menu_titles = (
#         'Currency',
#         'Transaction',
#     )
#     await mess.answer(text='', reply_markup=create_keyboard(add_menu_titles))


async def create_user(user_id: str):
    if res:=await get_user_total(user_id):
        print('Пользователь есть в базе. Его данные:')
        print(res)
    return res


def get_start_menu():
    menu_titles = (
        # types.InlineKeyboardButton(text='Add...', callback_data='add_menu'),
        # types.InlineKeyboardButton(text='Del...', callback_data='del_menu'),
        # types.InlineKeyboardButton(text='Settings', callback_data='settings_menu'),
        # types.InlineKeyboardButton(text='Clear', callback_data='clear_screen'),
        # types.InlineKeyboardButton(text='Statistics', callback_data='user_statistics'),
        'Statistics',
        'Add',
        'Del',
        'Clear',
        'Settings',
    )

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*menu_titles)
    # keyboard.add(*menu_titles)

    return keyboard


def create_keyboard(menu_titles: tuple):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*menu_titles)

    return keyboard


register_handlers_for_add_menu(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

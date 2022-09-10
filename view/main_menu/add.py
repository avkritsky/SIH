from decimal import Decimal, InvalidOperation

from aiogram import Dispatcher, types
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from controller.bot_data_work import get_user_data, update_user_total_info, add_transaction
from controller.bot_redis_work import redis_get_currency_short_names, redis_get_crypto_short_names
from model.user_data_class import UserData
from model.transaction_data_class import Transaction
from view.common.keyboard import create_keyboard, get_start_menu



class AddMenuAutomat(StatesGroup):
    waiting_fot_spended_currency = State()
    waiting_fot_spended_currency_value = State()
    waiting_fot_received_currency = State()
    waiting_fot_received_currency_value = State()


def register_handlers_for_add_menu(dp: Dispatcher):
    dp.register_message_handler(start_automat_for_add, Text(equals=['Add']), state='*')
    dp.register_message_handler(automat_for_add_spended_currency, state=AddMenuAutomat.waiting_fot_spended_currency)
    dp.register_message_handler(automat_for_add_spended_value, state=AddMenuAutomat.waiting_fot_spended_currency_value)
    dp.register_message_handler(automat_for_add_received_currency, state=AddMenuAutomat.waiting_fot_received_currency)
    dp.register_message_handler(automat_for_add_received_value, state=AddMenuAutomat.waiting_fot_received_currency_value)


async def start_automat_for_add(mess: Message, state: FSMContext):
    await state.set_state(AddMenuAutomat.waiting_fot_spended_currency.state)

    user_data: UserData = await get_user_data(mess.from_user.id)

    crypto_names = await redis_get_crypto_short_names()
    currency_names = await redis_get_currency_short_names()

    await state.set_data({'user_data': user_data,
                          'currency': currency_names,
                          'crypto': crypto_names})

    await mess.answer('Введите название затраченной валюты (аббревиатуру).\n'
                      'Для отмены введите: Cancel, Отмена, cl',
                      reply_markup=create_keyboard(currency_names))


async def automat_for_add_spended_currency(mess: Message, state: FSMContext):
    if mess.text.upper() not in ['RUB', ]:
        await mess.answer('Пока доступны только рубли для трат, введите RUB!')
        return

    await state.update_data(spended_currency=mess.text.upper())

    await state.set_state(AddMenuAutomat.waiting_fot_spended_currency_value.state)
    await mess.answer('Теперь введите количество затраченной валюты',
                      reply_markup=types.ReplyKeyboardRemove())


async def automat_for_add_spended_value(mess: Message, state: FSMContext):
    if not check_for_decimal(mess.text):
        await mess.answer('Введите число или дробное число!')
        return

    await state.update_data(spended_currency_val=mess.text)
    automat_data = await state.get_data()
    crypto_names = automat_data.get('crypto', ['BTC', 'ETC'])

    await state.set_state(AddMenuAutomat.waiting_fot_received_currency.state)
    await mess.answer('Введите валюту которую вы приобрели!',
                      reply_markup=create_keyboard(crypto_names))


def check_for_decimal(checked_txt: str) -> bool:
    try:
        Decimal(checked_txt.replace(',', '.'))
        return True
    except InvalidOperation:
        return False


async def automat_for_add_received_currency(mess: Message, state: FSMContext):
    await state.update_data(received_currency=mess.text)

    await state.set_state(AddMenuAutomat.waiting_fot_received_currency_value.state)
    await mess.answer('Введите введите количество приобретенной валюты!',
                      reply_markup=types.ReplyKeyboardRemove())


async def automat_for_add_received_value(mess: Message, state: FSMContext):
    if not check_for_decimal(mess.text):
        await mess.answer('Введите число или дробное число!')
        return

    automat_data = await state.get_data()
    spended_cur = automat_data.get('spended_currency')
    spended_cur_val = automat_data.get('spended_currency_val')
    received_cur = automat_data.get('received_currency')
    received_cur_val = mess.text

    user_data: UserData = automat_data.get('user_data')

    key_for_spended = f'{spended_cur}:{received_cur}'

    # set defaults for total summs
    user_total_for_spend = user_data.total.setdefault(key_for_spended, '0')
    user_total_for_recei = user_data.total.setdefault(received_cur, '0')
    # summing users data with new transaction
    user_total_for_spend = Decimal(user_total_for_spend) + Decimal(spended_cur_val)
    user_total_for_recei = Decimal(user_total_for_recei) + Decimal(received_cur_val)
    # save to uset data new values
    if spended_cur == user_data.default_value:
        user_data.total[key_for_spended] = str(user_total_for_spend)
        user_data.total[received_cur] = str(user_total_for_recei)

    await add_new_transaction(mess.from_user.id, spended_cur, spended_cur_val, received_cur, received_cur_val)
    await update_user_total_info(mess.from_user.id, user_data.total)

    await mess.answer(f'Вы добавили запись о {received_cur_val} {received_cur} '
                      f'приобретенные за {spended_cur_val} {spended_cur}!'
                      f'\nТеперь у Вас всего: {user_total_for_recei} {received_cur}'
                      f'\nВсего потрачено: {user_total_for_spend} {spended_cur}',
                      reply_markup=get_start_menu())

    await state.finish()


async def add_new_transaction(user_id: int, spc: str, spcv: str, rpc: str, rpcv: str):

    transaction = Transaction().set_user_id(str(user_id)).set_spended_currency(spc).set_spended_count(spcv)
    transaction.set_received_currency(rpc).set_received_count(rpcv)

    await add_transaction(transaction)

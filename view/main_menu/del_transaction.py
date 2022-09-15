from datetime import datetime
from decimal import Decimal

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from controller.bot_data_work import db_get_user_data, db_update_user_total_info, db_del_user_transaction, db_get_user_transaction
from model.user_data_class import UserData
from view.common.keyboard import create_keyboard, get_start_menu



class DelMenuAutomat(StatesGroup):
    show_users_transactions = State()
    del_selected_transaction = State()

def register_handlers_for_del_menu(dp: Dispatcher):
    dp.register_message_handler(start_automat_for_del, Text(equals=['Del']), state='*')
    dp.register_message_handler(automat_for_del_transaction, state=DelMenuAutomat.del_selected_transaction)


async def start_automat_for_del(mess: Message, state: FSMContext):
    await state.set_state(DelMenuAutomat.del_selected_transaction.state)

    user_data: UserData = await db_get_user_data(mess.from_user.id)
    user_transactions = await db_get_user_transaction(str(mess.from_user.id))

    if not user_transactions:
        await mess.answer(f'You have not any transactions!',
                          reply_markup=get_start_menu())
        await state.finish()
        return


    user_transactions = {
        (f'{datetime.fromtimestamp(transaction[2])}: {transaction[4]} {transaction[3]} '
        f'for {transaction[6]} {transaction[5]}'): transaction
        for transaction in user_transactions
    }

    transaction_keyboard = create_keyboard(tuple(user_transactions.keys()), row_size=1)

    await state.set_data({'user_data': user_data,
                          'user_transactions': user_transactions,
                          })

    await mess.answer('Выберите вашу транзакцию для удаления (кнопка меню)\n'
                      'Для отмены введите: Cancel, Отмена, cl',
                      reply_markup=transaction_keyboard)


async def automat_for_del_transaction(mess: Message, state: FSMContext):
    automat_data = await state.get_data()

    user_data: UserData = automat_data.get('user_data', {})
    user_transactions = automat_data.get('user_transactions', {})

    if mess.text not in user_transactions:
        await mess.answer('Выберите транзакцию из меню или введите Cancel/Отмена для отмены!')
        return

    try:
        trans_id, *_, trans_sc, trans_scv, trans_rc, trans_rcv = user_transactions.get(mess.text)
    except Exception as e:
        print(f'{e=}')
        return

    key_for_spended = f'{user_data.default_value}:{trans_rc}'

    user_data.total[key_for_spended] = str(Decimal(user_data.total.get(key_for_spended)) - Decimal(trans_scv))
    user_data.total[trans_rc] = str(Decimal(user_data.total.get(trans_rc)) - Decimal(trans_rcv))

    await db_update_user_total_info(mess.from_user.id, user_data.total)
    del_res = await db_del_user_transaction(mess.from_user.id, trans_id)

    await mess.answer(f'Транзакция {("неуспешно","успешно",)[del_res]} была удалена!',
                      reply_markup=get_start_menu())
    await state.finish()
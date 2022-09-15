from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from view.common.keyboard import create_keyboard
from view.additional_menu.profit_statistics.root_profit_statistics import show_profit_statistics




class AdditionalMenuAutomat(StatesGroup):
    show_profit_statistic = State()

def register_handlers_for_additional_menu(dp: Dispatcher):
    dp.register_message_handler(start_automat_for_additional_menu, Text(equals=['Additional']), state='*')
    dp.register_message_handler(start_automat_for_show_profit_statistics, Text(equals=['Profit statistics']),
                                state=AdditionalMenuAutomat.show_profit_statistic)
    # dp.register_message_handler(start_automat_for_additional_menu, state=AdditionalMenuAutomat.show_profit_statistic)


async def start_automat_for_additional_menu(mess: Message, state: FSMContext):
    await state.set_state(AdditionalMenuAutomat.show_profit_statistic.state)

    additional_menu = [
        'Profit statistics',
    ]

    keyboard = create_keyboard(additional_menu, row_size=1)

    await mess.answer('Select interesting action', reply_markup=keyboard)


async def start_automat_for_show_profit_statistics(mess: Message, state: FSMContext):
    await state.set_state(AdditionalMenuAutomat.show_profit_statistic.state)

    await show_profit_statistics(mess)

    await state.finish()

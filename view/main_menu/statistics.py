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


async def create_user_stats(mess: Message):

    user_data: UserData = await get_user_data(str(mess.from_user.id))

    if not user_data.total:
        await mess.answer(text='Excuse me, You have not any currency!')
        return

    user_stats_parts = []

    spended = Decimal(user_data.total.get(user_data.default_value, 0))
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

    return user_stats_parts

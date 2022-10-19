from decimal import Decimal
from datetime import datetime, timedelta
from os import remove

from aiogram.types import Message
from aiogram.types.input_file import InputFile
import numpy as np
import matplotlib.pyplot as plt

from controller.bot_data_work import db_get_user_data, db_add_user_statistics
from model.user_data_class import UserData
from controller.bot_redis_work import get_price, get_all_keys, set_data_to_redis
from settings.api_key import TEMP_PLOT_CHAT
from view.common.keyboard import get_start_menu


async def create_user_stats(mess: Message):

    user_data: UserData = await db_get_user_data(str(mess.from_user.id))

    if not user_data.total:
        await mess.answer(text='Excuse me, You have not any currency!')
        return False

    user_stats_parts = []
    user_data_for_plt = {}

    all_getted, all_spended = await calculate_stats(user_data, user_stats_parts, user_data_for_plt)
    await add_summary_data_to_stats(user_data, all_getted, all_spended, user_stats_parts, user_data_for_plt)

    plot = await create_and_upload_plot_stat(mess, user_data_for_plt, user_data.default_value)

    if plot:
        plot_file = InputFile(plot)
        await mess.bot.send_photo(mess.from_user.id,
                                  photo=plot_file,
                                  caption='\n'.join(user_stats_parts),
                                  reply_markup=get_start_menu())

        remove_plot_file_from_server(plot)
    else:
        await mess.answer(text='\n'.join(user_stats_parts),
                          reply_markup=get_start_menu())


async def add_summary_data_to_stats(user_data: UserData,
                          all_getted: Decimal,
                          all_spended: Decimal,
                          user_stats_parts: list,
                          user_data_for_plt: dict):
    user_data_for_plt['SUM:S'] = all_spended
    user_data_for_plt['SUM:R'] = all_getted

    all_sum, all_prc, emoji = calculate_profit_and_generate_emoji(all_spended, all_getted)
    user_stats_parts.append(f'{emoji} Summary profit: {all_sum} {user_data.default_value} or {all_prc} %')

    await add_new_statistics_to_user_stats_db(user_data, all_sum, all_prc)


async def add_new_statistics_to_user_stats_db(user_data: UserData, all_sum: Decimal, all_prc: Decimal):
    await add_data_to_user_stats(user_data.user_id, summ_val=str(all_sum), summ_prc=str(all_prc))


async def calculate_stats(user_data: UserData,
                          user_stats_parts: list,
                          user_data_for_plt: dict) -> tuple:

    usd_price = await get_usd_price()

    all_spended = Decimal(0)
    all_getted = Decimal(0)

    for valute_name, valute_val in user_data.total.items():

        if ':' in valute_name or valute_val == '0':
            continue

        getted = Decimal(0)

        valute_price_data = await get_price(valute_name.upper())

        if not valute_price_data:
            continue

        valute_price = valute_price_data.get('price', 0)

        if not valute_price:
            valute_price = valute_price_data.get('Value')

        usd_val = (Decimal(str(valute_val)) * Decimal(str(valute_price))).quantize(Decimal("1.00"))
        user_val = (usd_val * Decimal(str(usd_price))).quantize(Decimal('1.00'))
        getted += user_val
        all_getted += getted

        user_stats_parts.append(
            f'{valute_name.upper()}:'
            f' {valute_val} '
            f'| {usd_val} $'
            f'| {user_val} {user_data.default_value}'
        )

        spended = calculate_spend_value(user_data, valute_name)
        all_spended += spended

        profit, profit_perc, emoji = calculate_profit_and_generate_emoji(spended, getted)

        user_stats_parts.append(
            f'{emoji} Profit: {profit} {user_data.default_value} or {profit_perc} %\n'
        )

        # для постройки графиков
        user_data_for_plt[f'{valute_name}:S'] = spended
        user_data_for_plt[f'{valute_name}:R'] = getted

    return all_getted, all_spended


def calculate_spend_value(user_data: UserData, valute_name: str) -> Decimal:
    spended = user_data.total.get(f'{user_data.default_value}:{valute_name}')

    if spended is None:
        return Decimal(0)

    return Decimal(spended)


async def get_usd_price() -> str:
    raw_usd_price = await get_price('USD')
    return raw_usd_price.get('Value')


def calculate_profit_and_generate_emoji(spended: Decimal, getted: Decimal) -> tuple:
    all_sum = (getted - spended).quantize(Decimal("1.00"))
    all_prc = (((getted - spended) / spended) * 100).quantize(Decimal("1.00"))
    emoji = b"\xE2\x8F\xAB".decode('utf-8') if all_sum >= 0 else b"\xE2\x8F\xAC".decode('utf-8')

    return all_sum, all_prc, emoji



async def create_and_upload_plot_stat(mess: Message, user_data_plt: dict, user_default_cur: str = 'RUB') -> str:

    plot_file_name = generate_plot(user_data_plt, user_default_cur, mess.from_user.id, title='Spend and received value')

    # plot_file_id = await upload_user_plot_to_default_chat_for_file_id(mess, plot_file_name)

    return plot_file_name


def remove_plot_file_from_server(file_name: str):
    remove(file_name)


async def upload_user_plot_to_default_chat_for_file_id(mess: Message, plot_file_name: str) -> str:
    """Try upload user's plot to default chat and get file_id, else send plot to user and return empty str"""
    plot = InputFile(plot_file_name)
    try:
        plot_response = await mess.bot.send_photo(TEMP_PLOT_CHAT, plot)
        user_stats_plot_id = plot_response.photo[-1]['file_id']
        remove(plot_file_name)
    except Exception as e:
        await mess.bot.send_message(TEMP_PLOT_CHAT, f'Error at generating user stats plot: {e=}. {mess.from_user.id}')
        await mess.bot.send_photo(mess.chat.id, plot)
        return ''
    else:
        return user_stats_plot_id


def generate_plot(user_data_plt: dict, y_label: str, user_id: int, title: str) -> str:
    """Generate plot for user stats and return plots file name"""

    plt.cla()
    plt.clf()

    colors: list = generate_colors_for_stats(user_data_plt)

    y_pos = np.arange(len(user_data_plt))

    fig, ax = plt.subplots(1)

    ax.bar(y_pos, list(user_data_plt.values()), align='center', alpha=0.5, color=colors)
    max_value = max(user_data_plt.values())
    ax.set_ylim(0, max_value + max_value // 10)

    plt.xticks(y_pos, tuple(user_data_plt.keys()), rotation=45)
    plt.ylabel(y_label)
    plt.title(f'{title} at {datetime.now().replace(microsecond=0)}')

    add_descriptions_for_plot_bars(plt, user_data_plt)

    name_plot_file = generate_plot_name(user_id)
    plt.savefig(name_plot_file)

    return name_plot_file


def generate_plot_name(user_id: int):
    return f'data/tmp_plot/{user_id}_{int(datetime.timestamp(datetime.now()))}.png'


def generate_colors_for_stats(user_data_plt: dict) -> list:
    """Generate colors for stats bars"""
    colors = []
    summary = 0
    for i, value in enumerate(user_data_plt.values()):
        if i % 2 == 0:
            colors.append('blue')
            summary = value
        else:
            if value - summary >= 0:
                colors.append('green')
            else:
                colors.append('red')
    return colors


def add_descriptions_for_plot_bars(plt, user_data_plt: dict):
    """Add descriptions for bars with color differences"""
    summary = 0
    for i, value in enumerate(user_data_plt.values()):
        if i % 2 == 0:
            plt.text(x=i-0.4, y=int(value), s=int(value), size=12)
            summary = int(value)
        else:
            summary = int(value) - summary
            if summary >= 0:
                text = f'{int(value)}\n+{summary}'
                color = 'green'
            else:
                text = f'{int(value)}\n{summary}'
                color = 'red'
            plt.text(x=i-0.4, y=int(value), s=text, size=11, color=color)


async def add_data_to_user_stats(user_id: str, summ_val: str, summ_prc: str):
    """Add user stats in DB USER_STATS"""
    # if not await checked_user_stat_already_added(user_id):
    #     return
    await db_add_user_statistics(user_id, summ_val, summ_prc)


async def checked_user_stat_already_added(user_id: str) -> bool:
    """Checked that user stats already added in DB, if not, add data to redis"""
    today = int(datetime.timestamp(datetime.now().replace(hour=0, minute=0, second=0)))
    today_key = f'{today}:{user_id}'

    checked_user_data = await get_all_keys(mask=today_key)

    if checked_user_data:
        return False

    await set_data_to_redis(data={today_key: ''}, ttl=timedelta(days=2))
    return True

from decimal import Decimal
from datetime import datetime, timedelta

from aiogram.types import Message
from aiogram.types.input_file import InputFile
import numpy as np
import matplotlib.pyplot as plt

from controller.bot_data_work import get_user_data, add_user_stat
from model.user_data_class import UserData
from controller.bot_redis_work import get_price, get_all_keys, set_data_to_redis


async def create_user_stats(mess: Message):

    user_data: UserData = await get_user_data(str(mess.from_user.id))

    if not user_data.total:
        await mess.answer(text='Excuse me, You have not any currency!')
        return False

    user_stats_parts = []
    user_data_for_plt = {}

    all_spended = Decimal(0)
    all_getted = Decimal(0)

    for valute_name, valute_val in user_data.total.items():
        if ':' in valute_name:
            continue

        getted = Decimal(0)

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
        all_getted += getted

        user_stats_parts.append(
            f'{valute_name.upper()}:'
            f' {valute_val} '
            f'| {usd_val} $'
            f'| {user_val} {user_data.default_value}'
        )

        spended = user_data.total.get(f'{user_data.default_value}:{valute_name}')

        if spended is None:
            continue

        spended = Decimal(spended)
        all_spended += spended

        user_stats_parts.append(
            f'=== Profit: {(getted - spended).quantize(Decimal("1.00"))} {user_data.default_value} '
            f'or {(((getted - spended) / spended) * 100).quantize(Decimal("1.00"))} %\n'
        )

        # для постройки графиков
        user_data_for_plt[f'{valute_name}:S'] = spended
        user_data_for_plt[f'{valute_name}:R'] = getted

    user_data_for_plt['SUM:S'] = all_spended
    user_data_for_plt['SUM:R'] = all_getted

    all_sum = (all_getted - all_spended).quantize(Decimal("1.00"))
    all_prc = (((all_getted - all_spended) / all_spended) * 100).quantize(Decimal("1.00"))
    user_stats_parts.append(f'Summary profit: {all_sum} {user_data.default_value} or {all_prc} %')

    await create_and_upload_plot_stat(mess, user_data_for_plt, user_data.default_value)


    await add_data_to_user_stats(str(mess.from_user.id),
                                 summ_val=str(all_sum),
                                 summ_prc=str(all_prc))

    return user_stats_parts


async def create_and_upload_plot_stat(mess: Message, user_data_plt: dict, user_default_cur: str = 'RUB'):
    for k, v in user_data_plt.items():
        print(k, v)

    colors = []
    for i, value in enumerate(user_data_plt.values()):
        if (i+1) % 2 == 0:
            if value - summary >= 0:
                colors.append('green')
            else:
                colors.append('red')
        else:
            colors.append('blue')
            summary = value

    y_pos = np.arange(len(user_data_plt))

    plt.bar(y_pos, list(user_data_plt.values()), align='center', alpha=0.5, color=colors)
    plt.xticks(y_pos, tuple(user_data_plt.keys()), rotation=45)
    plt.ylabel(user_default_cur)
    plt.title('Spend and received value')

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

    name_plot_file = f'data/tmp_plot/{mess.from_user.id}_{int(datetime.timestamp(datetime.now()))}.png'
    print(f'{name_plot_file=}')
    plt.savefig(name_plot_file)

    photo = InputFile(name_plot_file)
    photo_response = await mess.bot.send_photo(mess.chat.id, photo)
    # Узнать как залить в другой чат, получить id и засунуть в скрытую ссылку.
    # добавить удаление после загрузки!!!



async def add_data_to_user_stats(user_id: str, summ_val: str, summ_prc: str):
    today = int(datetime.timestamp(datetime.now().replace(hour=0, minute=0, second=0)))
    today_key = f'{today}:{user_id}'

    checked_user_data = await get_all_keys(mask=today_key)

    if checked_user_data:
        return

    await set_data_to_redis(data={today_key: ''}, ttl=timedelta(days=2))
    await add_user_stat(user_id, summ_val, summ_prc)


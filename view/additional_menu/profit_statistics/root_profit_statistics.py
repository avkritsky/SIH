from datetime import datetime, timedelta
from decimal import Decimal

from aiogram.types import Message
from aiogram.types.input_file import InputFile
import matplotlib.pyplot as plt
import numpy as np

from controller.bot_data_work import db_get_user_statistics
from view.common.keyboard import get_start_menu
from view.main_menu.statistics import remove_plot_file_from_server, generate_plot_name


async def show_profit_statistics(mess: Message):

    raw_stats = await db_get_user_statistics(user_id=str(mess.from_user.id))

    stats = format_data_for_plot(raw_stats)

    plot = generate_plot(stats, 'Perc., %', mess.from_user.id, title='Profit statistic')

    await send_plot_to_user_and_del_file(mess, plot)


async def send_plot_to_user_and_del_file(mess: Message, plot: str):
    """Send photo and delete file from server"""
    plot_for_show = InputFile(plot)

    await mess.bot.send_photo(chat_id=mess.from_user.id,
                              photo=plot_for_show,
                              caption='Your profit statistics.',
                              reply_markup=get_start_menu())

    remove_plot_file_from_server(plot)



def format_data_for_plot(raw_data: list) -> dict:
    stats = {}
    all_stats = {}
    for item in raw_data:
        _, _, date_ts, _, profit_perc = item
        if datetime.timestamp(datetime.now()) - date_ts > 7*24*60*60:
            continue

        stats[datetime.isoformat(datetime.fromtimestamp(date_ts))[:10]] = Decimal(profit_perc)

        key = str(datetime.date(datetime.fromtimestamp(date_ts)))
        profit_perc = Decimal(profit_perc)
        stats_item: dict = all_stats.setdefault(key, {'vals': [], 'max': 0, 'min': 0})
        stats_item['vals'].append(profit_perc)
        stats_item['max'] = max(stats_item['vals'])
        stats_item['min'] = min(stats_item['vals'])
    return all_stats



def generate_plot(user_data_plt: dict, y_label: str, user_id: int, title: str) -> str:
    """Generate plot for user stats and return plots file name"""

    plt.cla()
    plt.clf()

    values = list(user_data_plt.values())

    y_pos = np.arange(len(user_data_plt))

    fig, ax = plt.subplots(1)

    max_vals = [item.get('max') for item in user_data_plt.values()]
    min_vals = [item.get('min') for item in user_data_plt.values()]

    # max_vals = []
    # for item in user_data_plt.values():
    #     val = item.get('max')
    #     if val < 0:
    #         val = item.get('min')
    #     max_vals.append(val)
    #
    # min_vals = []
    # for item in user_data_plt.values():
    #     val = item.get('min')
    #     if val < 0:
    #         val = item.get('max')
    #     min_vals.append(val)

    height_vals = [
        abs(abs(max_val) - abs(min_val))
        if (max_val:=item.get('max')) != (min_val:=item.get('min'))
        else (Decimal('0.5') if max_val < 0 else Decimal('-0.5'))
        for item in user_data_plt.values()
    ]

    # height_vals = [height_val
    #                if abs(height_val) >= Decimal('0.2')
    #                else (Decimal('0.2') if height_val < 0 else Decimal('-0.2'))
    #                for height_val in height_vals]

    print(f'{height_vals}')

    print(f'{max_vals=}\n{min_vals=}')

    ax.bar(y_pos,
           height=height_vals,
           bottom=min_vals,
           align='center',
           alpha=0.5,
           color=create_colors_for_max_values(max_vals))

    max_value = max(max_vals) + 2
    min_value = (min_value if (min_value := min(min_vals)) < 0 else 0) - 2
    ax.set_ylim(min_value, max_value)

    if min_value < 0:
        ax.axhline(0, color="black", ls="--")

    plt.xticks(y_pos, tuple(user_data_plt.keys()), rotation=25)
    plt.ylabel(y_label)
    plt.title(f'{title} from {datetime.now().date()-timedelta(days=6)} to {datetime.now().date()}')

    add_descriptions_for_plot_bars(plt, user_data_plt)

    name_plot_file = generate_plot_name(user_id)
    plt.savefig(name_plot_file)

    return name_plot_file


def create_colors_for_max_values(values: list) -> list:
    maximus = max(values)
    minimus = min(values)

    colors = []

    for val in values:
        if minimus < val < maximus:
            colors.append('blue')
        elif val == maximus:
            colors.append('green')
        else:
            colors.append('red')

    return colors


def add_descriptions_for_plot_bars(plt, user_data_plt: dict):
    """Add descriptions for bars"""

    for i, item in enumerate(user_data_plt.values()):
        max_value = item.get('max')
        min_value = item.get('min')

        if max_value < 0:
            min_value, max_value = max_value, min_value

        additional_for_space = Decimal(-1 * (-0.5 if max_value >= 0 else 0.5))

        plt.text(x=i-0.2, y=max_value+additional_for_space, s=max_value, size=6, color='black')

        if min_value != max_value:
            plt.text(x=i-0.2, y=min_value-additional_for_space, s=min_value, size=6, color='black')

from datetime import datetime
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
    for item in raw_data:
        _, _, date_ts, _, prodit_perc = item
        stats[datetime.isoformat(datetime.fromtimestamp(date_ts))[:10]] = Decimal(prodit_perc)
    return stats



def generate_plot(user_data_plt: dict, y_label: str, user_id: int, title: str) -> str:
    """Generate plot for user stats and return plots file name"""

    plt.cla()
    plt.clf()

    values = list(user_data_plt.values())

    y_pos = np.arange(len(user_data_plt))

    fig, ax = plt.subplots(1)

    ax.bar(y_pos, values, align='center', alpha=0.5, color=create_colors_for_max_values(values))
    max_value = max(user_data_plt.values())
    ax.set_ylim(0, max_value + max_value // 10)

    plt.xticks(y_pos, tuple(user_data_plt.keys()), rotation=25)
    plt.ylabel(y_label)
    plt.title(title)

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

    for i, value in enumerate(user_data_plt.values()):
        plt.text(x=i-0.2, y=int(value)+1, s=value, size=11, color='black')

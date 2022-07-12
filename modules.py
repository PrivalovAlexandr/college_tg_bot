import sqlite3

from aiogram import types
from requests import get
from copy import deepcopy

from key import key
from config import *



def group_list(corpus: str, course: str) -> list:
#   // list of group by specified parameters
    data_list = get('https://bot-t-s.nttek.ru/rest-api/available').json()
    rasp = get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()
    group_list = [i for i in rasp[corpus] if i[0] == course]
    return group_list      

def course_chain (user_group: str) -> list:
#   // course chain for function 'Change course'
    chain = []
    data_list = get('https://bot-t-s.nttek.ru/rest-api/available').json()
    rasp = get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()
    for i in rasp:
        for j in rasp[i]:
            if j[1:] == user_group[1:]:
                chain.append(j)
    chain.remove(user_group)
    return chain

def get_keyboard (buttons: list | tuple, one_time: bool = False):
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, 
        row_width=4, 
        one_time_keyboard=one_time)

    if 'Назад' in buttons:
        keyboard.add(*buttons[:-1])
        keyboard.add(buttons[-1])
    else:
        keyboard.add(*buttons)

    return keyboard

def data_base(sql:str, value: tuple = ()):
#   // sending database queries
    con = sqlite3.connect('tg_bot.db')
    cur = con.cursor()
    if 'SELECT' in sql:
        if value:
            query = cur.execute(sql, value).fetchall()
        else:
            query = cur.execute(sql).fetchall()
        con.close()
        return query
    else:
        if value:
            cur.execute(sql, value)
        else:
            cur.execute(sql)
        con.commit()
        con.close()

def begin(user_id: int):
    cache_dict[user_id] = [1, []] # [step:int, memory:list]
    user_trigger[user_id] = deepcopy(trigger_list)
    user_trigger[user_id]['Reg'] = False
    user_trigger[user_id]['AfterRestart'] = True

def users_to_msg(start_msg:str, array_to_message:list|tuple, cache_dict:dict, teacher:bool=0) -> str:
    for user in array_to_message:
        if not teacher:
            start_msg += f'id{user[0]} - @{cache_dict[user[0]][-1]}\n'
        else:
            start_msg += f'id{user[0]} - {cache_dict[user[0]][2]} - @{cache_dict[user[0]][-1]}\n'
    return start_msg
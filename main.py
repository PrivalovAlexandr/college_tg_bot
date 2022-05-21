import logging
import sqlite3

from key import key
from config import *

from aiogram import Bot, Dispatcher, executor, types
from requests import get

def group_list(corpus: str, course: str):
#   // список групп по заданному корпусу и курсу
    data_list = get('https://bot-t-s.nttek.ru/rest-api/available').json()
    rasp = get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()
    group_list = [i for i in rasp[corpus] if i[0] == course]
    return group_list      

def create_keyboard(keyboard_array):
    if keyboard_array == False:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = 0
        if len(keyboard_array) > 8:
            max_button = 3
        elif 'Своё расписание' in keyboard_array:
            max_button = 2
        else:
            max_button = 4
        for i in keyboard_array:
            if i != 'Назад':
                if button < max_button:
                    keyboard.add (i)
                else:
                    keyboard.row()
                    keyboard.add (i)
                    button = 0
            else:
                keyboard.row()
                keyboard.add (i)
            button += 1
    else:
        keyboard = types.ReplyKeyboardRemove()
    return keyboard

def data_base(sql:str, value: tuple = ()):
#   // отправка запросов к базе данных
    con = sqlite3.connect('tg_bot.db')
    cur = con.cursor()
    if value:
        cur.execute(sql, value)
    else:
        if 'SELECT' in sql:
            query = cur.execute(sql).fetchall()
            con.close()
            return query
        else:
            cur.execute(sql)
    con.commit()
    con.close()

#   //    синхронизация с бд    //

users = data_base('SELECT * FROM users')
for i in users:
    cache_dict[i[0]] = list(i)


#   //  Configure logging   //

logging.basicConfig(level=logging.INFO)

#   //  Initialize bot and dispatcher   //

bot = Bot(token=key)
dp = Dispatcher(bot)


#   //    bot    //

@dp.message_handler(lambda message: message['from']['id'] not in cache_dict)
#   // проверка регистрации
async def reg_user(message: types.Message):
    cache_dict[message['from']['id']] = 1
    Trigger['Main'] = False
    await message.answer('Выберите роль', reply_markup=create_keyboard(role))

#   //  основной функционал //

@dp.message_handler(lambda message: Trigger['Main'] and message.text in menu_key)
async def menu(message: types.Message):
    if message.text == 'Расписание':
        await message.answer('Расписание')
    elif message.text == 'Своё расписание':
        await message.answer('Своё расписание')
    elif message.text == 'Профиль':
        await message.answer('Профиль')
    elif message.text == 'Админ':
        await message.answer('Админ')

#   // регистрация  //

@dp.message_handler(lambda message:cache_dict[message['from']['id']] == 1 and message.text.capitalize() in role)
async def reg_role(message: types.Message):
    cache_dict[message['from']['id']] = 2
    memory.append(message.text.capitalize())
    if message.text.capitalize() == 'Студент':
        await message.answer('Выберите корпус')
    else:
        await message.answer('Введите свою фамилию')

@dp.message_handler(lambda message: cache_dict[message['from']['id']] == 2)
async def reg_corpus(message: types.Message):
    if memory[0] == 'Студент':
        if message.text.capitalize() in corpus:
            cache_dict[message['from']['id']] = 3
            memory.append(message.text.capitalize())
            await message.answer('Выберите курс')
    else:
        if not Trigger['Send']:
            memory.append(message.text.capitalize())
            Trigger['Send'] = True
            await message.answer(f'Ваша фамилия: {message.text.capitalize()}. Все верно?')
        else:
            if message.text.capitalize() in ['Да', 'Нет']:
                if message.text.capitalize() == 'Да':
                    cache_dict[message['from']['id']] = 5
                    await message.answer(f'Вы хотете завершить регистрацию с этими данными?\n\nРоль: {memory[0]}\nФамилия: {memory[1]}')
                else:
                    del memory[1]
                    Trigger['Send'] = False
                    await message.answer('Введите фамилию ещё раз')

@dp.message_handler(lambda message: cache_dict[message['from']['id']] == 3 and message.text in course)
async def reg_course (message: types.Message):
    memory.append(message.text)
    memory.append(group_list(memory[1], message.text))
    cache_dict[message['from']['id']] = 4
    await message.answer(f'Выберите группу\n\n{memory[3]}')

@dp.message_handler(lambda message: cache_dict[message['from']['id']] == 4 and message.text.upper() in memory[3])
async def reg_group(message: types.Message):
    memory[3] = message.text.upper()
    cache_dict[message['from']['id']] = 5
    await message.answer(f'Вы хотете завершить регистрацию с этими данными?\n\nРоль: {memory[0]}\nГруппа: {memory[3]}')

@dp.message_handler(lambda message: cache_dict[message['from']['id']] == 5 and message.text.capitalize() in ['Да', 'Нет'])
async def reg_confirm (message: types.Message):
    if message.text.capitalize() == 'Да':
        if message['from']['id'] in admin_list:
            admin = True
        else:
            admin = False
        if memory[0] == 'Студент':
            last_name = None
            corpus = memory[1]
            group = memory[3]
        else:
            last_name = memory[1]
            corpus = None
            group = None
        cache_dict[message['from']['id']] = [message['from']['id'], memory[0], last_name, corpus, group, admin]
        data_base('INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)', tuple(cache_dict[message['from']['id']]))
        Trigger['Main'] = True
        await message.answer(f'гатова\n\n {cache_dict}', reply_markup=create_keyboard(menu_key))
    else:
        memory.clear()
        cache_dict[message['from']['id']] = 1
        await message.answer('Выберите роль', reply_markup=create_keyboard(role))
        


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
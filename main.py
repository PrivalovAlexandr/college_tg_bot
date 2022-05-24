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
    if keyboard_array is False:
        keyboard = types.ReplyKeyboardRemove()
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
        if 'Назад' in keyboard_array:
            keyboard.add(*keyboard_array[:-1])
            keyboard.add(keyboard_array[-1])
        elif 'Своё расписание' in keyboard_array:
            keyboard.add(*keyboard_array[:2])
            keyboard.add(*keyboard_array[2:])
        else:
            keyboard.add(*keyboard_array)
    return keyboard

def switch_trigger(position:str, next:str):
    Trigger[position] = False
    Trigger[next] = True

def course_chain (user_group: str):
#   // цепочки курсов
    chain = []
    data_list = get('https://bot-t-s.nttek.ru/rest-api/available').json()
    rasp = get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()
    for i in rasp:
        for j in rasp[i]:
            if j[1:] == user_group[1:]:
                chain.append(j)
    chain.remove(user_group)
    return chain

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

@dp.message_handler(lambda _: Trigger['Main'])
async def menu(message: types.Message):
    if message.text.capitalize() == 'Расписание':
        switch_trigger('Main', 'Rasp')
        await message.answer('Расписание', reply_markup=create_keyboard(rasp_key))
    elif message.text.capitalize() == 'Своё расписание':
        await message.answer('Своё расписание')
    elif message.text.capitalize() == 'Профиль':
        msg = f"Ваш профиль\n\nРоль: {cache_dict[message.from_user.id][1]}\n"
        if cache_dict[message.from_user.id][1] == 'Студент':
            profile_key = profile[:]
            del profile_key[2]
            msg += f'Группа {cache_dict[message.from_user.id][4]}'
        else:
            profile_key = profile[:]
            del profile_key[1]
            msg += f'Фамилия {cache_dict[message.from_user.id][2]}'
        if cache_dict[message.from_user.id][5]:
            msg += '\n\nАдмин'
        switch_trigger('Main', 'Profile')
        await message.answer(msg, reply_markup=create_keyboard(profile_key))
    elif message.text.capitalize() == 'Админ':
        switch_trigger('Main', 'Admin')
        await message.answer('Админ', reply_markup=create_keyboard(admin_key))

@dp.message_handler(lambda _: Trigger['Rasp'])
async def menu_rasp(message: types.Message):
    if message.text.capitalize() == '':
        pass
    elif message.text.capitalize() == 'Назад':
        switch_trigger('Rasp', 'Main')
        await message.answer('Главное меню', reply_markup = create_keyboard(menu_key))


@dp.message_handler(lambda _: Trigger['Profile'])
async def menu_profile(message: types.Message):
    if message.text.capitalize() == 'Сбросить профиль':
        Trigger['Profile'] = False
        data_base('DELETE FROM users WHERE id = ?', (message.from_user.id, ))
        cache_dict[message.from_user.id] = 1
        await message.answer('Выберите роль', reply_markup=create_keyboard(role))
    elif message.text.capitalize() == 'Изменить курс' and cache_dict[message.from_user.id][1] == 'Студент':
        switch_trigger('Profile', 'Change_course')
        memory.append(course_chain(cache_dict[message.from_user.id][4]))
        await message.answer('Выберите курс', reply_markup=create_keyboard(memory[0]))
    elif message.text.capitalize() == 'Изменить фамилию' and cache_dict[message.from_user.id][1] == 'Преподаватель':
        switch_trigger('Profile', 'Change_surname')
        await message.answer('Введите фамилию', reply_markup=create_keyboard(False))
    elif message.text.capitalize() == 'Назад':
        switch_trigger('Profile', 'Main')
        await message.answer('Главное меню', reply_markup = create_keyboard(menu_key))

@dp.message_handler(lambda _: Trigger['Change_course'])
async def change_course(message: types.Message):
    if message.text.upper() in memory[0]:
        cache_dict[message.from_user.id][4] = message.text.upper()
        data_base(
            "UPDATE users SET 'group' = ? WHERE id = ?",
            (message.text.upper(), message.from_user.id))
        memory.clear()
        switch_trigger('Change_course', 'Main')
        await message.answer('Главное меню', reply_markup=create_keyboard(menu_key))

@dp.message_handler(lambda _: Trigger['Change_surname'])
async def change_surname(message: types.Message):
    if not Trigger['Send']:
        memory.append(message.text.capitalize())
        Trigger['Send'] = True
        await message.answer(
            f'Ваша фамилия: {message.text.capitalize()}. Все верно?',
            reply_markup=create_keyboard(['Да', 'Нет']))
    else:
        if message.text.capitalize() in ['Да', 'Нет']:
            if message.text.capitalize() == 'Да':
                cache_dict[message.from_user.id][2] = memory[0]
                Trigger['Send'] = False
                data_base("UPDATE users SET 'last_name' = ? WHERE id = ?", (memory[0], message.from_user.id))
                switch_trigger('Change_surname', 'Main')
                memory.clear()
                await message.answer('Главное меню', reply_markup=create_keyboard(menu_key))
            else:
                del memory[0]
                Trigger['Send'] = False
                await message.answer('Введите фамилию ещё раз', reply_markup=create_keyboard(False))

@dp.message_handler(lambda _: Trigger['Admin'])
async def menu_admin(message: types.Message):
    if message.text.capitalize() == '':
        pass
    elif message.text.capitalize() == 'Назад':
        switch_trigger('Admin', 'Main')
        await message.answer('Главное меню', reply_markup = create_keyboard(menu_key))

#   // регистрация  //

@dp.message_handler(lambda message:cache_dict[message.from_user.id] == 1)
async def reg_role(message: types.Message):
    if message.text.capitalize() in role:
        cache_dict[message.from_user.id] = 2
        memory.append(message.text.capitalize())
        if message.text.capitalize() == 'Студент':
            await message.answer('Выберите корпус', reply_markup=create_keyboard(corpus))
        else:
            await message.answer('Введите свою фамилию', reply_markup=create_keyboard(False))

@dp.message_handler(lambda message: cache_dict[message.from_user.id] == 2)
async def reg_corpus(message: types.Message):
    if memory[0] == 'Студент':
        if message.text.capitalize() in corpus:
            cache_dict[message.from_user.id] = 3
            memory.append(message.text.capitalize())
            await message.answer('Выберите курс', reply_markup=create_keyboard(course))
    else:
        if not Trigger['Send']:
            memory.append(message.text.capitalize())
            Trigger['Send'] = True
            await message.answer(
                f'Ваша фамилия: {message.text.capitalize()}. Все верно?',
                reply_markup=create_keyboard(['Да', 'Нет']))
        else:
            if message.text.capitalize() in ['Да', 'Нет']:
                if message.text.capitalize() == 'Да':
                    cache_dict[message.from_user.id] = 5
                    Trigger['Send'] = False
                    await message.answer(
                        f'Вы хотете завершить регистрацию с этими данными?\n\nРоль: {memory[0]}\nФамилия: {memory[1]}')
                else:
                    del memory[1]
                    Trigger['Send'] = False
                    await message.answer('Введите фамилию ещё раз', reply_markup=create_keyboard(False))

@dp.message_handler(lambda message: cache_dict[message.from_user.id] == 3)
async def reg_course (message: types.Message):
    if message.text in course:
        memory.append(message.text)
        memory.append(group_list(memory[1], message.text))
        cache_dict[message.from_user.id] = 4
        await message.answer(f'Выберите группу', reply_markup=create_keyboard(memory[3]))

@dp.message_handler(lambda message: cache_dict[message.from_user.id] == 4)
async def reg_group(message: types.Message):
    if message.text.upper() in memory[3]:
        memory[3] = message.text.upper()
        cache_dict[message.from_user.id] = 5
        await message.answer(
            f'Вы хотете завершить регистрацию с этими данными?\n\nРоль: {memory[0]}\nГруппа: {memory[3]}',
            reply_markup=create_keyboard(['Да', 'Нет']))

@dp.message_handler(lambda message: cache_dict[message.from_user.id] == 5)
async def reg_confirm (message: types.Message):
    if message.text.capitalize() == 'Да':
        if message.from_user.id in admin_list:
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
        cache_dict[message.from_user.id] = [message.from_user.id, memory[0], last_name, corpus, group, admin]
        memory.clear()
        data_base('INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)', tuple(cache_dict[message.from_user.id]))
        Trigger['Main'] = True
        await message.answer(f'гатова', reply_markup=create_keyboard(menu_key))
    else:
        memory.clear()
        cache_dict[message.from_user.id] = 1
        await message.answer('Выберите роль', reply_markup=create_keyboard(role))
        


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
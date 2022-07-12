import logging

from aiogram import Bot, Dispatcher, executor, types
from time import sleep
from copy import deepcopy

from config import *
from modules import *
from keyboards import *
from key import key



#   //  Configure logging   //
logging.basicConfig(level=logging.INFO)

#   //  Initialize bot and dispatcher   //
bot = Bot(token=key)
dp = Dispatcher(bot)



#   //    db sync    //


users = data_base('SELECT * FROM users')
for i in users:
    cache_dict[i[0]] = list(i)
    user_trigger[i[0]] = deepcopy(trigger_list)
admin = data_base('SELECT * FROM admin')
for i in admin:
    admin_list.append(i[0])



#    //    check for registration    //


@dp.message_handler(lambda message: message.from_user.id not in cache_dict)
async def start(message: types.Message):
    id = message.from_user.id
    begin(id)
    await message.answer(
        "Здравствуйте, для начала необходимо пройти небольшую регистарцию")
    await message.answer(
        "Выберите вашу роль", 
        reply_markup=kb_role)



#    //    main menu    //


@dp.message_handler(lambda message:
    (user_trigger[message.from_user.id]['Reg']) &
    (user_trigger[message.from_user.id]['AfterRestart'] is False))
async def after_restarting(message: types.Message):
    #    return to main menu after restarting
    user_trigger[message.from_user.id]['Menu'] = True
    user_trigger[message.from_user.id]['AfterRestart'] = True
    await message.answer(
        'Бот был перезагружен, добро пожаловать в главное меню', 
        reply_markup=kb_menu)



@dp.message_handler(lambda message:
    (user_trigger[message.from_user.id]['Menu']) &
    (message.text.capitalize() in menu_key))
async def main_menu(message: types.Message):
    match message.text.capitalize():
        case 'Расписание':
            await message.answer('технические чоколадки')
        case 'Своё расписание':
            await message.answer('технические чоколадки')
        case 'Профиль':
            id = message.from_user.id
            user_trigger[id]['Profile'] = True
            user_trigger[id]['Menu'] = False
            msg = 'Ваш профиль:\n\n'
            for i in cache_dict[id][1:-1]:
                if (i != None):
                    if ('Корпус' not in i):
                        msg += f"{i}\n"
            match cache_dict[id][1]:
                case 'Студент':
                    profile_key = profile_stud
                case 'Преподаватель':
                    profile_key = profile_teach
            await message.answer(msg, reply_markup=get_keyboard(profile_key))
        case 'Архив расписаний':
            await message.answer('технические чоколадки')



#    //    admin menu    //


@dp.message_handler(lambda message:
    (user_trigger[message.from_user.id]['Menu']) &
    (message.from_user.id in admin_list) &
    ('/admin' in message.text))
async def admin_menu(message: types.Message):
    id = message.from_user.id
    command = message.text.split(' ')
    match command[1]:
        case 'users':
            await message.answer(f'Сейчас зарегестрировано {len(cache_dict)} пользователей')
        case 'user':
            if len(command) == 4:
                if command[3] == 'byid':
                    try:
                        needed_id = int(command[2])
                    except ValueError:
                        await message.answer('id состоит из цифр так то')
                    if needed_id in cache_dict and len(cache_dict[needed_id]) > 2:
                        msg = 'Пользователь зарегестрирован'
                    else:
                        msg = 'Пользователь не зарегистрирован'
                else:
                    if command[3] == 'byusername':
                        s = data_base(
                            "SELECT * FROM users WHERE `username` = ?", 
                            (command[2].capitalize(), ))
                        if s:
                            msg = 'Пользователь зарегестрирован'
                        else:
                            msg = 'Пользователь не зарегистрирован'
                await message.answer(msg)
        case 'userbygroup':
            if len(command) > 2:
                group = command[2].upper()
                usr_id = data_base(
                    "SELECT id FROM users WHERE `group`=?", (group, ))
                if usr_id:
                    msg = f'Список пользователей с группой {group}:\n\n'
                    msg = users_to_msg(msg, usr_id, cache_dict)
                else:
                    msg = 'Пользователей с этой группой не найдено'
                await message.answer(msg)
        case 'teacherbysurname':
            if len(command) > 2:
                surname = command[2].capitalize()
                teacher = data_base(
                    'SELECT id FROM users WHERE `surname`=?', 
                    (surname, ))
                if teacher:
                    msg = f'Список преподавателей с фамилией {surname}:\n\n'
                    msg = users_to_msg(msg, teacher, cache_dict)
                else:
                    msg = 'Преподавателей с такой фамилией не найдено'
                await message.answer(msg)
        case 'allteacher':
            teacher = data_base(
                    "SELECT id FROM users WHERE `role`='Преподаватель'")
            if teacher:
                msg = f'Список преподавателей:\n\n'
                msg = users_to_msg(msg, teacher, cache_dict, 1)
            else:
                msg = 'Пользователей с ролью преподавателя не найдено'
            await message.answer(msg)
        case 'addadmin':
            if id == 459267180:
                if len(command) == 4:
                    if command[3] == 'byid':
                        try:
                            needed_id = int(command[2])
                        except ValueError:
                            await message.answer('id состоит из цифр так то')
                        i = data_base("SELECT * FROM users WHERE `id`=?", (needed_id,))
                        if i:
                            s = data_base("SELECT * FROM admin WHERE `id`=?", (needed_id,))
                            if not s:
                                data_base('INSERT INTO admin VALUES(?)', (needed_id, ))
                                await message.answer(
                                    f'Пользователь с id {needed_id} добавлен к администраторам')
                            else:
                                await message.answer(
                                    f'Пользователь с id {needed_id} уже является администратором')
                        else:
                            await message.answer(
                                f'Пользователь с id {needed_id} не зарегистрирован')
                    elif command[3] == 'byusername':
                        s = data_base(
                            "SELECT id FROM users WHERE `username` = ?", 
                            (command[2],))
                        if s:
                            s_2 = data_base("SELECT id FROM admin WHERE `id`=?", (s[0],))
                            if not s:
                                data_base('INSERT INTO admin VALUES(?)', (s[0], ))
                                await message.answer(
                                    f'Пользователь с username @{command[2]} добавлен к администраторам')
                            else:
                                await message.answer(
                                    f'Пользователь с username @{command[2]} уже является администратором')
                        else:
                            await message.answer(
                                f'Пользователь с username @{command[2]} не зарегистрирован')
        case 'deleteadmin':
            if id == 459267180:
                if len(command) == 4:
                    if command[3] == 'byid':
                        try:
                            needed_id = int(command[2])
                        except ValueError:
                            await message.answer('id состоит из цифр так то')
                        i = data_base("SELECT * FROM users WHERE `id`=?", (needed_id,))
                        if i:
                            s = data_base("SELECT id FROM admin WHERE `id`=?", (needed_id,))
                            if s:
                                data_base(
                                    "DELETE from admin WHERE id = ?", 
                                    (needed_id,))
                                await message.answer(
                                    f'Пользователь с id {needed_id} был удален из администраторов')
                            else:
                                await message.answer(
                                    f'Пользователь с id {needed_id} не является администратором')
                        else:
                            await message.answer(
                                f'Пользователь с id {needed_id} не зарегистрирован')
                    elif command[3] == 'byusername':
                        s = data_base(
                            "SELECT id FROM users WHERE `username` = ?", 
                            (command[2],))
                        if s:
                            s_2 = data_base("SELECT id FROM admin WHERE `id`=?", (s[0],))
                            if not s_2:
                                data_base('DELETE from admin VALUES(?)', (s[0], ))
                                await message.answer(
                                    f'Пользователь с username @{command[2]} был удален из администраторов')
                            else:
                                await message.answer(
                                    f'Пользователь с username @{command[2]} не является администратором')
                        else:
                            await message.answer(
                                f'Пользователь с username @{command[2]} не зарегистрирован')
        case 'alladmin':
            admins = data_base('SELECT * FROM admin')
            msg = users_to_msg('Список администраторов:\n\n', admins, cache_dict)
            await message.answer(msg)

#  //  profile

@dp.message_handler(lambda message:
    (user_trigger[message.from_user.id]['Profile']))
async def menu_profile (message: types.Message):
    id = message.from_user.id
    match message.text.capitalize():
        case 'Сбросить профиль':
            data_base(
                "DELETE from users WHERE id = ?", 
                (id,))
            begin(id)
            await message.answer(
                "Выберите вашу роль", 
                reply_markup=kb_role)
        case 'Изменить курс':
            if cache_dict[id][1] == 'Студент':
                user_trigger[id]['Profile'] = False
                chain = course_chain(cache_dict[id][4])
                if chain:
                    user_trigger[id]['Change_course'] = True
                    cache_dict[id].append(chain)
                    await message.answer(
                        'Выберите номер нового курса',
                        reply_markup=get_keyboard(chain))
                else:
                    user_trigger[id]['Menu'] = True
                    await message.answer(
                        'К сожалению, для вас пока нет других доступных курсов',
                        reply_markup=kb_menu) 
        case 'Изменить фамилию':
            if cache_dict[id][1] == 'Преподаватель':
                user_trigger[id]['Profile'] = False
                user_trigger[id]['Change_surname'] = True
                await message.answer(
                    'Введите новую фамилию',
                    reply_markup=types.ReplyKeyboardRemove())
        case 'Назад':
            user_trigger[id]['Profile'] = False
            await message.answer('Главное меню', reply_markup=kb_menu)

@dp.message_handler(lambda message:
    (user_trigger[message.from_user.id]['Change_course']))
async def change_course(message: types.Message):
    id = message.from_user.id
    if message.text.upper() in cache_dict[id][5]:
        cache_dict[id][4] = message.text.upper()
        del cache_dict[id][5]
        data_base(
            "UPDATE users SET 'group' = ? WHERE id = ?",
            (message.text.upper(), id))
        user_trigger[id]['Change_course'] = False
        user_trigger[id]['Menu'] = True
        await message.answer('Главное меню', reply_markup=kb_menu)

@dp.message_handler(lambda message:
    (user_trigger[message.from_user.id]['Change_surname']))
async def change_surname(message: types.Message):
    id = message.from_user.id
    text = message.text.capitalize()
    if not user_trigger[id]['Send']:
        cache_dict[id].append(text)
        user_trigger[id]['Send'] = True
        await message.answer(
            f'Ваша фамилия {text}. Все верно?', 
            reply_markup=kb_proof)
    else:
        match text:
            case 'Да':
                user_trigger[id]['Send'] = False
                user_trigger[id]['Change_surname'] = False
                user_trigger[id]['Menu'] = True
                cache_dict[id][2] = cache_dict[id][-1]
                del cache_dict[id][-1]
                data_base(
                    "UPDATE users SET 'surname' = ? WHERE id = ?",
                    (cache_dict[id][2], id))
                await message.answer(
                    'Ваша фамилия была успешно изменена',
                    reply_markup=kb_menu)
            case 'Нет':
                del cache_dict[id][5]
                user_trigger[id]['Send'] = False
                await message.answer(
                    'Введите свою фамилию ещё раз',
                    reply_markup=types.ReplyKeyboardRemove())
        

#    //    registration    //


@dp.message_handler(lambda message:
    (cache_dict[message.from_user.id][0] == 1) &
    (message.text.capitalize() in role))
async def reg_role(message: types.Message):
    text = message.text.capitalize()
    cache_dict[message.from_user.id][1].append(text)
    match text:
        case 'Студент':
            msg = 'Выберите корпус'
            keyboard = kb_corpus
        case 'Преподаватель':
            msg = 'Введите свою фамилию'
            keyboard = types.ReplyKeyboardRemove()
    cache_dict[message.from_user.id][0] = 2
    await message.answer(msg, reply_markup=keyboard)


@dp.message_handler(lambda message: cache_dict[message.from_user.id][0] == 2)
async def reg_corpus (message: types.Message):
    id = message.from_user.id
    text = message.text.capitalize()
    if cache_dict[id][1][0] == 'Студент':
        if text in corpus:
            cache_dict[id][0] = 3
            cache_dict[id][1].append(text)
            await message.answer(
                'Выберите курс', 
                reply_markup=kb_course)
    else:
        #   teacher
        if not user_trigger[id]['Send']:
            cache_dict[id][1].append(text)
            user_trigger[id]['Send'] = True
            await message.answer(
                f'Ваша фамилия {text}. Все верно?', 
                reply_markup=kb_proof)
        else:
            match text:
                case 'Да':
                    user_trigger[id]['Send'] = False
                    cache_dict[id][0] = 5
                    user_msg = ''
                    for i in cache_dict[id][1]:
                        user_msg += f'{i}\n'
                    await message.answer(
                        'Вы хотите завершить регистарцию с этими данными?')
                    await message.answer(user_msg)
                case 'Нет':
                    del cache_dict[id][1][1]
                    user_trigger[id]['Send'] = False
                    user_msg = 'Введите свою фамилию ещё раз'
                    await message.answer(user_msg, reply_markup=types.ReplyKeyboardRemove())
            


@dp.message_handler(lambda message: 
        (cache_dict[message.from_user.id][0] == 3) &
        (message.text in course))
async def reg_course (message: types.Message):
    id = message.from_user.id
    cache_dict[id][1].extend(
        [message.text,
        group_list(cache_dict[id][1][-1], message.text)]
    )
    cache_dict[id][0] = 4
    await message.answer(
        "Выберите группу", 
        reply_markup=get_keyboard(cache_dict[id][1][-1]))


@dp.message_handler(lambda message:
    (cache_dict[message.from_user.id][0] == 4))
async def reg_group (message: types.Message):
    if message.text.upper() in cache_dict[message.from_user.id][1][-1]:
        id = message.from_user.id
        del cache_dict[id][1][3]
        cache_dict[id][1][-1] = message.text.upper()
        cache_dict[id][0] = 5
        msg = ''
        for i in cache_dict[id][1]:
            msg += f"{i}\n"
        await message.answer('Вы хотите завершить регистрацию с этими данными?')
        await message.answer(msg, reply_markup=kb_proof)


@dp.message_handler(lambda message: cache_dict[message.from_user.id][0] == 5)
async def reg_confirm (message: types.Message):
   id = message.from_user.id
   match message.text.capitalize():
        case "Да":
            cache_dict[id][1].insert(0, id)
            match cache_dict[id][1][1]:
                case 'Студент':
                    cache_dict[id][1].insert(2, None)
                case 'Преподаватель':
                    cache_dict[id][1].extend([None, None])
            try:        
                cache_dict[id][1].append(message.from_user.username)
            except:
                cache_dict[id][1].append(
                    f'{message.from_user.first_name} {message.from_user.last_name}')
            try:
                data_base(
                    'INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)', 
                    tuple(cache_dict[id][1])
                )
            except:
                #   if db is locked
                sleep(1.5)
                data_base(
                    'INSERT INTO users VALUES(?, ?, ?, ?, ?)', 
                    tuple(cache_dict[id][1])
                )
            cache_dict[id] = cache_dict[id][1]
            user_trigger[id]['Reg'] = True
            user_trigger[id]['Menu'] = True
            await message.answer(
                'Главное меню', 
                reply_markup=kb_menu)
        case "Нет":
            cache_dict[id] = [1, []]
            await message.answer(
                "Выберите вашу роль", 
                reply_markup=kb_role)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
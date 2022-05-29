
#   //  тригеры для логики  //

Trigger = {
    #   регистрация
    'Send': False,
    #   меню
    'Main': True,
    'Rasp': False,
    'Profile': False,
    'Admin': False,
    #   профиль
    'Change_course': False,
    'Change_surname': False,
    #   расписание
    'Date': False,
    'ByGroup': False,
    'ByTeacher': False
}

admin_list = [
    459267180,
    501057196
]

cache_dict = {}
memory = []
backup = []

#   //    инофрмация о пользователе   //

#   id          //  id Telegram          //  Все
#   role        //  Роль                 //  Все
#   last_name   //  Фамилия              //  Преподаватели
#   corpus      //  Корпус               //  Студенты
#   group       //  Группа               //  Студенты
#   admin       //  Права администратора //  Все


#   //    ключи    //

role = ('Студент', 'Преподаватель')
corpus = ('Корпус 1', 'Корпус 2')
course = ('1', '2', '3', '4')
menu_key = ("Расписание", "Своё расписание", "Профиль", "Админ")
admin_key = ('Нюхнуть бебры', 'Рассылка', 'Пукнуть сливой', 'Назад')
rasp_key = ('По группам', 'По преподавателям', 'Назад')
profile = ['Сбросить профиль', 'Изменить курс', 'Изменить фамилию', 'Назад']
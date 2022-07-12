cache_dict = {}
admin_list = []
user_trigger = {}

trigger_list = {
    #   registration
    'Reg': True,
    'Send': False,
    #   main menu
    'Menu': False,
    'AfterRestart': False,
    'Profile': False,
    #   profile
    'Change_course': False,
    'Change_surname': False
}

role = ('Студент', 'Преподаватель')
corpus = ('Корпус 1', 'Корпус 2')
course = ('1', '2', '3', '4')
menu_key = ('Расписание', 'Своё расписание', 'Профиль', 'Архив расписаний')
profile_stud = ('Сбросить профиль', 'Изменить курс', 'Назад')
profile_teach = ('Сбросить профиль', 'Изменить фамилию', 'Назад')
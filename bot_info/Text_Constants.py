# Текстовые константы для бота или пользователей

USER_STATUS_CONSTANT = {
    "user_status_test": "Тестирование", 
    "user_status_complete": "Завершён",
    "user_status_reg": "Регистрация",
}

class BotMessages: # класс для сообщений бота

    BOT_STATUS_INFO = "🟢 Бот работает исправно.\nВремя на сервере: {now}" # cостояние бота
    BOT_STATUS_ERROR = "Не удалось отправить heartbeat: {e}"
    # приветственное предложение
    WELCOME = "Здарова вовчик, зарегайся через /reg и погнали"

    
    MESSAGE_FROM_SHOW_LEADERSTATS = (
        "ВРЕМЕННЫЙ ТЕКСТ ДЛЯ АДМИНОВ, ДОБРО ПОЖАЛОВАТЬ, "
        "{admin_name}\n"
        "Вывожу таблицу лидеров!"
    )
    LEADERSTATS_TEXT_UP = "Cписок Всех ЛИДЕРОВ!"
    LEADERSTAT_ONE_POS = "\n {pos} Место: {user_name} Курс: {user_course} баллов за тест: {score}"

    NOT_ADMIN_ACCESS = "УЁБИЩЕ У ТЕБЯ НЕТ ДОСТУПА ЖИРНЫЙ" # если нет доступа к функция

    # cтатусы для регистрации
    USER_REG_0 = (
        "Для начала, как тебя зовут? (Имя и фамилия через пробел)\n"
        "Пример: Иван Таранов"
    )
    USER_REG_1 = "Отлично! введи номер курса"
    USER_REG_FAIL = "Если ты видешь это сообщение, код нихуя не работает"

    USER_NICKNAME_FORMAT_ERROR = "Неправильный формат имени и фамилии"
    USER_COURSE_FORMAT_ERROR = "Неправильный формат курса"

    USER_REG_COMPLETE = (
        "Регистрация прошла успешно, ВРЕМЕННО ВЫВОЖУ ДАННЫЕ о регистрации: {user_data}\n"
        "Можешь переходить к написанию теста при помощи /test Удачи!"
    )

    USER_REG_AFTER_COMPLETE_TEST = "Вы уже зарегистрированы"

    # статусы для теста
    TEST_WRONG_USER_STATUS = "Сначала пройдите регистрацию через команду /reg :D"
    TEST_NEXT_QUESTION = "Переходим к следующему вопросу!"
    INCORRECT_FORMAT_ANSWER = "Неправильный формат вопроса"
    ANSWER_INDEX_OUT_OF_RANGE = "Нет такого варианта ответа!"

    TEST_COMPLETE = (
        "Спасибо за прохождение теста!\n"
        "Ваш счёт: {current_score} из {count_of_questions}"
    )
    TEMP_TEST_AFTER_COMPLETE_TEST = "Вы уже завершили тест!"

    QUESTION_OUT_OF_RANGE_ERROR = "Что-то пошло не так"


    
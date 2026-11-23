import asyncio
import os
import time
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import FSInputFile
from aiogram.filters import StateFilter
from datetime import datetime

from bot_info.questions import QUESTIONS 
import DB_info.database as db
import bot_info.Text_Constants as TEXT_CONST
import reg_value_cheking as value_check

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден! Проверь файл .env")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class QuizStates(StatesGroup):
    answering = State()

# некоторые константы для обращения
USER_STATUS_TEST: str = TEXT_CONST.USER_STATUS_CONSTANT["user_status_test"]
USER_STATUS_REG: str = TEXT_CONST.USER_STATUS_CONSTANT["user_status_reg"]
USER_STATUS_COMPLETE: str = TEXT_CONST.USER_STATUS_CONSTANT["user_status_complete"]

raw_admins = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in raw_admins.split(",") if x.strip()]

ADMIN_ID_FOR_STATUS = ADMIN_IDS[0] # айдишник для пингование состояние
BOT_MESSAGES = TEXT_CONST.BotMessages # сообщения бота


#====================================
# ФУНКЦИИ ДЛЯ ФУНКЦИОЛНАЛА БОТА
#====================================

# ФУНКЦИЯ ОТПРАВКИ ВОПРОСА
async def ask_question(message: types.Message, state: FSMContext, q_index: int):

    # здесь q_index всегда меньше чем длина
    if q_index >= len(QUESTIONS):
        await message.answer(
            text=BOT_MESSAGES.QUESTION_OUT_OF_RANGE_ERROR,
        )
        return None
    
    question = QUESTIONS[q_index]
    text = question["text"]

    for pos, option in enumerate(question["options"], 1):
        text += f"\nОтвет {pos}: {option}"

    await message.answer(
        text=text,
        reply_markup=get_reply_keyboard()
    )

    await state.update_data(current_q_index=q_index)
    await state.set_state(QuizStates.answering)

# ФУНКЦИЯ ДЛЯ КНОПОК НА КЛАВЕ
def get_reply_keyboard():
    # Создаем кнопки
    btn_1 = KeyboardButton(text="Ответ 1")
    btn_2 = KeyboardButton(text="Ответ 2")
    btn_3 = KeyboardButton(text="Ответ 3")
    btn_4 = KeyboardButton(text="Ответ 4")

    # Группируем их
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [btn_1, btn_2, btn_3, btn_4]
        ],
        resize_keyboard=True, # Автоматически подгоняет размер кнопок под экран
        one_time_keyboard=False # Панель не исчезнет после нажатия
    )
    return keyboard

def get_reply_keyboard_show_answer():

    btn = KeyboardButton(text="Посмотреть ответы")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[btn]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

# ФУНКЦИЯ ДЛЯ ПИНГОВАНИЯ АДМИНА
async def check_bot_status():

    while True:
        try:
            now = datetime.now().strftime("%H:%M:%S")
            await bot.send_photo(
                chat_id=ADMIN_ID_FOR_STATUS,
                photo=FSInputFile("bot_info/bot_status.png"),
                caption=BOT_MESSAGES.BOT_STATUS_INFO.format(now=now)
            )
        except Exception as e:
            logging.error(BOT_MESSAGES.BOT_STATUS_ERROR.format(e=e))

        await asyncio.sleep(60)


#====================================
# ХЕНДЛЕРЫ БОТА
#====================================

# начало теста
@dp.message(Command("start"), ~StateFilter(QuizStates.answering))
async def start(message: types.Message):
    await message.answer(
        text=BOT_MESSAGES.WELCOME, # TODO: Добавим какой-нибудь описание
    )

# запуск теста и регистрации
@dp.message(Command("test"), ~StateFilter(QuizStates.answering))
async def start_test(message: types.Message, state: FSMContext):
    
    data = await state.get_data()
    status = data.get("user_status")

    # обновим статус завершённого если захотят пройти тест заново
    if status == USER_STATUS_COMPLETE:
        # await state.update_data(user_status = USER_STATUS_TEST)
        # # TODO: нужно ли на секунду застыть чтобы успеть обновить статус?
        # time.sleep(5) #возможны траблы с с асинхронностью но это не точно        
        await message.answer(
            text = BOT_MESSAGES.TEST_WRONG_USER_STATUS
        )
        return None

    # без регистрации нельзя проходить
    if status != USER_STATUS_TEST:
        await message.answer(
            text = BOT_MESSAGES.TEST_WRONG_USER_STATUS
        )
        return None
    
    await state.update_data(current_q_index=0, score=0)
    await ask_question(message, state, 0)

# КОМНАДА АДМИНА (ПОКАЗ ВСЕХ ПАЦАНЧИКОВ) ЙОУ!
@dp.message(Command("show_leaderstats"))
async def show_leaderstats(message: types.Message):
    user_id: int = message.from_user.id
    if user_id in ADMIN_IDS:
        await message.answer(
            text=BOT_MESSAGES.MESSAGE_FROM_SHOW_LEADERSTATS.format(admin_name=message.from_user.full_name)
        )

        leaderstats = await db.show_all_users()
        text = BOT_MESSAGES.LEADERSTATS_TEXT_UP

        for pos, user_data in enumerate(leaderstats, 1):
            text += BOT_MESSAGES.LEADERSTAT_ONE_POS.format(
                pos = pos,
                user_name = user_data[0],
                user_course = user_data[1],
                score = user_data[2]
            )
        await message.answer(
            text = text
        )

    else:
        await message.answer(
            text = BOT_MESSAGES.NOT_ADMIN_ACCESS,
        )

@dp.message(Command("reg"), ~StateFilter(QuizStates.answering))
async def registration(message: types.Message, state: FSMContext):

    data = await state.get_data()
    status = data.get("user_status", '')

    # первичное обращение
    if status == '':
        # ставим статус регистрации и словарь данных пользователя
        status = USER_STATUS_REG + "0"
        await state.update_data(user_status = status, user_data = {})

    if status == USER_STATUS_COMPLETE or status == USER_STATUS_TEST:
        await message.answer(
            text=BOT_MESSAGES.USER_REG_AFTER_COMPLETE_TEST,
        )

    if USER_STATUS_REG in status:
        match status[-1]:
            case '0': 
                await message.answer(
                    text=BOT_MESSAGES.USER_REG_0,
                )
            case "1":
                await message.answer(
                    text=BOT_MESSAGES.USER_REG_1,
                )
            case _:
                await message.answer(
                    text=BOT_MESSAGES.USER_REG_FAIL,
                )

# хендлер для ловли ответа
@dp.message(F.text.lower().startswith("ответ"))
async def answer_cheking(message: types.Message, state: FSMContext):

    data = await state.get_data()
    status: str = data.get("user_status", "")

    if status == USER_STATUS_TEST:
        current_q_index = data.get("current_q_index", 0)
        current_score = data.get("score", 0) # Достаем текущий счет
    
        question = QUESTIONS[current_q_index]
        answer = int(message.text[-1]) - 1

        if answer not in [0,1,2,3]:
            await message.answer(text=BOT_MESSAGES.ANSWER_INDEX_OUT_OF_RANGE)
            return None
    
        if question["options"][answer] == question["answer"]:
            current_score += 1 # Если ответ верный, плюсуем балл

        current_q_index += 1 # переход к некст вопросу
        count_of_questions = len(QUESTIONS)

        if current_q_index >= count_of_questions:

            # обновляем статус пользователя как "Завершённый"

            await state.update_data(user_status = USER_STATUS_COMPLETE)
            await message.answer(
                text = BOT_MESSAGES.TEST_COMPLETE.format(
                    current_score = current_score, 
                    count_of_questions = count_of_questions
                ),
                reply_markup=get_reply_keyboard_show_answer()
            )
            await db.save_result(message.from_user.id, current_score)

        else:
            await message.answer(
                text = BOT_MESSAGES.TEST_NEXT_QUESTION,
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.update_data(current_q_index=current_q_index, score=current_score)
            await ask_question(message, state, current_q_index)

@dp.message(F.text == "Посмотреть ответы")
async def check_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    status: str = data.get("user_status", "")

    if status == USER_STATUS_COMPLETE:
        text = "ОТВЕТЫ:"

        for question_data in QUESTIONS:
            text += f"\nВопрос {question_data["id"]} - {question_data["answer"]}"

    await message.answer(
        text=text,
    )

@dp.message(F.text)
async def echo_handler(message: types.Message, state: FSMContext):

    data = await state.get_data()
    user_data = data.get("user_data", {})
    status: str = data.get("user_status", "")

    # входим в регистрацию
    if "Регистрация" in status:
        match status[-1]:
            case '0':
                nick = message.text
                # проверяем данные для корректности
                if not value_check.nickname_checking(nick):
                    await message.answer(
                        text=BOT_MESSAGES.USER_NICKNAME_FORMAT_ERROR
                    )
                    return None
                # сохраняем имя
                user_data["nickname"] = message.text
    
                await state.update_data(
                    user_data=user_data, 
                    user_status=USER_STATUS_REG + "1" # Меняем статус на следующий шаг
                )

                await registration(message, state)
            case '1':
                course = message.text
                # проверяем данные для корректности
                if not value_check.course_checking(course):
                    await message.answer(
                        text=BOT_MESSAGES.USER_COURSE_FORMAT_ERROR
                    )
                    return None
                # сохраняем курс
                user_data["course"] = course
    
                await state.update_data(
                    user_data=user_data,
                    user_status = USER_STATUS_TEST # ставим новый статус
                )

                await db.insert_user(message.from_user.id, user_data["nickname"], user_data["course"])

                await message.answer(
                    text=BOT_MESSAGES.USER_REG_COMPLETE.format(user_data=user_data)
                )
            case _:
                await message.answer(
                    text=BOT_MESSAGES.USER_REG_FAIL,
                )
    elif status == USER_STATUS_TEST:
        # заход сюда - неправильный формат вопроса
        await message.answer(
            text=BOT_MESSAGES.INCORRECT_FORMAT_ANSWER,
        )

async def main():
    await db.init_db()
    asyncio.create_task(check_bot_status())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
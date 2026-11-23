import aiosqlite
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DB_NAME")

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                course INTEGER,
                result INTEGER,
                time_by_complete TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def insert_user(user_id: int, username: str, course: int):
    async with aiosqlite.connect(DB_NAME) as db:
        # Сохраняем пользователя, если его еще нет
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, course, result, time_by_complete) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, course, -1, datetime.now().strftime("%H:%M:%S")) # в момент регистрации результата нет
        )
        await db.commit()

async def save_result(user_id: int, score: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET result = (?) WHERE users.user_id = (?)",
            (score, user_id)
        )
        await db.commit()

async def show_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT username, course, result " \
            "FROM users " \
            "WHERE result >= 0 " \
            "ORDER BY result DESC",
        ) as table:
            leaderboard = await table.fetchall()
            return leaderboard

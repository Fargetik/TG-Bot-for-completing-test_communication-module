# TODO требования к данными
# никнейм: Имя + фамилия (кирилица+пробел+кирилица, от 6 до 50 знаков, без спецсимволов и цифр)
# курс: целое число от 1 до 5 (5 курсов)
import re

pattern = r"^[А-Яа-яЁё]{3,}\s[А-Яа-яЁё]{3,}$"
def nickname_checking(nick: str) -> bool:
    if len(nick) > 50: return False
    if not re.fullmatch(pattern, nick): return False
    return True

def course_checking(course: str) -> bool:
    if not course.isdigit(): return False
    return 1 <= int(course) <= 5
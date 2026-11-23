# TODO требования к данными
# никнейм: Имя + фамилия (кирилица+пробел+кирилица, 50 знаков, без спецсимволов и цифр)
# курс: целое число от 1 до 5 (5 курсов)
import re

pattern = r"^[А-Яа-яЁё]+\s[А-Яа-яЁё]+$"
def nickname_checking(nick: str) -> bool:
    if len(nick) > 50: return False
    if not re.fullmatch(pattern, nick): return False
    return True

def course_checking(course: str) -> bool:
    if not course.isdigit(): return False
    return 1 <= int(course) <= 5
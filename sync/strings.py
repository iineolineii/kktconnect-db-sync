import re
from typing import overload

@overload
def normalize_cyrillic(value: str) -> str: ...

@overload
def normalize_cyrillic(value: None) -> None: ...

def normalize_cyrillic(value: str | None) -> str | None:
    if value is None:
        return None

    return re.sub(
        r"[^а-яa-z0-9]+", " ",
        value.lower().replace("ё", "е")
    ).strip()


def roles_by_position(position: str) -> tuple[bool, bool, bool]:
    position = normalize_cyrillic(position)
    words = position.split()

    teacher_keywords = {"препод", "педагог", "учеб"}
    admin_keywords   = {"зав", "зам", "инженер", "психолог", "кадр", "секретарь"}

    director_keyword = "директор"

    teacher  = False
    admin    = False
    director = False

    if director_keyword in words:
        teacher  = False
        admin    = True
        director = True
    else:
        roles_found = 0

        for word in words:
            for teacher_keyword in teacher_keywords:
                if teacher_keyword in word:
                    teacher = True
                    roles_found += 1
                    break

            for admin_keyword in admin_keywords:
                if admin_keyword in word:
                    admin = True
                    roles_found += 1
                    break

            if roles_found >= 2:
                break

    return (teacher, admin, director)

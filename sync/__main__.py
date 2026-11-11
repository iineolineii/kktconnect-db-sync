import asyncio
from pathlib import Path
from docx import Document

from .db import InternalSession, UnifiedSession, setup_database
from .db.models import Employee, User
from .excel import build_snils_map
from .db import ExternalSession
from .strings import normalize_cyrillic, roles_by_position
from .files   import convert_to_docx

DOCUMENT = Path("/home/iineolineii/Загрузки/Список сотрудников  для ТОР моя школа.docx")
WORKBOOK = Path("/home/iineolineii/Загрузки/перс.учет.xlsx")

UNIFIED_DB  = "/home/iineolineii/.local/opt/gosusligi/sync/unified.db"
INTERNAL_DB = "/home/iineolineii/.local/opt/gosusligi/sync/internal.db"
EXTERNAL_DB = "/home/iineolineii/.local/opt/gosusligi/sync/external.db"

async def main():
    await setup_database(UNIFIED_DB, UnifiedSession)

    await setup_database(INTERNAL_DB, InternalSession)
    internal_users = await InternalSession.get_all_models(Employee)

    await setup_database(EXTERNAL_DB, ExternalSession)
    external_users = await ExternalSession.get_all_models(User)

    snils_by_name = build_snils_map(WORKBOOK)
    document_path = convert_to_docx(DOCUMENT)
    document = Document(str(document_path))

    for table in document.tables:
        for row in table.rows[1:]:
            no_cell, name_cell, position_cell = row.cells[0], row.cells[1], row.cells[2]

            no = normalize_cyrillic(no_cell.text)
            if not no:
                continue

            name = normalize_cyrillic(name_cell.text)

            snils = snils_by_name.get(name)
            if not snils:
                raise KeyError(f"Could not found SNILS for employee with name {name!r}")

            position = normalize_cyrillic(position_cell.text)
            is_teacher, is_admin, is_director = roles_by_position(position)

            employee = Employee(
                name        = name.title(),
                snils       = snils,
                is_teacher  = is_teacher,
                is_admin    = is_admin,
                is_director = is_director
            )

            if name not in internal_users:
                raise KeyError(f"Unknown employee name {name!r}")

            elif name not in external_users:
                print(f"New employee {name.title()}")
                await ExternalSession.update_model(User(name=name))

            else:
                internal_user = internal_users[name]
                external_user = external_users[name]

                employee.invited   = internal_user.invited

                employee.email     = external_user.email
                employee.confirmed = external_user.confirmed
                employee.token     = external_user.token

                external_user.name = name.title()
                await ExternalSession.update_model(external_user)

            await UnifiedSession.update_model(employee)


if __name__ == "__main__":
    asyncio.run(main())

import magic
import subprocess
from pathlib import Path


def get_mime_type(path: Path) -> str:
    """Определяет MIME-тип файла с помощью python-magic."""
    return magic.from_file(str(path), mime=True)


def convert_to_docx(path: Path) -> Path:
    """Конвертирует .doc в .docx, если необходимо, иначе возвращает исходный путь."""
    mime_type = get_mime_type(path)

    if mime_type == "application/msword":
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to", "docx",
            "--outdir", path.parent,
            path
        ], check=True)
        return path.with_suffix(".docx")

    elif mime_type in {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip"
    }:
        return path

    else:
        raise ValueError(f"Неизвестный формат: {mime_type}")

# -*- coding: utf-8 -*-
"""
Удаляет области #Область ... #КонецОбласти, внутри которых нет значащего кода.
Значащий код = не пустые строки и не только комментарии (//).
"""
import re
from pathlib import Path


def is_meaningful_line(line: str) -> bool:
    """Строка считается значащей, если не пустая и не только комментарий."""
    s = line.strip()
    if not s:
        return False
    # Строка, состоящая только из комментария (// в начале после пробелов)
    if s.startswith("//"):
        return False
    return True


def has_meaningful_content(lines: list[str]) -> bool:
    """Есть ли между строками хотя бы одна значащая строка."""
    return any(is_meaningful_line(ln) for ln in lines)


def process_bsl_content(text: str) -> str:
    """Находит пары #Область...#КонецОбласти и удаляет те, внутри которых нет кода."""
    lines = text.split("\n")
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Ищем начало области (#Область с опциональным именем)
        if re.match(r"^\s*#Область\s", line):
            start_idx = i
            region_start_line = line
            i += 1
            content_lines = []
            end_idx = None
            while i < len(lines):
                if re.match(r"^\s*#КонецОбласти\s*$", lines[i]):
                    end_idx = i
                    break
                content_lines.append(lines[i])
                i += 1
            if end_idx is not None:
                if not has_meaningful_content(content_lines):
                    # Пустая область — не добавляем её в результат, пропускаем
                    i = end_idx + 1
                    continue
                # Область с кодом — оставляем как есть
                for j in range(start_idx, end_idx + 1):
                    result.append(lines[j])
                i = end_idx + 1
                continue
        result.append(line)
        i += 1
    # Убираем лишние подряд идущие пустые строки (оставляем максимум одну подряд)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(result))


def main():
    src = Path(__file__).resolve().parent / "src"
    bsl_files = list(src.rglob("*.bsl"))
    for path in sorted(bsl_files):
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Ошибка чтения {path}: {e}")
            continue
        new_content = process_bsl_content(content)
        if new_content != content:
            path.write_text(new_content, encoding="utf-8")
            print(f"Обновлён: {path}")


if __name__ == "__main__":
    main()

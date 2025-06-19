# Dream-Team-core/dataset_preparation/src/text_cleaner.py
import re

def clean_text(text: str) -> str:
    """
    Базовая очистка текста:
    - Удаляет множественные пробелы.
    - Удаляет пробелы в начале и конце строки.
    """
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text) # Заменяет один или более пробельных символов на один пробел
    return text.strip()

if __name__ == '__main__':
    # Пример использования
    test_str = "  Это    тестовая   строка   с   лишними   пробелами.  "
    cleaned_str = clean_text(test_str)
    print(f"Оригинал: '{test_str}'")
    print(f"Очищено:  '{cleaned_str}'")

    test_empty = None
    print(f"Оригинал: '{test_empty}'")
    print(f"Очищено:  '{clean_text(test_empty)}'")

    test_only_spaces = "     "
    print(f"Оригинал: '{test_only_spaces}'")
    print(f"Очищено:  '{clean_text(test_only_spaces)}'")
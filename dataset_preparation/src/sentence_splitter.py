# Dream-Team-core/dataset_preparation/src/sentence_splitter.py
import nltk
from .text_cleaner import clean_text # Импортируем из нашего же пакета

# Попытка загрузить токенизатор 'punkt' для nltk, если он еще не загружен
# и дополнительный 'punkt_tab'
_NLTK_RESOURCES_LOADED = False
def _ensure_nltk_resources():
    global _NLTK_RESOURCES_LOADED
    if _NLTK_RESOURCES_LOADED:
        return

    resources_to_check = ["punkt", "punkt_tab"]
    all_loaded_successfully = True

    for resource_name in resources_to_check:
        try:
            nltk.data.find(f'tokenizers/{resource_name}')
        except LookupError:
            print(f"Ресурс '{resource_name}' для nltk не найден. Попытка загрузки...")
            try:
                nltk.download(resource_name, quiet=False)
                nltk.data.find(f'tokenizers/{resource_name}') # Проверка после загрузки
                print(f"Ресурс '{resource_name}' успешно загружен.")
            except Exception as e_download:
                print(f"Ошибка при загрузке '{resource_name}': {e_download}")
                print(f"Пожалуйста, попробуйте загрузить '{resource_name}' вручную (см. предыдущие инструкции).")
                all_loaded_successfully = False
        except Exception as e_find:
            print(f"Произошла неожиданная ошибка при проверке ресурса '{resource_name}': {e_find}")
            all_loaded_successfully = False
    
    if all_loaded_successfully:
        _NLTK_RESOURCES_LOADED = True

_ensure_nltk_resources() # Вызываем при импорте модуля

def split_text_into_sentences(text_content: str) -> list[str]:
    """
    Разбивает предоставленный текстовый контент на предложения.
    Текст предварительно очищается.
    """
    if not _NLTK_RESOURCES_LOADED:
        print("Ошибка: Необходимые ресурсы NLTK (punkt/punkt_tab) не загружены. Разбиение на предложения может быть некорректным.")
        # Можно либо вернуть [clean_text(text_content)] либо возбудить исключение
        # return [clean_text(text_content)] # Возвращаем как одно предложение
        raise RuntimeError("NLTK tokenizers (punkt/punkt_tab) not available.")


    if not text_content:
        return []
    # Очистка текста здесь не нужна, если предполагается, что он уже очищен (например, целый абзац)
    # Но если это произвольный текст, то лучше очистить:
    # cleaned_text = clean_text(text_content)
    # if not cleaned_text:
    #     return []
    
    # Предполагаем, что text_content - это уже осмысленный блок (например, абзац)
    try:
        sentences = nltk.sent_tokenize(text_content, language='russian')
        # Дополнительная очистка для каждого предложения (удаление ведущих/замыкающих пробелов)
        return [s.strip() for s in sentences if s.strip()]
    except LookupError as e_lookup: # На случай если _ensure_nltk_resources не сработал полностью
        print(f"Критическая ошибка при разбиении: Ресурс NLTK не найден. {e_lookup}")
        raise # Перевыбрасываем, т.к. это критично
    except Exception as e:
        print(f"Ошибка при разбиении текста на предложения: {e}")
        # В случае ошибки возвращаем исходный текст как одно "предложение", чтобы не терять данные
        return [text_content.strip()] if text_content.strip() else []

if __name__ == '__main__':
    # Пример использования
    test_para = "Это первое предложение. А это второе! И, наконец, третье?"
    sentences = split_text_into_sentences(test_para)
    print(f"Абзац: '{test_para}'")
    print("Предложения:")
    for i, s in enumerate(sentences):
        print(f"  {i}: '{s}'")

    test_para_complex = "Г-н. Иванов поехал в г. Санкт-Петербург. Там он встретил М.Ю. Лермонтова."
    sentences_complex = split_text_into_sentences(test_para_complex)
    print(f"\nАбзац: '{test_para_complex}'")
    print("Предложения:")
    for i, s in enumerate(sentences_complex):
        print(f"  {i}: '{s}'")
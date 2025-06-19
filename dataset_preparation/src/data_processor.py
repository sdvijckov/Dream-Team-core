# Dream-Team-core/dataset_preparation/src/data_processor.py
import os
import json
import traceback

from .file_loaders import load_paragraphs_from_docx, load_paragraphs_from_txt
from .sentence_splitter import split_text_into_sentences
from .ner_extractor import extract_entities
from .dialogue_identifier import extract_dialogue_info

def process_file_to_jsonl(input_file_path: str, output_dir_for_this_file: str, input_base_dir: str) -> bool: # Добавлен input_base_dir
    """
    Обрабатывает один входной файл, извлекает данные и сохраняет в JSONL.
    Добавляет категорию на основе относительного пути.

    Args:
        input_file_path (str): Полный путь к входному файлу.
        output_dir_for_this_file (str): Полный путь к директории, куда будет сохранен .jsonl.
        input_base_dir (str): Полный путь к корневой входной директории (например, .../input_texts).

    Returns:
        bool: True, если обработка прошла успешно, иначе False.
    """
    # ... (начало функции остается таким же: проверки, загрузка абзацев) ...
    if not os.path.exists(input_file_path):
        print(f"Ошибка: Файл не найден: {input_file_path}")
        return False

    _, file_extension = os.path.splitext(input_file_path)
    base_file_name = os.path.basename(input_file_path) # Имя файла с расширением
    file_name_without_ext = os.path.splitext(base_file_name)[0] # Имя файла без расширения
    
    paragraphs_list = []
    if file_extension.lower() == '.docx':
        paragraphs_list = load_paragraphs_from_docx(input_file_path)
    elif file_extension.lower() == '.txt':
        paragraphs_list = load_paragraphs_from_txt(input_file_path)
    else:
        print(f"Неподдерживаемый формат файла: {input_file_path}. Поддерживаются .docx и .txt")
        return False

    if not paragraphs_list:
        print(f"Не удалось извлечь абзацы или файл пуст: {input_file_path}")
        return True 

    output_file_name = file_name_without_ext + '.jsonl'
    output_file_path = os.path.join(output_dir_for_this_file, output_file_name)

    # os.makedirs(output_dir_for_this_file, exist_ok=True) # Это теперь делается в main_creator.py

    # Определение категории/относительного пути
    category_path = None
    try:
        # Получаем путь к директории, содержащей входной файл
        containing_dir = os.path.dirname(input_file_path)
        # Вычисляем относительный путь от input_base_dir
        relative_path_to_file_dir = os.path.relpath(containing_dir, input_base_dir)
        if relative_path_to_file_dir == ".": # Файл в корне input_base_dir
            category_path = "" # или None, или "/" - по желанию
        else:
            category_path = relative_path_to_file_dir.replace(os.path.sep, '/') # Заменяем разделители на / для консистентности
    except ValueError: # Может возникнуть, если пути на разных дисках и relpath не может вычислить
        category_path = "unknown_category"
        print(f"Предупреждение: Не удалось определить категорию для {input_file_path}")


    try:
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            for para_idx, para_text in enumerate(paragraphs_list):
                if not para_text.strip(): 
                    continue

                sentences_in_para = split_text_into_sentences(para_text)
                
                sentences_data = []
                for sent_idx, sent_text in enumerate(sentences_in_para):
                    entities = extract_entities(sent_text) 
                    dialogue_info = extract_dialogue_info(sent_text)
                    
                    sentences_data.append({
                        "sentence_index_in_paragraph": sent_idx,
                        "text": sent_text,
                        "entities": entities,
                        "dialogue_info": dialogue_info
                    })

                record = {
                    "id": f"{file_name_without_ext}_paragraph_{para_idx}",
                    "source_file": base_file_name,
                    "category": category_path, # <--- ДОБАВЛЕНО ПОЛЕ КАТЕГОРИИ
                    "paragraph_index": para_idx,
                    "paragraph_text": para_text,
                    "sentences": sentences_data
                }
                f_out.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"Файл '{input_file_path}' успешно обработан. Категория: '{category_path}'. Результат: '{output_file_path}'")
        return True
    except Exception as e:
        print(f"Критическая ошибка при обработке или сохранении JSONL для файла {input_file_path}: {e}")
        traceback.print_exc()
        return False

# В __main__ блоке data_processor.py нужно будет добавить input_base_dir при вызове
# Но лучше тестировать через main_creator.py
if __name__ == '__main__':
    print("Модуль data_processor.py. Для тестирования всего процесса запустите main_creator.py.")
    # ... (можно оставить или обновить тестовый вызов, добавив input_base_dir)
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # test_input_root_dp = os.path.join(os.path.dirname(current_dir), "input_texts")
    # test_output_dir_dp = os.path.join(os.path.dirname(current_dir), "processed_data_test_dp")
    # sample_txt_path_dp = os.path.join(test_input_root_dp, "sample_for_dp_test.txt")
    # ... создать файл ...
    # process_file_to_jsonl(sample_txt_path_dp, test_output_dir_dp, test_input_root_dp)
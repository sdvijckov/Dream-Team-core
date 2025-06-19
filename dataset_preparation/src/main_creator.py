# Dream-Team-core/dataset_preparation/src/main_creator.py
import os
from .data_processor import process_file_to_jsonl

def run_dataset_creation_pipeline(input_dir: str = None, output_dir: str = None, recursive_search: bool = True): # Изменили recursive_search по умолчанию на True
    """
    Основная функция для запуска процесса создания датасета.
    Ищет файлы в input_dir (рекурсивно по умолчанию) и обрабатывает их, 
    сохраняя в output_dir с сохранением структуры подпапок.

    Args:
        input_dir (str, optional): Путь к директории с входными текстами. 
                                   Если None, используется ../input_texts.
        output_dir (str, optional): Путь к директории для сохранения обработанных данных. 
                                    Если None, используется ../processed_data.
        recursive_search (bool, optional): Искать ли файлы в подпапках input_dir. 
                                           По умолчанию True.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_preparation_root = os.path.dirname(script_dir)

    if input_dir is None:
        input_dir = os.path.join(dataset_preparation_root, "input_texts")
    # Нормализуем путь для корректного сравнения и построения относительных путей
    input_dir = os.path.normpath(input_dir)


    if output_dir is None:
        output_dir = os.path.join(dataset_preparation_root, "processed_data")
    output_dir = os.path.normpath(output_dir)

    if not os.path.isdir(input_dir):
        print(f"Директория с входными текстами не найдена: {input_dir}")
        print(f"Пожалуйста, создайте ее и поместите туда файлы для обработки или укажите корректный путь.")
        return
    
    # Не создаем output_dir здесь, он будет создаваться по мере необходимости для подпапок

    print(f"Поиск файлов для обработки в: {input_dir}" + (" (включая подпапки)" if recursive_search else ""))
    
    files_processed_count = 0
    files_to_process_map = {} # Словарь для хранения {output_subdir_path: [input_file_path, ...]}

    if recursive_search:
        for root, _, filenames in os.walk(input_dir):
            for filename in filenames:
                if filename.lower().endswith(('.docx', '.txt')):
                    input_file_path = os.path.join(root, filename)
                    
                    # Определяем относительный путь от input_dir до текущей папки файла
                    relative_subdir = os.path.relpath(root, input_dir)
                    
                    # Создаем соответствующий путь для выходной поддиректории
                    # Если relative_subdir это '.', значит файл в корне input_dir, тогда output_subdir = output_dir
                    current_output_subdir = output_dir
                    if relative_subdir != ".":
                        current_output_subdir = os.path.join(output_dir, relative_subdir)
                    
                    if current_output_subdir not in files_to_process_map:
                        files_to_process_map[current_output_subdir] = []
                    files_to_process_map[current_output_subdir].append(input_file_path)
    else: # Если не рекурсивный поиск, то все файлы из корня input_dir идут в корень output_dir
        if output_dir not in files_to_process_map:
            files_to_process_map[output_dir] = []
        for item_name in os.listdir(input_dir):
            item_path = os.path.join(input_dir, item_name)
            if os.path.isfile(item_path) and item_name.lower().endswith(('.docx', '.txt')):
                files_to_process_map[output_dir].append(item_path)

    if not files_to_process_map or not any(files_to_process_map.values()):
        print(f"В директории {input_dir} (и ее подпапках, если рекурсивный поиск включен) "
              "не найдено файлов .docx или .txt для обработки.")
        return

    total_files_to_process = sum(len(files) for files in files_to_process_map.values())
    print(f"Найдено файлов для обработки: {total_files_to_process}")

    for target_output_subdir, input_file_paths_list in files_to_process_map.items():
        if not input_file_paths_list:
            continue

        # Создаем выходную поддиректорию, если ее нет
        if not os.path.isdir(target_output_subdir):
            print(f"Создание выходной поддиректории: {target_output_subdir}")
            os.makedirs(target_output_subdir, exist_ok=True)
            
        for file_path in input_file_paths_list:
            print(f"--- Обработка файла: {file_path} -> сохранение в {target_output_subdir} ---")
            # Передаем target_output_subdir в process_file_to_jsonl
            # В process_file_to_jsonl имя выходного файла будет формироваться на основе имени входного
            # и он будет сохранен в target_output_subdir
            if process_file_to_jsonl(file_path, target_output_subdir, input_dir):
                files_processed_count += 1
            
    print(f"\nОбработка датасета завершена. Всего обработано файлов: {files_processed_count}")

if __name__ == "__main__":
    # По умолчанию теперь рекурсивный поиск включен
    run_dataset_creation_pipeline(recursive_search=True)
    
    # Для теста можно создать структуру в input_texts:
    # input_texts/
    #   ├── book1/
    #   │   ├── chapter1.txt
    #   │   └── chapter2.docx
    #   └── standalone.txt
    # Ожидаемый результат в processed_data:
    # processed_data/
    #   ├── book1/
    #   │   ├── chapter1.jsonl
    #   │   └── chapter2.jsonl
    #   └── standalone.jsonl
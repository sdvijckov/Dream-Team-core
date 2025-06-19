import os

def create_file_with_placeholder(filepath, placeholder_text=""):
    """Создает файл с текстом-заглушкой, если он не существует."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Placeholder for {os.path.basename(filepath)}\n{placeholder_text}\n")
        print(f"      Создан файл: {filepath}")
    else:
        print(f"      Файл уже существует: {filepath}")


def create_structure_recursive(base_path, structure_dict, is_package=False):
    """Рекурсивно создает папки и файлы для вложенных структур."""
    if is_package:
        create_file_with_placeholder(os.path.join(base_path, "__init__.py"))

    for name, content in structure_dict.items():
        if name == "_is_package_": # Пропускаем служебный ключ
            continue
        
        current_path = os.path.join(base_path, name)
        
        if isinstance(content, dict): # Это папка
            is_sub_package = content.get("_is_package_", True)
            print(f"    Создана/проверена папка: {current_path}")
            os.makedirs(current_path, exist_ok=True) # Создаем папку здесь
            create_structure_recursive(current_path, content, is_package=is_sub_package) # Рекурсивный вызов
        elif isinstance(content, str): # Это файл с плейсхолдером
            create_file_with_placeholder(current_path, content)
        elif content is None: # Это пустой файл-заглушка
             create_file_with_placeholder(current_path)


def setup_dream_team_core_structure():
    base_dir = os.getcwd()
    print(f"Создание структуры для Dream Team Core в: {base_dir}")

    core_structure = {
        "assets": {
            "_is_package_": False,
            "icons": {"_is_package_": False, "app_icon.png": "# Placeholder for Core app icon"},
            "logos": {"_is_package_": False, "company_logo.png": "# Placeholder for company logo"},
            "fonts": {"_is_package_": False},
            "images": {"_is_package_": False},
            "text_resources": {
                "_is_package_": False,
                "splash_screen_info.md": "# Информация для стартового экрана\n\n## О компании\nОписание..."
            }
        },
        "settings": {
            "_is_package_": True,
            "src": {
                "_is_package_": True,
                "settings_manager.py": None
            },
            "config_files": {
                "_is_package_": False,
                "app_settings.json": "{\n  \"first_run\": true\n}"
            }
        },
        "dataset_preparation": {
            "_is_package_": True,
            "src": {
                "_is_package_": True,
                "text_parser.py": "# Previous code for text_parser.py",
                "dataset_creator.py": "# Previous code for dataset_creator.py"
            },
            "input_texts": {"_is_package_": False},
            "processed_data": {"_is_package_": False}
        },
        "profile_generation": {
            "_is_package_": True,
            "src": {
                "_is_package_": True,
                "profile_generator.py": None
            },
            "generated_profiles": {"_is_package_": False},
            "system_prompts": {"_is_package_": False}
        },
        "model_training": {
            "_is_package_": True,
            "src": {
                "_is_package_": True,
                "model_trainer.py": None
            },
            "training_input_data": {"_is_package_": False},
            "trained_models_info": {"_is_package_": False}
        },
        "ui_core": {
            "_is_package_": True,
            "main_core_ui.py": "# Kivy App for Core",
            "screens": {"_is_package_": True, "splash_screen.py": "# Kivy Splash Screen logic"},
            "widgets": {"_is_package_": True}
        },
        # Файлы на верхнем уровне проекта
        "main_core_launcher.py": "# Main launcher for Dream Team Core"
    }
    
    for top_level_name, top_level_content in core_structure.items():
        current_path = os.path.join(base_dir, top_level_name)
        if isinstance(top_level_content, dict): # Это папка на верхнем уровне
            is_package = top_level_content.get("_is_package_", True)
            if top_level_name == "assets": # assets не пакет
                 is_package = False
            print(f"  Создана/проверена папка верхнего уровня: {current_path}")
            os.makedirs(current_path, exist_ok=True)
            create_structure_recursive(current_path, top_level_content, is_package=is_package)
        elif isinstance(top_level_content, (str, type(None))): # Это файл на верхнем уровне
            placeholder = top_level_content if isinstance(top_level_content, str) else ""
            create_file_with_placeholder(current_path, placeholder)
            
    print("\nСтруктура Dream Team Core успешно создана/проверена.")

if __name__ == "__main__":
    setup_dream_team_core_structure()
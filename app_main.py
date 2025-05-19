# Файл: dream_team_core/app_main.py

import os
# Установка переменной окружения KIVY_GL_BACKEND (часто нужно для Windows)
# Делаем это до первого импорта Kivy
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2' # или 'sdl2', 'glew' - можно поэкспериментировать

from gui.main_app import MainApp # Импортируем класс нашего Kivy-приложения

if __name__ == '__main__':
    print("Запуск главного приложения Dream Team Core...")
    # В будущем здесь может быть код для проверки зависимостей, настройки логгирования и т.д.
    
    # Запуск Kivy приложения
    app_instance = MainApp()
    app_instance.run()
    print("Приложение Dream Team Core завершило работу.")
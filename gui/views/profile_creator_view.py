# Файл: dream_team_core/gui/views/profile_creator_view.py

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder # Для загрузки KV файла

# Загружаем KV файл для этого виджета (экрана)
# Имя файла должно соответствовать имени класса в нижнем регистре, без "View" или "Screen"
# ProfileCreatorView -> profilecreator.kv (Kivy автоматически ищет так)
# Но мы можем указать явно, что удобнее для структуры:
Builder.load_file('gui/views/profile_creator_view.kv') # Путь относительно корня проекта

class ProfileCreatorView(BoxLayout): # Наш главный контейнер для этого экрана
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Здесь можно будет инициализировать логику, связанную с этим экраном,
        # например, загрузку моделей GPTunnel при старте и т.д.
        self.ids.generated_profile_output.text = "Здесь будет отображен сгенерированный профиль Агента..."

    def generate_profile_action(self):
        # Эта функция будет вызываться при нажатии кнопки "Сгенерировать Профиль"
        # Пока просто выводим информацию из полей
        api_key = self.ids.api_key_input.text
        agent_name = self.ids.agent_name_input.text
        agent_role = self.ids.agent_role_input.text
        # ... (получить остальные данные по их id из .kv файла)
        
        # Имитация вызова логики из core
        self.ids.generated_profile_output.text = (
            f"Запрос на генерацию профиля...\n"
            f"API Ключ: {'*' * len(api_key) if api_key else 'Не указан'}\n"
            f"Имя Агента: {agent_name}\n"
            f"Роль: {agent_role}\n"
            f"Остальные параметры: (пока не получаем)\n\n"
            f"В будущем здесь будет реальный вызов функции из "
            f"core.agent_profile_creator.generate_agent_profile()"
        )
        print("Действие: Сгенерировать профиль")
        print(f"API Key: {api_key}")
        print(f"Agent Name: {agent_name}")
        print(f"Agent Role: {agent_role}")

    def clear_fields_action(self):
        self.ids.api_key_input.text = ""
        self.ids.agent_name_input.text = ""
        self.ids.agent_role_input.text = ""
        # ... (очистить остальные поля)
        self.ids.generated_profile_output.text = "Поля очищены. Здесь будет отображен сгенерированный профиль Агента..."
        print("Действие: Очистить поля")

    def copy_profile_action(self):
        # Логика копирования текста в буфер обмена
        # from kivy.core.clipboard import Clipboard
        # Clipboard.copy(self.ids.generated_profile_output.text)
        # self.ids.status_label.text = "Профиль скопирован в буфер обмена!"
        print("Действие: Копировать профиль (пока заглушка)")
        self.ids.generated_profile_output.text += "\n(Профиль скопирован - имитация)"
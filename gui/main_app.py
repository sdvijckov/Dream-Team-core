# Файл: dream_team_core/gui/main_app.py

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen # Для управления несколькими экранами
from .views.profile_creator_view import ProfileCreatorView # Импортируем наш экран

# Можно задать минимальную версию Kivy, если нужно
# from kivy import require
# require('2.0.0') # Например, если используем фичи из Kivy 2.0+

class MainApp(App):
    def build(self):
        # Создаем ScreenManager для управления экранами
        self.screen_manager = ScreenManager()

        # Создаем экран для создания профиля
        profile_screen = Screen(name='profile_creator')
        profile_screen.add_widget(ProfileCreatorView()) # Добавляем наш виджет на экран
        self.screen_manager.add_widget(profile_screen)

        # В будущем здесь можно будет добавлять другие экраны
        # training_screen = Screen(name='model_training')
        # training_screen.add_widget(ModelTrainingView()) 
        # self.screen_manager.add_widget(training_screen)
        # self.screen_manager.current = 'model_training' # Установить стартовый экран

        self.screen_manager.current = 'profile_creator' # Устанавливаем этот экран как текущий
        return self.screen_manager

    def on_start(self):
        # Действия при старте приложения
        print("Приложение Dream Team Core (Kivy) запущено!")
        # Здесь можно, например, загрузить список моделей для Spinner
        # self.load_gptunnel_models_for_spinner()

    # def load_gptunnel_models_for_spinner(self):
        # Эта функция позже будет вызывать client.get_models() 
        # и обновлять values у self.screen_manager.get_screen('profile_creator').ids.model_selector_spinner.values
        # pass

if __name__ == '__main__': # Этот блок здесь не нужен, если запускаем через app_main.py
    pass
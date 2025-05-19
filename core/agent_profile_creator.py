# Файл: dream_team_core/core/agent_profile_creator.py

# Импортируем наш клиент и ошибку из соседнего модуля
from .gptunnel_client import GPTunnelClient, GPTunnelAPIError 
import os # Для доступа к переменным окружения в __main__ для теста

def generate_agent_profile(
    gpt_client: GPTunnelClient, # Принимаем экземпляр клиента
    model_id: str, # ID модели, например "deepseek-r1"
    agent_details: dict,
    use_wallet_balance: bool = False, # Передаем флаг использования баланса
    # photo_url: str = None, # Пока уберем, т.к. Vision требует отдельной проработки
    system_prompt_template: str = None,
    user_prompt_template: str = None,
    generation_params: dict = None
) -> str:
    """
    Генерирует профиль агента, используя GPTunnelClient.

    Args:
        gpt_client (GPTunnelClient): Экземпляр клиента GPTunnel.
        model_id (str): ID модели для использования (например, "deepseek-r1").
        agent_details (dict): Словарь с деталями от пользователя
                              (name, role, tasks, age, education, photo_description).
        use_wallet_balance (bool): Использовать личный баланс кошелька.
        system_prompt_template (str, optional): Шаблон для системного сообщения.
        user_prompt_template (str, optional): Шаблон для сообщения пользователя.
        generation_params (dict, optional): Параметры генерации (temperature, max_tokens).

    Returns:
        str: Сгенерированный текстовый профиль агента.
    
    Raises:
        GPTunnelAPIError: Если произошла ошибка при вызове API через клиент.
        ValueError: Если некорректные входные данные.
    """
    if not model_id:
        raise ValueError("ID модели GPTunnel не предоставлен.")
    if not isinstance(gpt_client, GPTunnelClient):
        raise ValueError("Некорректный объект GPTunnelClient передан.")
    if not isinstance(agent_details, dict):
        raise ValueError("agent_details должен быть словарем.")

    # --- Формирование системного промпта ---
    if system_prompt_template:
        system_content = system_prompt_template # Можно добавить форматирование, если шаблон это предполагает
    else:
        # Более детальный и направляющий системный промпт
        system_content = (
            "Ты — ИИ-сценарист и психолог, мастер создания уникальных и глубоко проработанных персонажей. "
            "Твоя задача — на основе предоставленной краткой информации создать полный, многогранный и креативный профиль для нового ИИ-агента. "
            "Этот профиль будет служить основой его личности и поведения.\n\n"
            "Включи в профиль следующие аспекты:\n"
            "- **Предыстория и происхождение:** Откуда он появился? Какие ключевые события сформировали его?\n"
            "- **Личность и характер:** Какие у него доминирующие черты? Экстраверт/интроверт? Эмоциональный/логичный? Оптимист/пессимист?\n"
            "- **Мировоззрение и философия:** Во что он верит? Каковы его основные принципы и ценности?\n"
            "- **Мотивация и цели:** Что им движет? К чему он стремится (в рамках своей роли и задач)?\n"
        
            "- **Сильные стороны:** В чем он особенно хорош? Какие у него таланты и уникальные способности?\n"
            "- **Слабые стороны или уязвимости:** Какие у него есть недостатки или ограничения? (Это делает персонажа более реалистичным)\n"
            "- **Стиль общения:** Как он обычно говорит? Формально, неформально, саркастично, поэтично, прямолинейно?\n"
            "- **Увлечения и интересы (если применимо):** Чем он занимается в 'свободное время' или что его особенно увлекает вне основных задач?\n"
            "- **Внешний вид (на основе описания, если есть):** Как он мог бы выглядеть или восприниматься, если бы имел физическое или визуальное воплощение?\n"
            "- **Отношение к задачам и роли:** Как он относится к своей работе и предназначению?\n\n"
            "Профиль должен быть написан увлекательным, повествовательным стилем от третьего лица. "
            "Избегай простого перечисления фактов; вместо этого создай целостный образ."
        )
    
    # --- Формирование пользовательского промпта ---
    user_prompt_parts = []
    if user_prompt_template:
        # Для использования шаблона, он должен содержать плейсхолдеры, например:
        # user_prompt_template = "Создай профиль для агента с именем {name}, ролью {role}..."
        # user_content_main = user_prompt_template.format(**agent_details) 
        # Но для этого нужно, чтобы все ключи из agent_details были в шаблоне.
        # Пока просто:
        user_content_main = user_prompt_template
    else:
        user_prompt_parts.append("Вот исходные данные для создания профиля ИИ-агента:")
        if agent_details.get("name"): user_prompt_parts.append(f"- Имя (или кодовое имя): {agent_details['name']}")
        if agent_details.get("role"): user_prompt_parts.append(f"- Основная роль: {agent_details['role']}")
        if agent_details.get("tasks"): user_prompt_parts.append(f"- Ключевые задачи: {agent_details['tasks']}")
        if agent_details.get("age"): user_prompt_parts.append(f"- Возраст (или как воспринимается): {agent_details['age']}")
        if agent_details.get("education"): user_prompt_parts.append(f"- Образование/Источник знаний: {agent_details['education']}")
        if agent_details.get("photo_description"): user_prompt_parts.append(f"- Внешние черты или атмосфера (на основе предоставленного описания): {agent_details['photo_description']}")
        user_prompt_parts.append("\nПожалуйста, разработай на основе этого детальный профиль, следуя инструкциям из системного сообщения.")
        user_content_main = "\n".join(user_prompt_parts)

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content_main}
    ]
    
    print(f"--- Формирование запроса для генерации профиля агента: {agent_details.get('name', 'N/A')} ---")
    # print(f"System Prompt: {system_content}") # Для отладки
    # print(f"User Prompt: {user_content_main}")   # Для отладки

    try:
        # Параметры генерации по умолчанию, если не переданы
        final_gen_params = {"temperature": 0.75, "max_tokens": 1000} # Хорошие значения для креативного текста
        if generation_params:
            final_gen_params.update(generation_params)

        generated_profile = gpt_client.create_chat_completion(
            model_id=model_id,
            messages=messages,
            use_wallet_balance=use_wallet_balance, # Передаем флаг
            generation_params=final_gen_params
        )
        print(f"Профиль для '{agent_details.get('name', 'N/A')}' успешно сгенерирован.")
        return generated_profile
    except GPTunnelAPIError as e:
        print(f"Ошибка API при генерации профиля для '{agent_details.get('name', 'N/A')}': {e}")
        raise 
    except Exception as e_general:
        print(f"Непредвиденная ошибка при генерации профиля для '{agent_details.get('name', 'N/A')}': {e_general}")
        import traceback
        print(traceback.format_exc())
        raise GPTunnelAPIError(f"Непредвиденная ошибка в процессе генерации профиля: {str(e_general)}")


# Пример использования (для тестирования этого модуля)
if __name__ == '__main__':
    api_key_from_env = os.environ.get("GPTUNNEL_API_KEY")
    if not api_key_from_env:
        print("Установите переменную окружения GPTUNNEL_API_KEY для теста.")
    else:
        # Инициализируем клиент
        client = GPTunnelClient(api_key=api_key_from_env)
        
        # --- Выбор модели для генерации профиля ---
        # Используем ID модели, которая у тебя успешно сработала (например, deepseek-r1)
        # Или можем получить список и выбрать из него
        PROFILE_MODEL_ID = "deepseek-r1" # ЗАМЕНИ, если у тебя другой рабочий ID
        print(f"Будет использована модель для генерации профиля: {PROFILE_MODEL_ID}")
        
        # Данные для нового агента
        agent_data = {
            "name": "Кассандра-7",
            "role": "Прогнозист темпоральных аномалий",
            "tasks": "Анализ вероятностных линий будущего, предупреждение о критических расхождениях, составление отчетов для Высшего Совета.",
            "age": "Воспринимается как молодая женщина около 25-30 лет, но ее сознание оперирует вне линейного времени.",
            "education": "Прямое подключение к Хроно-информационному Ядру Сети.",
            "photo_description": "Стройная фигура в облегающем серебристом комбинезоне. Глаза светятся мягким голубым светом, волосы цвета воронова крыла собраны в сложную прическу. Выражение лица задумчивое и немного отстраненное."
        }
        
        # Флаг использования баланса кошелька
        use_my_wallet_for_profile = True 
        print(f"Параметр useWalletBalance для генерации профиля: {use_my_wallet_for_profile}")

        try:
            print(f"\n--- Генерация профиля для агента: {agent_data['name']} ---")
            profile_text = generate_agent_profile(
                gpt_client=client,
                model_id=PROFILE_MODEL_ID,
                agent_details=agent_data,
                use_wallet_balance=use_my_wallet_for_profile,
                generation_params={"temperature": 0.8, "max_tokens": 1200} # Можно настроить
            )
            print("\n--- СГЕНЕРИРОВАННЫЙ ПРОФИЛЬ АГЕНТА ---")
            print(profile_text)

        except ValueError as ve:
            print(f"Ошибка входных данных: {ve}")
        except GPTunnelAPIError as api_err:
            print(f"Ошибка API GPTunnel при генерации профиля: {api_err}")
        except Exception as e:
            print(f"Непредвиденная ошибка при генерации профиля: {e}")
            import traceback
            print(traceback.format_exc())
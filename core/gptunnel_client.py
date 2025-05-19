# Файл: dream_team_core/core/gptunnel_client.py

import requests
import json
import os

GPTUNNEL_BASE_URL = "https://gptunnel.ru/v1" # Базовый URL API

class GPTunnelAPIError(Exception):
    """Кастомное исключение для ошибок GPTunnel API."""
    def __init__(self, message, status_code=None, response_text=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self):
        details = super().__str__()
        if self.status_code is not None:
            details += f" (Status: {self.status_code})"
        if self.response_text is not None and self.response_text != "No response content": # Не выводим "No response content" если он неинформативен
            # Попытаемся красиво отформатировать JSON, если это он
            try:
                parsed_response = json.loads(self.response_text)
                pretty_response = json.dumps(parsed_response, indent=2, ensure_ascii=False)
                details += f"\nResponse Body:\n{pretty_response}"
            except json.JSONDecodeError:
                details += f"\nResponse Body (raw):\n{self.response_text}"
        return details


class GPTunnelClient:
    def __init__(self, api_key: str):
        """
        Клиент для взаимодействия с GPTunnel API.

        Args:
            api_key (str): API ключ для GPTunnel.
        """
        if not api_key:
            raise ValueError("API ключ GPTunnel не предоставлен.")
        self.api_key = api_key
        self.base_headers = {
            "Authorization": self.api_key, # Просто ключ, как указано в документации
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, payload: dict = None, params: dict = None) -> dict:
        """Приватный метод для выполнения HTTP запросов."""
        url = f"{GPTUNNEL_BASE_URL}{endpoint}"
        # print(f"--- DEBUG: Requesting {method} {url} ---") # Для отладки
        # if payload:
        #     print(f"--- DEBUG: Payload: {json.dumps(payload, indent=2, ensure_ascii=False)} ---") # Для отладки
            
        try:
            response = requests.request(method, url, headers=self.base_headers, json=payload, params=params, timeout=180)
            response.raise_for_status() 
            
            # Некоторые API могут возвращать пустой ответ с кодом 204 No Content
            if response.status_code == 204:
                return {} # Возвращаем пустой словарь, если нет контента
            
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            response_text = http_err.response.text if http_err.response is not None else "No response content"
            status_code = http_err.response.status_code if http_err.response is not None else None
            
            # Если это 402, и мы не передавали useWalletBalance, можно добавить совет
            # Но лучше, чтобы вызывающий код сам решал, как обрабатывать 402
            raise GPTunnelAPIError(
                f"Ошибка HTTP при запросе к {url}", # Сообщение станет более детальным в __str__
                status_code=status_code,
                response_text=response_text
            )
        except requests.exceptions.RequestException as req_err:
            raise GPTunnelAPIError(f"Ошибка сети/соединения при запросе к {url}: {req_err}")
        except json.JSONDecodeError as json_err:
            response_text_on_json_error = ""
            if 'response' in locals() and hasattr(response, 'text'): # Проверяем, что response определена
                response_text_on_json_error = response.text
            raise GPTunnelAPIError(f"Не удалось декодировать JSON ответ от {url}. Ошибка: {json_err}", response_text=response_text_on_json_error)


    def get_models(self) -> list:
        """Получает список доступных моделей."""
        # Эндпоинт: GET /v1/models
        response_data = self._request("GET", "/models")
        if "data" in response_data and isinstance(response_data["data"], list):
            return [{"id": model.get("id"), "title": model.get("title", model.get("id"))}
                    for model in response_data["data"] if model.get("id")]
        else:
            raise GPTunnelAPIError(f"Неожиданный формат ответа от /models", response_text=str(response_data))

    def create_chat_completion(
            self, 
            model_id: str, 
            messages: list, 
            use_wallet_balance: bool = False, # Новый параметр!
            generation_params: dict = None
        ) -> str:
        """
        Создает текстовое завершение с использованием /v1/chat/completions.

        Args:
            model_id (str): ID модели для использования.
            messages (list): Список сообщений.
            use_wallet_balance (bool): Использовать личный баланс кошелька.
            generation_params (dict, optional): Параметры генерации (temperature, max_tokens, etc.).

        Returns:
            str: Сгенерированный текст ответа.
        """
        # Эндпоинт: POST /v1/chat/completions
        payload = {
            "model": model_id,
            "messages": messages,
            "useWalletBalance": use_wallet_balance # Вот он, наш параметр!
        }
        if generation_params:
            # Убедимся, что не перезаписываем ключевые параметры если они уже есть в generation_params
            # и что они не конфликтуют с обязательными
            for key, value in generation_params.items():
                 if key not in ["model", "messages", "useWalletBalance"]:
                      payload[key] = value
        
        response_data = self._request("POST", "/chat/completions", payload=payload)
        
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                message_content = choice["message"]["content"]
                return message_content.strip() if message_content else "" # Возвращаем пустую строку, если content is None
            # Альтернативный вариант из документации для /v1/assistant/chat, может быть и здесь:
            elif "text" in choice: 
                return choice["text"].strip()
            else:
                 raise GPTunnelAPIError(f"Ответ получен, но отсутствует 'content' в 'message' или 'text' в 'choice'.", response_text=str(response_data))
        else:
            raise GPTunnelAPIError(f"Неожиданный формат ответа от /chat/completions: отсутствует 'choices' или он пуст.", response_text=str(response_data))

# Пример использования (для тестирования этого модуля)
if __name__ == '__main__':
    api_key_from_env = os.environ.get("GPTUNNEL_API_KEY")
    if not api_key_from_env:
        print("Установите переменную окружения GPTUNNEL_API_KEY для теста.")
    else:
        # Инициализируем клиент
        client = GPTunnelClient(api_key=api_key_from_env)
        
        print("--- Тест получения списка моделей ---")
        models = []
        try:
            models = client.get_models()
            if not models:
                print("Список моделей пуст. Тестирование прервано.")
                exit()

            print("Доступные модели:")
            for i, model in enumerate(models):
                print(f"  [{i}] ID: {model['id']}, Title: {model['title']}")
        except GPTunnelAPIError as api_err:
            print(f"Ошибка API GPTunnel при получении списка моделей: {api_err}")
            print("Продолжение без списка моделей невозможно.")
            exit()
        except Exception as e:
            print(f"Непредвиденная ошибка при получении списка моделей: {e}")
            import traceback
            print(traceback.format_exc())
            exit()
            
        # --- Выбор модели для теста чата ---
        # Укажи здесь ID модели, которую хочешь протестировать, например "deepseek-chat" или другой из списка
        # Если GPTunnel имеет модель с ID "deepseek-r1", то так и пиши.
        # Но обычно ID моделей для чата содержат "chat", "gpt", "claude" и т.д.
        # Посмотри точный ID в списке моделей, который выводится выше.
        target_model_id_for_test = "deepseek-r1" # ЗАМЕНИ НА РЕАЛЬНЫЙ ID ИЗ СПИСКА МОДЕЛЕЙ
        
        # Проверка, есть ли такая модель в списке (опционально, но полезно)
        if not any(m['id'] == target_model_id_for_test for m in models):
            print(f"\nВНИМАНИЕ: Модель '{target_model_id_for_test}' не найдена в списке доступных моделей.")
            print("Пожалуйста, выберите ID из списка выше и исправьте 'target_model_id_for_test'.")
            # Попробуем взять первую модель из списка, если она есть, и она похожа на чатовую
            found_fallback = False
            for m_info in models:
                if "chat" in m_info['id'].lower() or "gpt" in m_info['id'].lower() or "claude" in m_info['id'].lower() or "gemini" in m_info['id'].lower() or "command" in m_info['id'].lower() or "mistral" in m_info['id'].lower() or "llama" in m_info['id'].lower() or "deepseek" in m_info['id'].lower():
                    target_model_id_for_test = m_info['id']
                    print(f"Автоматически выбрана первая подходящая чат-модель для теста: {target_model_id_for_test}")
                    found_fallback = True
                    break
            if not found_fallback:
                print("Не найдено подходящих чат-моделей в списке для автоматического выбора. Пропуск теста чата.")
                exit()
        
        print(f"\n--- Тест чата с моделью: {target_model_id_for_test} ---")
        test_messages = [
            {"role": "system", "content": "Ты дружелюбный и остроумный ассистент."},
            {"role": "user", "content": "Расскажи короткий смешной анекдот про программиста."}
        ]
        # Параметры генерации (можно менять)
        test_gen_params = {"temperature": 0.7, "max_tokens": 150} 
        
        # Флаг использования баланса кошелька
        # Установи в True, если хочешь использовать средства с баланса
        use_my_wallet = True 
        print(f"Параметр useWalletBalance будет установлен в: {use_my_wallet}")

        try:
            chat_response = client.create_chat_completion(
                model_id=target_model_id_for_test,
                messages=test_messages,
                use_wallet_balance=use_my_wallet, # Передаем флаг
                generation_params=test_gen_params
            )
            print("\nОтвет от модели:")
            print(chat_response)
        except GPTunnelAPIError as api_err:
            print(f"Ошибка API GPTunnel при выполнении чата: {api_err}")
        except Exception as e:
            print(f"Непредвиденная ошибка при выполнении чата: {e}")
            import traceback
            print(traceback.format_exc())
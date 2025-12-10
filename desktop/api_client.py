"""
HTTP клиент для работы с backend API
"""
import requests
from typing import Optional, Dict, Any
import json

BASE_URL = "http://localhost:8000"


class APIClient:
    """Клиент для взаимодействия с backend API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip('/')
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Обработка ответа с улучшенной обработкой ошибок"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP ошибка {response.status_code}"
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    error_msg += f": {error_data['detail']}"
            except:
                error_msg += f": {response.text[:200]}"
            raise Exception(error_msg) from e
        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка парсинга JSON: {str(e)}") from e
        except Exception as e:
            raise Exception(f"Неожиданная ошибка: {str(e)}") from e
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Универсальный метод для выполнения запросов"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(method, url, timeout=60, **kwargs)
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            raise Exception("Не удалось подключиться к серверу. Убедитесь, что backend запущен на http://localhost:8000")
        except requests.exceptions.Timeout:
            raise Exception("Превышено время ожидания ответа от сервера")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка запроса: {str(e)}") from e
        except Exception as e:
            raise Exception(f"Неожиданная ошибка: {str(e)}") from e
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Анализ текста"""
        return self._make_request('POST', '/analyze_text', json={"text": text})
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Анализ изображения"""
        import os
        import mimetypes
        
        try:
            # Определяем MIME-тип по расширению файла
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                # Если не определили, пробуем по расширению
                ext = os.path.splitext(image_path)[1].lower()
                mime_map = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }
                mime_type = mime_map.get(ext, 'image/png')
            
            # Получаем имя файла
            filename = os.path.basename(image_path)
            
            # Открываем файл и отправляем с правильным именем и типом
            with open(image_path, 'rb') as f:
                files = {
                    'file': (filename, f, mime_type)
                }
                return self._make_request('POST', '/analyze_image', files=files)
        except FileNotFoundError:
            raise Exception(f"Файл не найден: {image_path}")
        except IOError as e:
            raise Exception(f"Ошибка чтения файла: {str(e)}") from e
    
    def parse_demo(self, url: str) -> Dict[str, Any]:
        """Парсинг сайта"""
        return self._make_request('POST', '/parse_demo', json={"url": url})
    
    def get_history(self) -> Dict[str, Any]:
        """Получить историю"""
        return self._make_request('GET', '/history')
    
    def clear_history(self) -> Dict[str, Any]:
        """Очистить историю"""
        return self._make_request('DELETE', '/history')
    
    def health_check(self) -> bool:
        """Проверка доступности сервера"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


api_client = APIClient()


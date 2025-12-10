"""
Сервис для парсинга веб-страниц
"""
import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse

from backend.config import settings

# Selenium импорты (опционально)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Предупреждение: Selenium не установлен. Установите: pip install selenium webdriver-manager")


class ParserService:
    """Сервис для парсинга веб-страниц"""
    
    def __init__(self):
        self.timeout = settings.parser_timeout
        self.user_agent = settings.parser_user_agent
        self.use_selenium = settings.use_selenium and SELENIUM_AVAILABLE
        self.selenium_timeout = settings.selenium_timeout
        self.selenium_headless = settings.selenium_headless
        self.selenium_wait_time = settings.selenium_wait_time
        self.competitor_urls = [url.strip() for url in settings.competitor_urls.split(",") if url.strip()] if settings.competitor_urls else []
        
        # Инициализация Selenium драйвера (ленивая загрузка)
        self._driver = None
    
    def _get_selenium_driver(self):
        """Получить или создать Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError("Selenium не установлен")
        
        if self._driver is None:
            chrome_options = Options()
            if self.selenium_headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={self.user_agent}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            try:
                service = Service(ChromeDriverManager().install())
                self._driver = webdriver.Chrome(service=service, options=chrome_options)
                self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as e:
                print(f"Ошибка инициализации Selenium: {e}")
                raise
        
        return self._driver
    
    def _close_selenium_driver(self):
        """Закрыть Selenium WebDriver"""
        if self._driver:
            try:
                self._driver.quit()
            except:
                pass
            self._driver = None
    
    def parse_url_with_selenium(self, url: str) -> Dict[str, Optional[str]]:
        """
        Парсинг веб-страницы с использованием Selenium (для JS-контента)
        
        Args:
            url: URL для парсинга
            
        Returns:
            Словарь с title, h1, first_paragraph
        """
        driver = None
        try:
            driver = self._get_selenium_driver()
            driver.set_page_load_timeout(self.selenium_timeout)
            driver.get(url)
            
            # Ждем загрузки контента
            WebDriverWait(driver, self.selenium_wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Получаем HTML после выполнения JavaScript
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # Извлекаем данные
            title_tag = soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else None
            
            h1_tag = soup.find('h1')
            h1 = h1_tag.get_text(strip=True) if h1_tag else None
            
            first_paragraph = None
            content_selectors = ['article', 'main', '[role="main"]', 'body']
            for selector in content_selectors:
                content_area = soup.select_one(selector)
                if content_area:
                    paragraph = content_area.find('p')
                    if paragraph:
                        first_paragraph = paragraph.get_text(strip=True)
                        if len(first_paragraph) > 500:
                            first_paragraph = first_paragraph[:500] + "..."
                        break
            
            if not first_paragraph:
                paragraph = soup.find('p')
                if paragraph:
                    first_paragraph = paragraph.get_text(strip=True)
                    if len(first_paragraph) > 500:
                        first_paragraph = first_paragraph[:500] + "..."
            
            return {
                "url": url,
                "title": title,
                "h1": h1,
                "first_paragraph": first_paragraph
            }
            
        except TimeoutException:
            return {
                "url": url,
                "title": None,
                "h1": None,
                "first_paragraph": None,
                "error": "Timeout при загрузке страницы через Selenium"
            }
        except WebDriverException as e:
            return {
                "url": url,
                "title": None,
                "h1": None,
                "first_paragraph": None,
                "error": f"Ошибка Selenium: {str(e)}"
            }
        except Exception as e:
            return {
                "url": url,
                "title": None,
                "h1": None,
                "first_paragraph": None,
                "error": f"Ошибка парсинга через Selenium: {str(e)}"
            }
    
    def parse_url(self, url: str, use_selenium: Optional[bool] = None) -> Dict[str, Optional[str]]:
        """
        Парсинг веб-страницы
        
        Args:
            url: URL для парсинга
            use_selenium: Использовать Selenium (если None, используется настройка из config)
            
        Returns:
            Словарь с title, h1, first_paragraph
        """
        # Валидация URL
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"https://{url}"
        
        # Определяем, использовать ли Selenium
        should_use_selenium = use_selenium if use_selenium is not None else self.use_selenium
        
        # Если нужно использовать Selenium и он доступен
        if should_use_selenium and SELENIUM_AVAILABLE:
            return self.parse_url_with_selenium(url)
        
        # Иначе используем httpx (стандартный метод)
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                
                # httpx автоматически декодирует response.text на основе заголовков
                # Если кодировка не указана, использует utf-8 по умолчанию
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Извлекаем title
                title_tag = soup.find('title')
                title = title_tag.get_text(strip=True) if title_tag else None
                
                # Извлекаем h1
                h1_tag = soup.find('h1')
                h1 = h1_tag.get_text(strip=True) if h1_tag else None
                
                # Извлекаем первый абзац (из основного контента)
                first_paragraph = None
                
                # Пробуем найти основной контент (article, main, или body)
                content_selectors = ['article', 'main', '[role="main"]', 'body']
                for selector in content_selectors:
                    content_area = soup.select_one(selector)
                    if content_area:
                        # Ищем первый параграф
                        paragraph = content_area.find('p')
                        if paragraph:
                            first_paragraph = paragraph.get_text(strip=True)
                            # Ограничиваем длину
                            if len(first_paragraph) > 500:
                                first_paragraph = first_paragraph[:500] + "..."
                            break
                
                # Если не нашли, берем первый p из body
                if not first_paragraph:
                    paragraph = soup.find('p')
                    if paragraph:
                        first_paragraph = paragraph.get_text(strip=True)
                        if len(first_paragraph) > 500:
                            first_paragraph = first_paragraph[:500] + "..."
                
                return {
                    "url": url,
                    "title": title,
                    "h1": h1,
                    "first_paragraph": first_paragraph
                }
                
        except httpx.TimeoutException:
            # Если httpx не сработал и Selenium доступен, пробуем Selenium как fallback
            if SELENIUM_AVAILABLE and not should_use_selenium:
                return self.parse_url_with_selenium(url)
            return {
                "url": url,
                "title": None,
                "h1": None,
                "first_paragraph": None,
                "error": "Timeout при загрузке страницы"
            }
        except httpx.HTTPStatusError as e:
            return {
                "url": url,
                "title": None,
                "h1": None,
                "first_paragraph": None,
                "error": f"HTTP ошибка {e.response.status_code}"
            }
        except Exception as e:
            return {
                "url": url,
                "title": None,
                "h1": None,
                "first_paragraph": None,
                "error": f"Ошибка парсинга: {str(e)}"
            }
    
    def parse_competitor_urls(self) -> List[Dict[str, Optional[str]]]:
        """
        Парсинг всех URL конкурентов из конфигурации
        
        Returns:
            Список результатов парсинга
        """
        results = []
        for url in self.competitor_urls:
            result = self.parse_url(url)
            results.append(result)
        return results
    
    def __del__(self):
        """Очистка ресурсов при удалении объекта"""
        self._close_selenium_driver()


# Глобальный экземпляр
parser_service = ParserService()


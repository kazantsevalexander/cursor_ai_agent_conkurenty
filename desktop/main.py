"""
Главное окно PyQt6 приложения
Мониторинг конкурентов - Desktop App
"""
import sys
import traceback
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QListWidget, QStackedWidget,
    QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from api_client import api_client
from styles import DARK_THEME

# Настройка логирования
LOG_FILE = os.path.join(os.path.dirname(__file__), "app.log")

def log_error(message: str, exception: Exception = None):
    """Логирование ошибок в файл"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
            if exception:
                f.write(f"Exception: {traceback.format_exc()}\n")
            f.write("-" * 80 + "\n")
    except:
        pass  # Если не можем записать в лог, просто игнорируем


def format_response_as_text(response: dict) -> str:
    """Преобразует JSON ответ в читаемый текст"""
    if not isinstance(response, dict):
        return str(response)
    
    # Проверяем наличие ошибки
    if response.get('error'):
        return f"❌ Ошибка: {response['error']}"
    
    if not response.get('success', False):
        return "❌ Запрос не выполнен успешно"
    
    result_parts = []
    
    # Обработка анализа текста
    if 'analysis' in response and response['analysis']:
        analysis = response['analysis']
        
        if 'summary' in analysis and analysis['summary']:
            result_parts.append("📋 ОБЩЕЕ РЕЗЮМЕ")
            result_parts.append("=" * 60)
            result_parts.append(analysis['summary'])
            result_parts.append("")
        
        if 'strengths' in analysis and analysis['strengths']:
            result_parts.append("✅ СИЛЬНЫЕ СТОРОНЫ")
            result_parts.append("-" * 60)
            for i, strength in enumerate(analysis['strengths'], 1):
                result_parts.append(f"{i}. {strength}")
            result_parts.append("")
        
        if 'weaknesses' in analysis and analysis['weaknesses']:
            result_parts.append("⚠️ СЛАБЫЕ СТОРОНЫ")
            result_parts.append("-" * 60)
            for i, weakness in enumerate(analysis['weaknesses'], 1):
                result_parts.append(f"{i}. {weakness}")
            result_parts.append("")
        
        if 'unique_offers' in analysis and analysis['unique_offers']:
            result_parts.append("💡 УНИКАЛЬНЫЕ ПРЕДЛОЖЕНИЯ")
            result_parts.append("-" * 60)
            for i, offer in enumerate(analysis['unique_offers'], 1):
                result_parts.append(f"{i}. {offer}")
            result_parts.append("")
        
        if 'recommendations' in analysis and analysis['recommendations']:
            result_parts.append("🎯 РЕКОМЕНДАЦИИ")
            result_parts.append("-" * 60)
            for i, rec in enumerate(analysis['recommendations'], 1):
                result_parts.append(f"{i}. {rec}")
            result_parts.append("")
    
    # Обработка анализа изображения
    if 'analysis' in response and response['analysis']:
        analysis = response['analysis']
        
        if 'description' in analysis and analysis['description']:
            result_parts.append("🖼️ ОПИСАНИЕ ИЗОБРАЖЕНИЯ")
            result_parts.append("=" * 60)
            result_parts.append(analysis['description'])
            result_parts.append("")
        
        if 'visual_style_score' in analysis:
            result_parts.append(f"📊 Оценка визуального стиля: {analysis['visual_style_score']}/10")
        
        if 'design_score' in analysis:
            result_parts.append(f"📊 Оценка дизайна: {analysis['design_score']}/10")
        
        if 'visual_style_analysis' in analysis and analysis['visual_style_analysis']:
            result_parts.append("\n🎨 АНАЛИЗ ВИЗУАЛЬНОГО СТИЛЯ")
            result_parts.append("-" * 60)
            result_parts.append(analysis['visual_style_analysis'])
            result_parts.append("")
        
        if 'marketing_insights' in analysis and analysis['marketing_insights']:
            result_parts.append("💼 МАРКЕТИНГОВЫЕ ИНСАЙТЫ")
            result_parts.append("-" * 60)
            for i, insight in enumerate(analysis['marketing_insights'], 1):
                result_parts.append(f"{i}. {insight}")
            result_parts.append("")
        
        if 'animation_potential' in analysis and analysis['animation_potential']:
            result_parts.append("🎬 ПОТЕНЦИАЛ ДЛЯ АНИМАЦИИ")
            result_parts.append("-" * 60)
            result_parts.append(analysis['animation_potential'])
            result_parts.append("")
        
        if 'recommendations' in analysis and analysis['recommendations']:
            result_parts.append("🎯 РЕКОМЕНДАЦИИ")
            result_parts.append("-" * 60)
            for i, rec in enumerate(analysis['recommendations'], 1):
                result_parts.append(f"{i}. {rec}")
            result_parts.append("")
    
    # Обработка парсинга
    if 'data' in response and response['data']:
        data = response['data']
        
        if 'url' in data:
            result_parts.append(f"🌐 URL: {data['url']}")
            result_parts.append("")
        
        if 'title' in data and data['title']:
            result_parts.append(f"📄 Заголовок страницы: {data['title']}")
            result_parts.append("")
        
        if 'h1' in data and data['h1']:
            result_parts.append(f"📝 H1: {data['h1']}")
            result_parts.append("")
        
        if 'first_paragraph' in data and data['first_paragraph']:
            result_parts.append("📑 Первый абзац:")
            result_parts.append("-" * 60)
            result_parts.append(data['first_paragraph'])
            result_parts.append("")
        
        if 'analysis' in data and data['analysis']:
            result_parts.append("\n" + "=" * 60)
            result_parts.append("АНАЛИЗ ИЗВЛЕЧЕННОГО КОНТЕНТА")
            result_parts.append("=" * 60)
            analysis = data['analysis']
            
            if 'summary' in analysis and analysis['summary']:
                result_parts.append("\n📋 ОБЩЕЕ РЕЗЮМЕ")
                result_parts.append("-" * 60)
                result_parts.append(analysis['summary'])
                result_parts.append("")
            
            if 'strengths' in analysis and analysis['strengths']:
                result_parts.append("✅ СИЛЬНЫЕ СТОРОНЫ")
                result_parts.append("-" * 60)
                for i, strength in enumerate(analysis['strengths'], 1):
                    result_parts.append(f"{i}. {strength}")
                result_parts.append("")
            
            if 'weaknesses' in analysis and analysis['weaknesses']:
                result_parts.append("⚠️ СЛАБЫЕ СТОРОНЫ")
                result_parts.append("-" * 60)
                for i, weakness in enumerate(analysis['weaknesses'], 1):
                    result_parts.append(f"{i}. {weakness}")
                result_parts.append("")
            
            if 'recommendations' in analysis and analysis['recommendations']:
                result_parts.append("🎯 РЕКОМЕНДАЦИИ")
                result_parts.append("-" * 60)
                for i, rec in enumerate(analysis['recommendations'], 1):
                    result_parts.append(f"{i}. {rec}")
                result_parts.append("")
    
    if not result_parts:
        # Если ничего не найдено, возвращаем JSON для отладки
        return json.dumps(response, ensure_ascii=False, indent=2)
    
    return "\n".join(result_parts)


class WorkerThread(QThread):
    """Поток для выполнения API запросов"""
    finished = pyqtSignal(str)  # Изменено на str для безопасности
    error = pyqtSignal(str)
    
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
    
    def run(self):
        try:
            result = self.func(*self.args)
            # Преобразуем результат в читаемый текст
            try:
                if isinstance(result, dict):
                    # Проверяем, является ли это ответом истории (есть 'items' и 'total')
                    if 'items' in result and 'total' in result:
                        # Для истории просто сериализуем в JSON
                        result_str = json.dumps(result, ensure_ascii=False, indent=2, default=str)
                    else:
                        # Для других ответов используем форматирование
                        result_str = format_response_as_text(result)
                else:
                    result_str = str(result)
                log_error(f"WorkerThread: успешно получен результат, длина: {len(result_str)}")
                self.finished.emit(result_str)
            except Exception as e:
                log_error(f"WorkerThread: ошибка форматирования результата", e)
                self.error.emit(f"Ошибка обработки результата: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            if not error_msg:
                error_msg = f"Неизвестная ошибка: {type(e).__name__}"
            log_error(f"WorkerThread: исключение при выполнении", e)
            self.error.emit(error_msg)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мониторинг конкурентов - AI Ассистент")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(DARK_THEME)
        
        # Сохраняем ссылки на worker threads
        self._text_worker = None
        self._image_worker = None
        self._parse_worker = None
        self._history_worker = None
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(central_widget)
        
        # Боковая панель
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar, 0)
        
        # Контент
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)
        
        # Создаем вкладки
        self.create_tabs()
        
        # Показываем первую вкладку
        self.content_stack.setCurrentIndex(0)
    
    def create_sidebar(self):
        """Создание боковой панели"""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Логотип
        logo = QLabel("CompetitorAI")
        logo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        sidebar_layout.addWidget(logo)
        
        # Кнопки навигации
        self.nav_buttons = []
        tabs = ["Анализ текста", "Анализ изображений", "Парсинг", "История"]
        for i, tab_name in enumerate(tabs):
            btn = QPushButton(tab_name)
            btn.clicked.connect(lambda checked, idx=i: self.content_stack.setCurrentIndex(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        sidebar_layout.addStretch()
        
        # Статус
        self.status_label = QLabel("● Система активна")
        sidebar_layout.addWidget(self.status_label)
        
        return sidebar
    
    def create_tabs(self):
        """Создание вкладок контента"""
        # Вкладка 1: Анализ текста
        text_tab = self.create_text_tab()
        self.content_stack.addWidget(text_tab)
        
        # Вкладка 2: Анализ изображений
        image_tab = self.create_image_tab()
        self.content_stack.addWidget(image_tab)
        
        # Вкладка 3: Парсинг
        parse_tab = self.create_parse_tab()
        self.content_stack.addWidget(parse_tab)
        
        # Вкладка 4: История
        history_tab = self.create_history_tab()
        self.content_stack.addWidget(history_tab)
    
    def create_text_tab(self):
        """Вкладка анализа текста"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Анализ текста конкурента")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(label)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Вставьте текст для анализа...")
        layout.addWidget(self.text_input)
        
        btn = QPushButton("Проанализировать")
        btn.clicked.connect(self.analyze_text)
        layout.addWidget(btn)
        
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        layout.addWidget(self.text_result)
        
        return widget
    
    def create_image_tab(self):
        """Вкладка анализа изображений"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Анализ изображений")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(label)
        
        btn = QPushButton("Выбрать изображение")
        btn.clicked.connect(self.select_image)
        layout.addWidget(btn)
        
        self.image_result = QTextEdit()
        self.image_result.setReadOnly(True)
        layout.addWidget(self.image_result)
        
        return widget
    
    def create_parse_tab(self):
        """Вкладка парсинга"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Парсинг сайта")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        layout.addWidget(self.url_input)
        
        btn = QPushButton("Парсить и анализировать")
        btn.clicked.connect(self.parse_url)
        layout.addWidget(btn)
        
        self.parse_result = QTextEdit()
        self.parse_result.setReadOnly(True)
        layout.addWidget(self.parse_result)
        
        return widget
    
    def create_history_tab(self):
        """Вкладка истории"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("История запросов")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(label)
        
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)
        
        btn = QPushButton("Обновить историю")
        btn.clicked.connect(self.load_history)
        layout.addWidget(btn)
        
        return widget
    
    def _handle_text_result(self, result: str):
        """Обработчик результата анализа текста"""
        try:
            self.text_result.setText(result)
        except Exception as e:
            self.text_result.setText(f"❌ Ошибка отображения: {str(e)}")
    
    def _handle_text_error(self, error: str):
        """Обработчик ошибки анализа текста"""
        try:
            self.text_result.setText(f"❌ Ошибка: {error}")
        except Exception as e:
            print(f"Критическая ошибка в обработчике: {e}")
    
    def analyze_text(self):
        """Анализ текста"""
        text = self.text_input.toPlainText().strip()
        if not text:
            self.text_result.setText("Введите текст для анализа")
            return
        
        self.text_result.setText("Анализирую...")
        try:
            worker = WorkerThread(api_client.analyze_text, text)
            worker.finished.connect(self._handle_text_result)
            worker.error.connect(self._handle_text_error)
            # Сохраняем ссылку на worker, чтобы он не удалился
            self._text_worker = worker
            worker.start()
        except Exception as e:
            self.text_result.setText(f"❌ Ошибка при запуске: {str(e)}")
    
    def _handle_image_result(self, result: str):
        """Обработчик результата анализа изображения"""
        try:
            self.image_result.setText(result)
        except Exception as e:
            self.image_result.setText(f"❌ Ошибка отображения: {str(e)}")
    
    def _handle_image_error(self, error: str):
        """Обработчик ошибки анализа изображения"""
        try:
            self.image_result.setText(f"❌ Ошибка: {error}")
        except Exception as e:
            print(f"Критическая ошибка в обработчике: {e}")
    
    def select_image(self):
        """Выбор изображения"""
        from PyQt6.QtWidgets import QFileDialog
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Выбрать изображение", "", "Images (*.png *.jpg *.jpeg)"
            )
            if filename:
                self.image_result.setText("Анализирую...")
                worker = WorkerThread(api_client.analyze_image, filename)
                worker.finished.connect(self._handle_image_result)
                worker.error.connect(self._handle_image_error)
                # Сохраняем ссылку на worker
                self._image_worker = worker
                worker.start()
        except Exception as e:
            self.image_result.setText(f"❌ Ошибка при выборе файла: {str(e)}")
    
    def _handle_parse_result(self, result: str):
        """Обработчик результата парсинга"""
        try:
            self.parse_result.setText(result)
        except Exception as e:
            self.parse_result.setText(f"❌ Ошибка отображения: {str(e)}")
    
    def _handle_parse_error(self, error: str):
        """Обработчик ошибки парсинга"""
        try:
            self.parse_result.setText(f"❌ Ошибка: {error}")
        except Exception as e:
            print(f"Критическая ошибка в обработчике: {e}")
    
    def parse_url(self):
        """Парсинг URL"""
        url = self.url_input.text().strip()
        if not url:
            self.parse_result.setText("Введите URL для парсинга")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.setText(url)
        
        self.parse_result.setText("Парсирую...")
        try:
            worker = WorkerThread(api_client.parse_demo, url)
            worker.finished.connect(self._handle_parse_result)
            worker.error.connect(self._handle_parse_error)
            # Сохраняем ссылку на worker
            self._parse_worker = worker
            worker.start()
        except Exception as e:
            self.parse_result.setText(f"❌ Ошибка при запуске: {str(e)}")
    
    def _handle_history_result(self, result: str):
        """Обработчик результата загрузки истории"""
        try:
            # Парсим JSON ответ
            history_data = json.loads(result)
            
            self.history_list.clear()
            
            items = history_data.get('items', [])
            total = history_data.get('total', 0)
            
            if not items or total == 0:
                self.history_list.addItem("📭 История пуста")
                self.history_list.addItem("Выполните анализ текста, изображения или парсинг, чтобы увидеть историю")
                return
            
            # Форматируем каждый элемент истории
            for item in items:
                request_type = item.get('request_type', 'unknown')
                request_summary = item.get('request_summary', '')
                timestamp = item.get('timestamp', '')
                
                # Форматируем дату если есть
                if timestamp:
                    try:
                        from datetime import datetime
                        # Обрабатываем разные форматы timestamp
                        if isinstance(timestamp, str):
                            # Убираем 'Z' и обрабатываем ISO формат
                            timestamp_clean = timestamp.replace('Z', '+00:00')
                            if '+' in timestamp_clean or timestamp_clean.endswith('+00:00'):
                                dt = datetime.fromisoformat(timestamp_clean)
                            else:
                                dt = datetime.fromisoformat(timestamp_clean)
                            time_str = dt.strftime("%Y-%m-%d %H:%M")
                        else:
                            # Если это уже объект datetime
                            time_str = timestamp.strftime("%Y-%m-%d %H:%M")
                    except Exception as e:
                        # Если не удалось распарсить, используем как есть
                        time_str = str(timestamp)[:16] if len(str(timestamp)) > 16 else str(timestamp)
                else:
                    time_str = ""
                
                # Типы запросов на русском
                type_map = {
                    'text': '📝 Текст',
                    'image': '🖼️ Изображение',
                    'parse': '🌐 Парсинг'
                }
                type_label = type_map.get(request_type, f'❓ {request_type}')
                
                # Формируем строку для отображения
                if time_str:
                    display_text = f"[{time_str}] {type_label}: {request_summary[:55]}"
                else:
                    display_text = f"{type_label}: {request_summary[:60]}"
                
                if len(request_summary) > (55 if time_str else 60):
                    display_text += "..."
                
                self.history_list.addItem(display_text)
            
            # Добавляем информацию о количестве
            if total > 0:
                self.history_list.addItem("")
                self.history_list.addItem(f"Всего записей: {total}")
        except json.JSONDecodeError as e:
            self.history_list.clear()
            self.history_list.addItem(f"❌ Ошибка парсинга JSON: {str(e)}")
            self.history_list.addItem(f"Ответ: {result[:200]}")
        except Exception as e:
            self.history_list.clear()
            self.history_list.addItem(f"❌ Ошибка загрузки истории: {str(e)}")
            import traceback
            log_error(f"Ошибка в _handle_history_result: {str(e)}", e)
    
    def _handle_history_error(self, error: str):
        """Обработчик ошибки загрузки истории"""
        try:
            self.history_list.clear()
            self.history_list.addItem(f"❌ Ошибка: {error}")
        except Exception as e:
            print(f"Критическая ошибка в обработчике истории: {e}")
    
    def load_history(self):
        """Загрузка истории"""
        self.history_list.clear()
        self.history_list.addItem("Загрузка истории...")
        try:
            worker = WorkerThread(api_client.get_history)
            worker.finished.connect(self._handle_history_result)
            worker.error.connect(self._handle_history_error)
            # Сохраняем ссылку на worker
            self._history_worker = worker
            worker.start()
        except Exception as e:
            self.history_list.clear()
            self.history_list.addItem(f"❌ Ошибка при запуске: {str(e)}")


def exception_hook(exctype, value, tb):
    """Глобальный обработчик исключений для предотвращения вылетов"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print(f"Необработанное исключение:\n{error_msg}")
    log_error(f"Необработанное исключение: {exctype.__name__}: {value}", value)
    
    # Показываем диалог с ошибкой
    app = QApplication.instance()
    if app is not None:
        try:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Критическая ошибка")
            msg.setText(f"Произошла ошибка:\n{str(value)}\n\nДетали сохранены в {LOG_FILE}")
            msg.setDetailedText(error_msg)
            msg.exec()
        except Exception as e:
            print(f"Не удалось показать диалог ошибки: {e}")


def main():
    # Устанавливаем глобальный обработчик исключений
    sys.excepthook = exception_hook
    
    app = QApplication(sys.argv)
    
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        print(f"Ошибка при запуске приложения:\n{error_msg}")
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Ошибка запуска")
        msg.setText(f"Не удалось запустить приложение:\n{str(e)}")
        msg.setDetailedText(error_msg)
        msg.exec()
        sys.exit(1)


if __name__ == "__main__":
    main()


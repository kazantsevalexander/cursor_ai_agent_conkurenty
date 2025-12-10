"""
Сервис для работы с OpenAI API
"""
import base64
import json
import re
from typing import Optional
from io import BytesIO

from openai import OpenAI
from PIL import Image

from backend.config import settings
from backend.models.schemas import CompetitorAnalysis, ImageAnalysis


class OpenAIService:
    """Сервис для работы с OpenAI"""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY не установлен в .env файле")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.vision_model = settings.openai_vision_model
    
    def analyze_text(self, text: str) -> Optional[CompetitorAnalysis]:
        """
        Анализ текста конкурента
        
        Args:
            text: Текст для анализа
            
        Returns:
            CompetitorAnalysis или None при ошибке
        """
        prompt = f"""Проанализируй следующий текст конкурента в сфере авторского надзора за строительством объектов в Республике Беларусь и предоставь структурированный анализ в формате JSON.

Текст для анализа:
{text}

Сфокусируйся на специфике строительной отрасли Беларуси:
- Нормативная база (СНБ, ТКП, СНиП)
- Лицензирование и допуски СРО
- Качество материалов и технологий
- Соответствие стандартам и требованиям
- Опыт работы с государственными заказчиками
- Региональные особенности строительства в Беларуси

Верни JSON объект со следующей структурой:
{{
    "strengths": ["сильная сторона 1", "сильная сторона 2"],
    "weaknesses": ["слабая сторона 1", "слабая сторона 2"],
    "unique_offers": ["уникальное предложение 1", "уникальное предложение 2"],
    "recommendations": ["рекомендация 1", "рекомендация 2"],
    "summary": "краткое общее резюме анализа с акцентом на строительную специфику Беларуси"
}}

Важно: верни ТОЛЬКО валидный JSON, без дополнительного текста."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты эксперт по маркетинговому анализу и конкурентной разведке в сфере строительства и авторского надзора в Республике Беларусь. Знаешь специфику белорусского строительного рынка, нормативную базу (СНБ, ТКП), требования к лицензированию и особенности работы с государственными заказчиками. Всегда отвечай только валидным JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Извлекаем JSON из ответа (на случай если модель добавила текст)
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            analysis_data = json.loads(content)
            
            return CompetitorAnalysis(**analysis_data)
            
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON от OpenAI: {e}")
            print(f"Полученный ответ: {content[:500]}")
            return None
        except Exception as e:
            print(f"Ошибка при анализе текста: {e}")
            return None
    
    def _image_to_base64(self, image_data: bytes) -> str:
        """Конвертировать изображение в base64"""
        # Проверяем и оптимизируем изображение
        img = Image.open(BytesIO(image_data))
        
        # Конвертируем в RGB если нужно
        if img.mode in ("RGBA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background
        
        # Сохраняем в bytes
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        img_bytes = buffered.getvalue()
        
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def analyze_image(self, image_data: bytes, filename: str = "image.jpg") -> Optional[ImageAnalysis]:
        """
        Анализ изображения
        
        Args:
            image_data: Байты изображения
            filename: Имя файла (для определения формата)
            
        Returns:
            ImageAnalysis или None при ошибке
        """
        try:
            base64_image = self._image_to_base64(image_data)
            
            prompt = """Проанализируй это изображение с точки зрения маркетинга и визуального стиля конкурента в сфере авторского надзора за строительством объектов в Республике Беларусь.

Изображение может содержать:
- Фотографии строительных объектов, процессов строительства
- Проектную документацию, чертежи, схемы
- Рекламные материалы, баннеры, презентации
- Инфографику о строительных услугах

Верни JSON объект со следующей структурой:
{
    "description": "детальное описание изображения с акцентом на строительную специфику",
    "marketing_insights": ["инсайт 1", "инсайт 2"],
    "visual_style_score": 7,
    "visual_style_analysis": "детальный анализ визуального стиля презентации услуг",
    "design_score": 8,
    "animation_potential": "описание потенциала для создания анимации, 3D-визуализации, интерактивных презентаций строительных процессов или проектов",
    "recommendations": ["рекомендация 1", "рекомендация 2"]
}

Критерии оценки:
- visual_style_score (0-10): Общая привлекательность и профессиональность визуального стиля
- design_score (0-10): Качество архитектурного/дизайнерского решения, если изображение содержит проектные решения или визуализации объектов
- animation_potential: Оцени, можно ли использовать изображение/концепцию для создания анимации (строительные процессы, эволюция проекта, интерактивные презентации)

Важно:
- Все оценки это числа от 0 до 10
- animation_potential - это текстовая оценка потенциала
- Верни ТОЛЬКО валидный JSON, без дополнительного текста"""

            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт по визуальному анализу в сфере строительства и архитектуры. Специализируешься на оценке строительных проектов, рекламных материалов строительных компаний и авторского надзора в Республике Беларусь. Умеешь оценивать потенциал материалов для создания анимаций и визуализаций."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Извлекаем JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            analysis_data = json.loads(content)
            
            return ImageAnalysis(**analysis_data)
            
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON от OpenAI: {e}")
            print(f"Полученный ответ: {content[:500]}")
            return None
        except Exception as e:
            print(f"Ошибка при анализе изображения: {e}")
            return None


# Глобальный экземпляр (инициализируется только при наличии ключа)
try:
    openai_service = OpenAIService() if settings.openai_api_key else None
except Exception as e:
    print(f"Предупреждение: Не удалось инициализировать OpenAI сервис: {e}")
    openai_service = None


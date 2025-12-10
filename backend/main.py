"""
Главный модуль FastAPI приложения
Мониторинг конкурентов - MVP ассистент
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pathlib import Path
import uvicorn

from backend.config import settings
from backend.models.schemas import (
    TextAnalysisRequest,
    TextAnalysisResponse,
    ImageAnalysisResponse,
    ParseDemoRequest,
    ParseDemoResponse,
    ParsedContent,
    HistoryResponse
)
from backend.services.openai_service import openai_service
from backend.services.parser_service import parser_service
from backend.services.history_service import history_service


# Инициализация приложения
app = FastAPI(
    title="Мониторинг конкурентов",
    description="MVP ассистент для анализа конкурентов с поддержкой текста и изображений",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Эндпоинты ===

@app.get("/")
async def root():
    """Главная страница - отдаём фронтенд"""
    web_index = Path("web/index.html")
    if web_index.exists():
        return FileResponse(web_index)
    return {"message": "API работает. Используйте /docs для документации.", "web_ui": "/static/index.html"}


@app.get("/favicon.ico")
async def favicon():
    """Обработка favicon - возвращаем 204 No Content"""
    return Response(status_code=204)


@app.post("/analyze_text", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Анализ текста конкурента
    
    Принимает текст и возвращает структурированную аналитику:
    - Сильные стороны
    - Слабые стороны
    - Уникальные предложения
    - Рекомендации по улучшению стратегии
    """
    if not openai_service:
        return TextAnalysisResponse(
            success=False,
            error="OpenAI сервис не инициализирован. Проверьте OPENAI_API_KEY в .env файле"
        )
    
    try:
        analysis = openai_service.analyze_text(request.text)
        
        if not analysis:
            return TextAnalysisResponse(
                success=False,
                error="Не удалось проанализировать текст. Проверьте логи."
            )
        
        # Сохраняем в историю
        request_summary = request.text[:100] + "..." if len(request.text) > 100 else request.text
        response_summary = analysis.summary if analysis.summary else "Анализ выполнен"
        
        history_service.add_entry(
            request_type="text",
            request_summary=request_summary,
            response_summary=response_summary
        )
        
        return TextAnalysisResponse(
            success=True,
            analysis=analysis
        )
    except Exception as e:
        return TextAnalysisResponse(
            success=False,
            error=str(e)
        )


@app.post("/analyze_image", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Анализ изображения конкурента
    
    Принимает изображение (баннер, сайт, упаковка) и возвращает:
    - Описание изображения
    - Маркетинговые инсайты
    - Оценку визуального стиля
    - Рекомендации
    """
    if not openai_service:
        return ImageAnalysisResponse(
            success=False,
            error="OpenAI сервис не инициализирован. Проверьте OPENAI_API_KEY в .env файле"
        )
    
    # Проверяем тип файла
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        return ImageAnalysisResponse(
            success=False,
            error=f"Неподдерживаемый тип файла. Разрешены: {', '.join(allowed_types)}"
        )
    
    try:
        # Читаем изображение
        content = await file.read()
        
        # Анализируем
        analysis = openai_service.analyze_image(content, file.filename)
        
        if not analysis:
            return ImageAnalysisResponse(
                success=False,
                error="Не удалось проанализировать изображение. Проверьте логи."
            )
        
        # Сохраняем в историю
        request_summary = f"Изображение: {file.filename or 'uploaded_image'}"
        response_summary = analysis.description[:200] if analysis.description else "Анализ изображения выполнен"
        
        history_service.add_entry(
            request_type="image",
            request_summary=request_summary,
            response_summary=response_summary
        )
        
        return ImageAnalysisResponse(
            success=True,
            analysis=analysis
        )
    except Exception as e:
        return ImageAnalysisResponse(
            success=False,
            error=str(e)
        )


@app.post("/parse_demo", response_model=ParseDemoResponse)
async def parse_demo(request: ParseDemoRequest):
    """
    Парсинг и анализ сайта конкурента (демо)
    
    Принимает URL, извлекает:
    - Title страницы
    - H1 заголовок
    - Первый абзац
    
    И передаёт их модели для анализа
    """
    if not openai_service:
        return ParseDemoResponse(
            success=False,
            error="OpenAI сервис не инициализирован. Проверьте OPENAI_API_KEY в .env файле"
        )
    
    try:
        # Парсим страницу
        parsed_data = parser_service.parse_url(request.url)
        
        if parsed_data.get("error"):
            return ParseDemoResponse(
                success=False,
                error=parsed_data["error"]
            )
        
        # Формируем текст для анализа из извлеченных данных
        analysis_text_parts = []
        if parsed_data.get("title"):
            analysis_text_parts.append(f"Заголовок: {parsed_data['title']}")
        if parsed_data.get("h1"):
            analysis_text_parts.append(f"H1: {parsed_data['h1']}")
        if parsed_data.get("first_paragraph"):
            analysis_text_parts.append(f"Первый абзац: {parsed_data['first_paragraph']}")
        
        analysis_text = "\n".join(analysis_text_parts) if analysis_text_parts else "Контент не найден"
        
        # Анализируем извлечённый контент
        analysis = openai_service.analyze_text(analysis_text) if analysis_text_parts else None
        
        parsed_content = ParsedContent(
            url=parsed_data["url"],
            title=parsed_data.get("title"),
            h1=parsed_data.get("h1"),
            first_paragraph=parsed_data.get("first_paragraph"),
            analysis=analysis
        )
        
        # Сохраняем в историю
        request_summary = f"URL: {request.url}"
        response_summary = f"Title: {parsed_data.get('title', 'N/A')}"
        
        history_service.add_entry(
            request_type="parse",
            request_summary=request_summary,
            response_summary=response_summary
        )
        
        return ParseDemoResponse(
            success=True,
            data=parsed_content
        )
    except Exception as e:
        return ParseDemoResponse(
            success=False,
            error=str(e)
        )


@app.get("/history", response_model=HistoryResponse)
async def get_history():
    """
    Получить историю последних 10 запросов
    """
    items = history_service.get_history()
    return HistoryResponse(
        items=items,
        total=len(items)
    )


@app.delete("/history")
async def clear_history():
    """
    Очистить историю запросов
    """
    history_service.clear_history()
    return {"success": True, "message": "История очищена"}


@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {
        "status": "healthy",
        "service": "Competitor Monitor",
        "version": "1.0.0",
        "openai_configured": openai_service is not None
    }


# Статические файлы для фронтенда
web_dir = Path("web")
if web_dir.exists():
    app.mount("/static", StaticFiles(directory="web"), name="static")


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )


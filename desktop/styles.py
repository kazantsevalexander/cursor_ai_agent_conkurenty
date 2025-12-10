"""
Стили для PyQt6 приложения - тёмная тема с cyan акцентами
"""

DARK_THEME = """
/* === Основные стили === */
QMainWindow, QWidget {
    background-color: #0a0f1c;
    color: #f1f5f9;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

QPushButton {
    background-color: #06b6d4;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #22d3ee;
}

QPushButton:disabled {
    background-color: #1e293b;
    color: #64748b;
}

QLineEdit, QTextEdit {
    background-color: #0d1320;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 8px;
    color: #f1f5f9;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #06b6d4;
}

QListWidget {
    background-color: #111827;
    border: 1px solid #1e293b;
    border-radius: 8px;
}

QScrollBar:vertical {
    background-color: #111827;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}
"""


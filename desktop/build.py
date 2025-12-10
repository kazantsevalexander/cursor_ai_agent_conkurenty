"""
Скрипт сборки desktop-приложения в .exe
Использует PyInstaller для создания исполняемого файла
"""
import sys
import os
import shutil
import subprocess
from pathlib import Path

# Настройка кодировки для Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def build_exe():
    """Собрать .exe файл"""
    print("=" * 60)
    print("СБОРКА DESKTOP ПРИЛОЖЕНИЯ")
    print("=" * 60)
    
    # Текущая директория
    current_dir = Path(__file__).parent
    
    # Проверяем наличие PyInstaller
    print("\nПроверка PyInstaller...")
    try:
        import PyInstaller  # type: ignore
        print(f"   OK PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("   ERROR: PyInstaller не установлен")
        print("   Установка: pip install pyinstaller")
        sys.exit(1)
    
    # Проверяем наличие main.py
    main_file = current_dir / "main.py"
    if not main_file.exists():
        print(f"\nERROR: файл {main_file} не найден")
        print("   Убедитесь, что вы находитесь в папке desktop/")
        sys.exit(1)
    
    # Имя приложения
    app_name = "CompetitorMonitor"
    
    # Параметры PyInstaller
    pyinstaller_args = [
        "pyinstaller",
        "--name", app_name,
        "--onefile",           # Один .exe файл
        "--windowed",          # Без консоли
        "--noconfirm",         # Перезаписывать без подтверждения
        "--clean",             # Очистить кеш
        
        # Иконка (если есть)
        # "--icon", "icon.ico",
        
        # Добавляем файлы
        "--add-data", f"styles.py{os.pathsep}.",
        "--add-data", f"api_client.py{os.pathsep}.",
        
        # Скрытые импорты
        "--hidden-import", "PyQt6",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "requests",
        
        # Главный файл
        "main.py"
    ]
    
    print(f"\nЗапуск сборки: {app_name}.exe")
    print("-" * 60)
    
    # Запускаем PyInstaller
    result = subprocess.run(pyinstaller_args, cwd=current_dir)
    
    if result.returncode == 0:
        exe_path = current_dir / "dist" / f"{app_name}.exe"
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("\n" + "=" * 60)
            print("СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
            print("=" * 60)
            print(f"\nФайл: {exe_path}")
            print(f"Размер: {size_mb:.1f} MB")
            print("\nДля запуска:")
            print(f"   1. Запустите backend: cd .. && python run.py")
            print(f"   2. Запустите {app_name}.exe")
        else:
            print("\nERROR: .exe файл не найден")
    else:
        print("\nERROR: Ошибка сборки")
        sys.exit(1)


def clean():
    """Очистить артефакты сборки"""
    current_dir = Path(__file__).parent
    
    dirs_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = ["*.spec"]
    
    print("Очистка артефактов сборки...")
    
    for dir_name in dirs_to_remove:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Удалено: {dir_name}/")
    
    for pattern in files_to_remove:
        for file in current_dir.glob(pattern):
            file.unlink()
            print(f"   Удалено: {file.name}")
    
    print("Очистка завершена")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean()
    else:
        build_exe()


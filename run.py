"""
Упрощённый запуск бота
"""
import subprocess
import sys

if __name__ == "__main__":
    print("🎨 Interior Style Bot - запуск...")
    print("=" * 50)

    # Запускаем uvicorn
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ])
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import random
import os
from pathlib import Path

# Создаем необходимые директории
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
IMAGES_DIR = STATIC_DIR / "images"
TEMPLATES_DIR = BASE_DIR / "templates"

# Создаем папки, если их нет
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app = FastAPI(title="Interior Style Bot", description="AI-powered interior design consultant")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Шаблоны
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ============ МОДЕЛИ ДАННЫХ ============
class Answer(BaseModel):
    question_id: int
    answer_text: str
    style_scores: Dict[str, int]


# ============ БАЗА ВОПРОСОВ (расширенная с эмодзи) ============
QUESTIONS = [
    {
        "id": 1,
        "text": "🎯 Как вы хотите себя чувствовать в этом пространстве?",
        "answers": [
            {"text": "🧘 Спокойствие и умиротворение", "styles": {"japandi": 3, "minimal": 2, "scandi": 2}},
            {"text": "⚡ Энергия и вдохновение", "styles": {"loft": 3, "popart": 2, "midcentury": 1}},
            {"text": "💎 Роскошь и статус", "styles": {"artdeco": 3, "classic": 3}},
            {"text": "📐 Порядок и ясность", "styles": {"minimal": 3, "hitech": 2}},
            {"text": "🕯️ Уют и тепло", "styles": {"scandi": 3, "boho": 2, "japandi": 1}}
        ]
    },
    {
        "id": 2,
        "text": "🎨 Какая цветовая палитра вам ближе?",
        "answers": [
            {"text": "🌿 Природные, земляные тона", "styles": {"scandi": 2, "japandi": 3, "boho": 1}},
            {"text": "⚫ Монохром и контрасты", "styles": {"minimal": 2, "loft": 2, "hitech": 2}},
            {"text": "👑 Глубокие, драгоценные цвета", "styles": {"artdeco": 3, "classic": 2}},
            {"text": "☁️ Светлые, воздушные оттенки", "styles": {"scandi": 2, "minimal": 1, "japandi": 1}},
            {"text": "🎨 Яркие, смелые акценты", "styles": {"popart": 3, "loft": 1, "midcentury": 2}}
        ]
    },
    {
        "id": 3,
        "text": "🪵 Какие материалы вам приятнее?",
        "answers": [
            {"text": "🌳 Натуральное дерево, камень, лён", "styles": {"scandi": 2, "japandi": 3, "boho": 1}},
            {"text": "🏭 Бетон, кирпич, металл", "styles": {"loft": 3, "minimal": 1}},
            {"text": "💎 Мрамор, бархат, золото", "styles": {"artdeco": 3, "classic": 2}},
            {"text": "📱 Стекло, пластик, хром", "styles": {"hitech": 3, "minimal": 1}},
            {"text": "🎭 Смешанные, эклектичные", "styles": {"boho": 2, "midcentury": 2, "popart": 1}}
        ]
    },
    {
        "id": 4,
        "text": "🖼️ Как вы относитесь к декору и деталям?",
        "answers": [
            {"text": "🧹 Минимум вещей, только функционал", "styles": {"minimal": 3, "hitech": 2}},
            {"text": "☕ Люблю уютные мелочи", "styles": {"scandi": 2, "boho": 2, "japandi": 1}},
            {"text": "🏺 Коллекционные, статусные предметы", "styles": {"classic": 2, "artdeco": 2}},
            {"text": "🎨 Арт-объекты, необычные вещи", "styles": {"popart": 2, "loft": 1, "midcentury": 2}}
        ]
    },
    {
        "id": 5,
        "text": "📐 Какая геометрия мебели вам ближе?",
        "answers": [
            {"text": "📏 Чёткие линии, простота", "styles": {"minimal": 2, "hitech": 2, "scandi": 1}},
            {"text": "🌀 Плавные, органичные формы", "styles": {"japandi": 2, "midcentury": 2, "boho": 1}},
            {"text": "🏛️ Симметрия, классика", "styles": {"classic": 3, "artdeco": 1}},
            {"text": "🎪 Асимметрия, смелые решения", "styles": {"loft": 2, "popart": 2, "midcentury": 1}}
        ]
    }
]

# ============ РАСШИРЕННЫЕ ОПИСАНИЯ СТИЛЕЙ ============
STYLE_DESCRIPTIONS = {
    "japandi": {
        "name": "Japandi",
        "full_name": "Японско-скандинавский минимализм",
        "description": "Гармония простоты, натуральных материалов и уюта. Вдохновение из японской эстетики wabi-sabi и скандинавского hygge. Это стиль для тех, кто ценит тишину, природу и качество.",
        "colors": ["Бежевый", "Природный дуб", "Глина", "Тёмно-зелёный", "Серый камень"],
        "materials": ["Дерево", "Лён", "Бамбук", "Глина", "Рисовая бумага"],
        "shopping_list": [
            "Низкий деревянный стол",
            "Льняные шторы",
            "Керамическая посуда ручной работы",
            "Бумажный светильник",
            "Бонсай или икебана"
        ],
        "avoid": ["Пластик", "Яркие кислотные цвета", "Излишний декор", "Хромированные поверхности"],
        "image": "https://images.unsplash.com/photo-1616486338812-3eadae5b9c1c?w=600&h=400&fit=crop"
    },
    "scandi": {
        "name": "Scandi",
        "full_name": "Скандинавский стиль",
        "description": "Свет, воздух, функциональность. Уютный минимализм с акцентом на текстиль и природные материалы. Создаёт ощущение лёгкости и спокойствия.",
        "colors": ["Белый", "Светло-серый", "Пастельные тона", "Пыльный розовый", "Мятный"],
        "materials": ["Светлое дерево", "Шерсть", "Хлопок", "Керамика", "Стекло"],
        "shopping_list": [
            "Пушистый плед из овечьей шерсти",
            "Деревянный торшер на треноге",
            "Плетёная корзина для хранения",
            "Живые растения в кашпо",
            "Белый диван простой формы"
        ],
        "avoid": ["Тёмные тона", "Массивная тёмная мебель", "Агрессивные узоры", "Бархат"],
        "image": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=600&h=400&fit=crop"
    },
    "minimal": {
        "name": "Minimal",
        "full_name": "Минимализм",
        "description": "Меньше — значит больше. Аскетичность, чистые линии и максимальная функциональность. Интерьер, в котором ничего не отвлекает от главного.",
        "colors": ["Белый", "Чёрный", "Серый", "Бежевый", "Песочный"],
        "materials": ["Бетон", "Стекло", "Металл", "Натуральный камень", "Матовые поверхности"],
        "shopping_list": [
            "Системы хранения без ручек",
            "Монохромный диван",
            "Геометрические светильники",
            "Зеркало в простой раме",
            "Пуф-пуфик"
        ],
        "avoid": ["Декор без функции", "Пёстрые обои", "Много текстиля", "Сувениры на полках"],
        "image": "https://images.unsplash.com/photo-1616486029423-aaa4789e8c9a?w=600&h=400&fit=crop"
    },
    "loft": {
        "name": "Loft",
        "full_name": "Индустриальный стиль",
        "description": "Свобода, брутальность и творческий хаос. Открытые коммуникации, кирпичные стены и металл. Рождался в заброшенных фабриках Нью-Йорка.",
        "colors": ["Серый", "Чёрный", "Кирпичный", "Тёмно-синий", "Ржавый"],
        "materials": ["Кирпич", "Бетон", "Металл", "Состаренное дерево", "Кожа"],
        "shopping_list": [
            "Металлические стеллажи на колёсиках",
            "Кожаное кресло в стиле mid-century",
            "Винтажная лампа на подвесах",
            "Постеры в чёрных рамках",
            "Грубый деревянный стол"
        ],
        "avoid": ["Позолота", "Рюши и кружева", "Классическая резная мебель", "Ковры с длинным ворсом"],
        "image": "https://images.unsplash.com/photo-1572120360610-d971b9d7767c?w=600&h=400&fit=crop"
    },
    "artdeco": {
        "name": "Art Deco",
        "full_name": "Ар-Деко",
        "description": "Роскошь 20-х, геометрия, экзотика. Смелые формы и дорогие материалы. Символ успеха и хорошего вкуса.",
        "colors": ["Чёрный", "Золотой", "Изумрудный", "Бордовый", "Белый мрамор"],
        "materials": ["Мрамор", "Латунь", "Бархат", "Экзотическое дерево", "Хрусталь"],
        "shopping_list": [
            "Зеркало в лучах (солнечное зеркало)",
            "Бархатный диван насыщенного цвета",
            "Хрустальная люстра или светильник",
            "Латунные настольные лампы",
            "Геометрические принты"
        ],
        "avoid": ["Простота без намёка на роскошь", "Деревенские мотивы", "Бюджетные материалы-имитации"],
        "image": "https://images.unsplash.com/photo-1618220179428-22790b461013?w=600&h=400&fit=crop"
    },
    "classic": {
        "name": "Classic",
        "full_name": "Классический стиль",
        "description": "Элегантность, симметрия, благородство. Античные мотивы и дорогая отделка. Никогда не выходит из моды.",
        "colors": ["Бежевый", "Слоновая кость", "Золотой", "Тёмное дерево", "Бордовый"],
        "materials": ["Дуб", "Мрамор", "Шёлк", "Хрусталь", "Бронза"],
        "shopping_list": [
            "Классический диван с каретной стяжкой",
            "Массивный обеденный стол из дуба",
            "Люстра из хрусталя",
            "Картины в позолоченных рамах",
            "Антикварное зеркало в резной раме"
        ],
        "avoid": ["Минимализм и аскетизм", "Открытые коммуникации", "Пластик и современные материалы"],
        "image": "https://images.unsplash.com/photo-1616486081543-5a1731ba264c?w=600&h=400&fit=crop"
    },
    "hitech": {
        "name": "Hi-Tech",
        "full_name": "Хай-тек",
        "description": "Технологичность, футуризм, умный дом. Глянец, стекло и трансформация. Интерьер из будущего.",
        "colors": ["Белый", "Серебристый", "Чёрный", "Синий неон", "Серый металлик"],
        "materials": ["Пластик", "Стекло", "Хром", "Сенсорные поверхности", "Алюминий"],
        "shopping_list": [
            "Умная подсветка с пультом",
            "Робот-пылесос",
            "Стеклянный стол",
            "Сенсорные выключатели",
            "Скрытые системы хранения"
        ],
        "avoid": ["Натуральное дерево", "Винтаж и ретро", "Мягкие округлые формы", "Избыток текстиля"],
        "image": "https://images.unsplash.com/photo-1616486338812-3eadae5b9c1c?w=600&h=400&fit=crop"
    },
    "midcentury": {
        "name": "Mid-Century",
        "full_name": "Мид-сенчури модерн",
        "description": "Ретро-футуризм 50-60х. Органичные формы, яркие акценты и функциональность. Вдохновение эпохой космоса и оптимизма.",
        "colors": ["Оранжевый", "Бирюзовый", "Горчичный", "Тик", "Лаймовый"],
        "materials": ["Гнутая фанера", "Пластик", "Вельвет", "Латунь", "Стекловолокно"],
        "shopping_list": [
            "Кресло-яйцо или кресло-тюльпан",
            "Лампа-паук",
            "Винтажные постеры космической тематики",
            "Деревянный комод на тонких ножках",
            "Ковёр с абстрактным узором"
        ],
        "avoid": ["Тяжёлая резная классика", "Современный хай-тек", "Излишняя помпезность"],
        "image": "https://images.unsplash.com/photo-1616486338812-3eadae5b9c1c?w=600&h=400&fit=crop"
    },
    "boho": {
        "name": "Boho",
        "full_name": "Бохо-стиль",
        "description": "Свободный, эклектичный, творческий. Микс культур, текстур и цветов. Для свободных художников и путешественников.",
        "colors": ["Терракота", "Бирюза", "Горчица", "Фуксия", "Слоновая кость"],
        "materials": ["Макраме", "Ротанг", "Хлопок", "Керамика", "Бамбук"],
        "shopping_list": [
            "Подушки с кистями разных размеров",
            "Плетёное кресло-качалка",
            "Макраме-панно на стену",
            "Ковры с этническими узорами",
            "Комнатные растения в кашпо"
        ],
        "avoid": ["Холодный минимализм", "Строгие офисные линии", "Дорогой глянец и пластик"],
        "image": "https://images.unsplash.com/photo-1616486338812-3eadae5b9c1c?w=600&h=400&fit=crop"
    }
}


# ============ API ЭНДПОИНТЫ ============
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/questions")
async def get_questions():
    """Получить все вопросы"""
    return {"questions": QUESTIONS}


@app.post("/api/calculate")
async def calculate_style(answers: List[Answer]):
    """Рассчитать стиль на основе ответов"""
    scores = {style: 0 for style in STYLE_DESCRIPTIONS.keys()}

    for answer in answers:
        for style, points in answer.style_scores.items():
            if style in scores:
                scores[style] += points

    # Добавляем небольшую вариативность для естественности
    for style in scores:
        variation = random.uniform(0.95, 1.05)
        scores[style] = round(scores[style] * variation, 1)

    # Сортируем и берём топ-3
    sorted_styles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_styles = sorted_styles[:3]

    # Главный стиль
    main_style = top_styles[0][0]
    main_score = top_styles[0][1]

    # Второй стиль (если разница не более 30%)
    secondary_style = None
    if len(top_styles) > 1 and (top_styles[1][1] / main_score) > 0.7:
        secondary_style = top_styles[1][0]

    # Формируем результат
    result = {
        "main_style": STYLE_DESCRIPTIONS[main_style],
        "secondary_style": STYLE_DESCRIPTIONS[secondary_style] if secondary_style else None,
        "confidence": min(95, int((main_score / (main_score + top_styles[1][1])) * 100)) if len(top_styles) > 1 else 85,
        "all_scores": {style: {"name": STYLE_DESCRIPTIONS[style]["name"], "score": int(score)}
                       for style, score in sorted_styles[:5]}
    }

    return JSONResponse(content=result)


@app.get("/api/styles")
async def get_styles():
    """Получить все доступные стили"""
    return {"styles": STYLE_DESCRIPTIONS}


@app.get("/health")
async def health_check():
    """Проверка работоспособности"""
    return {"status": "healthy", "questions_count": len(QUESTIONS), "styles_count": len(STYLE_DESCRIPTIONS)}


# ============ ЗАПУСК ============
if __name__ == "__main__":
    import uvicorn

    # Создаем файл с настройками для правильного запуска
    print("🚀 Запуск Interior Style Bot...")
    print(f"📁 Статика: {STATIC_DIR}")
    print(f"📁 Шаблоны: {TEMPLATES_DIR}")
    print(f"🌐 Откройте: http://localhost:8000")
    print(f"🛑 Для остановки нажмите Ctrl+C\n")

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
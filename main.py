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


# ============ БАЗА ВОПРОСОВ ============
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

# ============ СТИЛИ ============
STYLE_DESCRIPTIONS = {
    "japandi": {
        "name": "Japandi",
        "full_name": "Японско-скандинавский минимализм",
        "description": "Гармония простоты, натуральных материалов и уюта. Вдохновение из японской эстетики wabi-sabi и скандинавского hygge.",
        "colors": ["Бежевый", "Природный дуб", "Глина", "Тёмно-зелёный"],
        "materials": ["Дерево", "Лён", "Бамбук", "Глина"],
        "shopping_list": [
            "Низкий деревянный стол",
            "Льняные шторы",
            "Керамическая посуда ручной работы",
            "Бумажный светильник"
        ],
        "avoid": ["Пластик", "Яркие цвета", "Излишний декор"],
        "image": "https://ru.pinterest.com/pin/1102959765012876940/"
    },
    "scandi": {
        "name": "Scandi",
        "full_name": "Скандинавский стиль",
        "description": "Свет, воздух, функциональность. Уютный минимализм с акцентом на текстиль и природные материалы.",
        "colors": ["Белый", "Светло-серый", "Пастельные тона", "Пыльный розовый"],
        "materials": ["Светлое дерево", "Шерсть", "Хлопок", "Керамика"],
        "shopping_list": [
            "Пушистый плед",
            "Деревянный торшер",
            "Плетёная корзина",
            "Живые растения"
        ],
        "avoid": ["Тёмные тона", "Массивная мебель", "Агрессивные узоры"],
        "image": "https://ru.pinterest.com/pin/656610820718408460/"
    },
    "minimal": {
        "name": "Minimal",
        "full_name": "Минимализм",
        "description": "Меньше — значит больше. Аскетичность, чистые линии и максимальная функциональность.",
        "colors": ["Белый", "Чёрный", "Серый", "Бежевый"],
        "materials": ["Бетон", "Стекло", "Металл", "Натуральный камень"],
        "shopping_list": [
            "Системы хранения без ручек",
            "Монохромный диван",
            "Геометрические светильники",
            "Зеркало в простой раме"
        ],
        "avoid": ["Декор без функции", "Пёстрые обои", "Много текстиля"],
        "image": "https://ru.pinterest.com/pin/67131850692464196/"
    },
    "loft": {
        "name": "Loft",
        "full_name": "Индустриальный стиль",
        "description": "Свобода, брутальность и творческий хаос. Открытые коммуникации, кирпичные стены и металл.",
        "colors": ["Серый", "Чёрный", "Кирпичный", "Тёмно-синий"],
        "materials": ["Кирпич", "Бетон", "Металл", "Состаренное дерево"],
        "shopping_list": [
            "Металлические стеллажи",
            "Кожаное кресло",
            "Винтажная лампа на подвесах",
            "Постеры в чёрных рамках"
        ],
        "avoid": ["Позолота", "Рюши", "Классическая мебель"],
        "image": "https://ru.pinterest.com/pin/3025924746257553/"
    },
    "artdeco": {
        "name": "Art Deco",
        "full_name": "Ар-Деко",
        "description": "Роскошь 20-х, геометрия, экзотика. Смелые формы и дорогие материалы.",
        "colors": ["Чёрный", "Золотой", "Изумрудный", "Бордовый"],
        "materials": ["Мрамор", "Латунь", "Бархат", "Экзотическое дерево"],
        "shopping_list": [
            "Зеркало в лучах",
            "Бархатный диван",
            "Хрустальная люстра",
            "Латунные светильники"
        ],
        "avoid": ["Простота", "Деревенские мотивы", "Бюджетные материалы"],
        "image": "https://ru.pinterest.com/pin/1123859282032136762/"
    },
    "classic": {
        "name": "Classic",
        "full_name": "Классический стиль",
        "description": "Элегантность, симметрия, благородство. Античные мотивы и дорогая отделка.",
        "colors": ["Бежевый", "Слоновая кость", "Золотой", "Тёмное дерево"],
        "materials": ["Дуб", "Мрамор", "Шёлк", "Хрусталь"],
        "shopping_list": [
            "Классический диван с каретной стяжкой",
            "Массивный обеденный стол",
            "Люстра из хрусталя",
            "Картины в рамах"
        ],
        "avoid": ["Минимализм", "Открытые коммуникации", "Пластик"],
        "image": "https://yandex.ru/images/search?from=tabbar&img_url=https%3A%2F%2Fmir-s3-cdn-cf.behance.net%2Fproject_modules%2Fmax_3840_webp%2F5716b0119659483.60a2927a81f28.jpg&lr=44&pos=7&rpt=simage&text=Classic%20interior"
    },
    "hitech": {
        "name": "Hi-Tech",
        "full_name": "Хай-тек",
        "description": "Технологичность, футуризм, умный дом. Глянец, стекло и трансформация.",
        "colors": ["Белый", "Серебристый", "Чёрный", "Синий неон"],
        "materials": ["Пластик", "Стекло", "Хром", "Сенсорные поверхности"],
        "shopping_list": [
            "Умная подсветка",
            "Робот-пылесос",
            "Стеклянный стол",
            "Сенсорные выключатели"
        ],
        "avoid": ["Дерево", "Винтаж", "Мягкие формы"],
        "image": "https://ru.pinterest.com/pin/3166662233611918/"
    },
    "midcentury": {
        "name": "Mid-Century",
        "full_name": "Мид-сенчури модерн",
        "description": "Ретро-футуризм 50-60х. Органичные формы, яркие акценты и функциональность.",
        "colors": ["Оранжевый", "Бирюзовый", "Горчичный", "Тик"],
        "materials": ["Гнутая фанера", "Пластик", "Вельвет", "Латунь"],
        "shopping_list": [
            "Кресло-яйцо",
            "Лампа-паук",
            "Винтажные постеры",
            "Деревянный комод на ножках"
        ],
        "avoid": ["Классика", "Хай-тек", "Излишняя роскошь"],
        "image": "https://ru.pinterest.com/pin/1123859282032460084/"
    },
    "boho": {
        "name": "Boho",
        "full_name": "Бохо-стиль",
        "description": "Свободный, эклектичный, творческий. Микс культур, текстур и цветов.",
        "colors": ["Терракота", "Бирюза", "Горчица", "Фуксия"],
        "materials": ["Макраме", "Ротанг", "Хлопок", "Керамика"],
        "shopping_list": [
            "Подушки с кистями",
            "Плетёное кресло-качалка",
            "Макраме-панно",
            "Ковры с узорами"
        ],
        "avoid": ["Минимализм", "Строгие линии", "Дорогой глянец"],
        "image": "https://ru.pinterest.com/pin/6333255724030513/"
    }
}


# ============ API ============
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
    """Рассчитать стиль"""
    scores = {style: 0 for style in STYLE_DESCRIPTIONS.keys()}

    for answer in answers:
        for style, points in answer.style_scores.items():
            if style in scores:
                scores[style] += points

    # Вариативность
    for style in scores:
        variation = random.uniform(0.95, 1.05)
        scores[style] = round(scores[style] * variation, 1)

    sorted_styles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_styles = sorted_styles[:3]

    main_style = top_styles[0][0]
    main_score = top_styles[0][1]

    secondary_style = None
    if len(top_styles) > 1 and (top_styles[1][1] / main_score) > 0.7:
        secondary_style = top_styles[1][0]

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
    """Получить все стили"""
    return {"styles": STYLE_DESCRIPTIONS}


@app.get("/health")
async def health_check():
    """Проверка здоровья"""
    return {"status": "healthy", "questions": len(QUESTIONS), "styles": len(STYLE_DESCRIPTIONS)}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
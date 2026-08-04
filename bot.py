import os
import asyncio
from fastapi import FastAPI, Request, Response
import uvicorn

# Импорт твоей логики (обработчики)
from maxbot import Bot, Dispatcher, types

app = FastAPI()

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в переменных окружения")

SECRET = os.getenv("SECRET_KEY", "my-secret-key-256")  # лучше тоже вынести в env

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --- Твои обработчики (без изменений) ---
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    """Приветствие и объяснение миссии проекта."""
    text = (
        "👋 Здравствуйте! Наш научно-исследовательский проект посвящён изучению "
        "**воздействия электромагнитного излучения на рекомбинаторику нейронных связей**, "
        "раскрытию секретов аномальной памяти и нестандартных моделей мышления.\n\n"
        "Мы опираемся на труды выдающихся учёных:\n"
        "▫️ *Наталья Петровна Бехтерева* – нейрофизиолог, академик, исследовавшая механизмы памяти, "
        "творчества и «ошибок» мозга;\n"
        "▫️ *Александр Романович Лурия* – автор классической работы «Маленькая книжка о большой памяти», "
        "основоположник нейропсихологии.\n\n"
        "Для продолжения экспериментов нам необходимо приобретать/арендовать оборудование "
        "и привлекать профильных специалистов.\n\n"
        "Вы можете поддержать нас **добровольным пожертвованием** – любая сумма приближает открытия.\n"
        "Узнать подробнее: /donate\n"
        "О проекте: /about"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(commands=["about"])
async def cmd_about(message: types.Message):
    """Краткая научная справка."""
    text = (
        "🔬 **Научная база**\n\n"
        "Фундаментальные исследования Н.П. Бехтеревой показали, что определённые электрические "
        "и магнитные воздействия способны модулировать активность нейронных ансамблей, "
        "ответственных за долговременную память и инсайт.\n"
        "Работы А.Р. Лурии, в частности изучение феномена «абсолютной памяти» С.В. Шерешевского, "
        "демонстрируют, насколько пластичен и неисследован человеческий мозг.\n"
        "Наш проект развивает эти направления, применяя контролируемое электромагнитное излучение "
        "для мягкой стимуляции рекомбинации связей между нейронами.\n\n"
        "Цель – лучше понять природу уникальной памяти и нестандартного мышления, "
        "а в перспективе – помочь людям с когнитивными нарушениями."
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(commands=["donate"])
async def cmd_donate(message: types.Message):
    """Информация о добровольных пожертвованиях."""
    text = (
        "💙 **Сделать добровольное пожертвование**\n\n"
        "Ваши средства пойдут строго на:\n"
        "• аренду/покупку генераторов ЭМ-полей и экранированных камер;\n"
        "• оплату работы технических специалистов и научных консультантов;\n"
        "• лицензии на программное обеспечение для анализа нейроданных.\n\n"
        "🔹 **Реквизиты для перевода:**\n"
        "Банк: [Название банка]\n"
        "Получатель: [MIKHAIL ANDREYEV]\n"
        "Карта Сбер: 2202 2080 4614 8079\n"
        "Назначение: «Добровольное пожертвование на уставную деятельность»\n\n"
        "Или воспользуйтесь кнопкой ниже для быстрого перевода через СБП:"
    )
    
    # Кнопка-ссылка (замените URL на вашу платёжную форму / СБП / благотворительный сервис)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text="Перевести через СБП",
            url="https://pay.cloudtips.ru/p/d2a28dfa"
        )
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    await message.answer(
        "Доступные команды:\n"
        "/start – главное меню\n"
        "/about – о научной основе\n"
        "/donate – добровольное пожертвование\n"
        "/help – эта справка"
    )

@dp.message_handler(content_types=["text"])
async def handle_any_text(message: types.Message):
    await message.answer(
        "Пожалуйста, воспользуйтесь командами /start или /donate. "
        "Если у вас есть вопросы, напишите на почту anna.tan2000@yandex.ru"
    )
# -----------------------------------------

@app.post("/webhook")
async def handle_webhook(request: Request):
    # Проверка секретного ключа от MAX
    header_secret = request.headers.get("X-Max-Bot-Api-Secret")
    if header_secret != SECRET:
        return Response(status_code=403)

    body = await request.json()
    # Здесь нужно передать тело запроса в диспетчер dp
    # Это зависит от того, как библиотека maxbot умеет принимать «сырые» события.
    # Если она не умеет, придётся парсить JSON и вручную вызывать нужную логику.

    # Вариант 1 (если maxbot поддерживает обработку сырого события):
    # await dp.feed_update(body)

    # Вариант 2 (если нет — самый надёжный): разобрать JSON и вызвать нужный хендлер вручную.
    # Ниже — примерная структура, которую нужно адаптировать под формат событий MAX.
    event_type = body.get("event_type")
    message = body.get("message")

    if event_type == "message_created" and message:
        # Создаём объект Message, совместимый с типами maxbot
        msg = types.Message(
            id=message["id"],
            chat=message["chat"],
            from_user=message["from"],
            text=message.get("text", ""),
            # остальные поля по необходимости
        )
        # Пробрасываем в диспетчер
        await dp.process_update(msg)

    return Response(status_code=200)

if __name__ == "__main__":
    # Запускаем FastAPI как HTTP‑сервер
    uvicorn.run(app, host="https://nsk7.bothost.ru/api/webhooks/github?token=af188319873cfd8c2588d02a922a37ef586e582e1fb737a1", port=int(os.getenv("PORT", 443)))
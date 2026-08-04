import os
import asyncio
from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SECRET = os.getenv("SECRET_KEY", "my-secret-key-256")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в переменных окружения")

MAX_API_BASE = "https://platform-api.max.ru"

async def send_message(chat_id: str, text: str, reply_markup=None, parse_mode: str = None):
    """Отправка сообщения через API MAX"""
    url = f"{MAX_API_BASE}/messages"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if parse_mode:
        payload["parse_mode"] = parse_mode

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {BOT_TOKEN}"},
            timeout=10.0,
        )
        # Можно логировать resp.status_code и resp.text() для отладки
        return resp

@app.post("/webhook")
async def handle_webhook(request: Request):
    # Проверка секретного ключа
    header_secret = request.headers.get("X-Max-Bot-Api-Secret")
    if header_secret != SECRET:
        return Response(status_code=403)

    body = await request.json()
    event_type = body.get("event_type")
    message = body.get("message")

    if event_type == "message_created" and message:
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        from_user = message.get("from", {})

        # Простая логика: если текст — команда, отвечаем соответствующим текстом
        if text == "/start":
            reply = (
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
            await send_message(chat_id, reply, parse_mode="Markdown")

        elif text == "/about":
            reply = (
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
            await send_message(chat_id, reply, parse_mode="Markdown")

        elif text == "/donate":
            # Кнопка-ссылка
            keyboard = {
                "inline_keyboard": [
                    [
                        {
                            "text": "Перевести через CloudTips",
                            "url": "https://pay.cloudtips.ru/p/d2a28dfa"
                        }
                    ]
                ]
            }
            reply = (
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
            await send_message(chat_id, reply, reply_markup=keyboard, parse_mode="Markdown")

        elif text == "/help":
            reply = (
                "Доступные команды:\n"
                "/start – главное меню\n"
                "/about – о научной основе\n"
                "/donate – добровольное пожертвование\n"
                "/help – эта справка"
            )
            await send_message(chat_id, reply)

        else:
            # На любой другой текст
            reply = (
                "Пожалуйста, воспользуйтесь командами /start или /donate. "
                "Если у вас есть вопросы, напишите на почту anna.tan2000@yandex.ru"
            )
            await send_message(chat_id, reply)

    return Response(status_code=200)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 443))
    uvicorn.run(app, host="https://anna.tan2000.bothost.ru/webhooks", port=port)
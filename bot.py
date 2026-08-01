import asyncio
import logging
from maxapi import Bot, Dispatcher, F
from maxapi.filters.command import Command, CommandStart
from maxapi.fsm import State, StatesGroup, MemoryContext
from maxapi.types import Message, BotStarted

logging.basicConfig(level=logging.INFO)
bot = Bot(token="YOUR_BOT_TOKEN")  # Получи у Master Bot
dp = Dispatcher(context=MemoryContext())

class Donation(StatesGroup):
    name = State()
    amount = State()

@dp.bot_started()
async def on_start(event: BotStarted):
    await bot.send_message(event.chat_id, "Привет! Я бот для сбора пожертвований. Напиши /donate")

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для сбора пожертвований. Напиши /donate")

@dp.message(Command("donate"))
async def cmd_donate(message: Message, state):
    await state.set_state(Donation.name)
    await message.answer("Как я могу к тебе обращаться?")

@dp.message(Donation.name)
async def process_name(message: Message, state):
    if not message.text:
        await message.answer("Пожалуйста, напиши имя текстом.")
        return
    await state.update_data(name=message.text)
    await state.set_state(Donation.amount)
    await message.answer(f"Отлично, {message.text}! Какую сумму хочешь пожертвовать?")

@dp.message(Donation.amount, F.text.regexp(r"^\d+$"))
async def process_amount(message: Message, state):
    data = await state.get_data()
    await state.clear()
    await message.answer(
        f"Спасибо, {data['name']}! Ты хочешь пожертвовать {message.text} ₽.\n"
        "Перевод на карту: 1234 5678 9012 3456"
    )

@dp.message(Donation.amount)
async def invalid_amount(message: Message):
    await message.answer("Введи сумму числом, например: 500")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
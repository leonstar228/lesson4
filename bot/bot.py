import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "8254934023:AAGgxupNEJjpQ5rcGx3vVPbqYuRVfjWWWiY"
API_URL = "http://127.0.0.1:8000"

bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AddTask(StatesGroup):
    waiting_title = State()

@dp.message(Command("start"))
async def start(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Додати")],
            [types.KeyboardButton(text="📋 Список")]
        ],
        resize_keyboard=True
    )
    await msg.answer("Меню:", reply_markup=kb)

@dp.message(F.text == "➕ Додати")
async def add_task(msg: types.Message, state: FSMContext):
    await msg.answer("Введіть текст задачі:")
    await state.set_state(AddTask.waiting_title)

@dp.message(AddTask.waiting_title)
async def save_task(msg: types.Message, state: FSMContext):
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(f"{API_URL}/tasks", json={"title": msg.text})
        await msg.answer("✅ Задачу додано")
        await state.clear()
    except:
        await msg.answer("❌ Помилка додавання")

@dp.message(F.text == "📋 Список")
async def list_tasks(msg: types.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/tasks") as resp:
                tasks = await resp.json()

        if not tasks:
            await msg.answer("Список пустий")
            return

        status_emoji = {"todo": "⏳", "done": "✅"}

        for t in tasks:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✔", callback_data=f"done_{t['id']}"),
                    InlineKeyboardButton(text="🗑", callback_data=f"del_{t['id']}")
                ]
            ])
            emoji = status_emoji.get(t["status"], "❓")
            await msg.answer(f"{t['id']}. {t['title']} {emoji}", reply_markup=kb)

    except:
        await msg.answer("❌ Помилка отримання")

@dp.callback_query(F.data.startswith("done_"))
async def done_task(cb: types.CallbackQuery):
    task_id = cb.data.split("_")[1]
    async with aiohttp.ClientSession() as session:
        await session.patch(f"{API_URL}/tasks/{task_id}", json={"status": "done"})
    await cb.message.edit_text("✅ Виконано")
    await cb.answer()

@dp.callback_query(F.data.startswith("del_"))
async def delete_task(cb: types.CallbackQuery):
    task_id = cb.data.split("_")[1]
    async with aiohttp.ClientSession() as session:
        await session.delete(f"{API_URL}/tasks/{task_id}")
    await cb.message.edit_text("🗑 Видалено")
    await cb.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
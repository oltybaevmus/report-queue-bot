from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram import F
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

queue = []  # простая очередь в памяти

def get_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟩 Встать в очередь", callback_data="join")],
        [InlineKeyboardButton(text="⬜ Покинуть очередь", callback_data="leave")],
        [InlineKeyboardButton(text="🔹 Список очереди", callback_data="list")],
        [InlineKeyboardButton(text="🚫 Передумал", callback_data="cancel")]
    ])

def queue_text():
    if not queue:
        return "Очередь пуста 🕊"
    text = "📋 Текущая очередь:\n"
    for i, user in enumerate(queue, start=1):
        text += f"{i}. {user.mention_html()}\n"
    return text

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! 👋 Я помогу вести очередь по отчетам.", reply_markup=get_keyboard())

@dp.callback_query(F.data == "join")
async def join_queue(callback: types.CallbackQuery):
    user = callback.from_user
    if user in queue:
        await callback.answer("Ты уже в очереди 😉", show_alert=True)
        return
    queue.append(user)
    await callback.message.answer(f"{user.mention_html()} встал(а) в очередь!", parse_mode="HTML")
    await callback.message.answer(queue_text(), parse_mode="HTML", reply_markup=get_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "leave")
async def leave_queue(callback: types.CallbackQuery):
    user = callback.from_user
    if user not in queue:
        await callback.answer("Ты не в очереди 🤷", show_alert=True)
        return
    queue.remove(user)
    next_user = queue[0] if queue else None
    msg = f"{user.mention_html()} покинул(а) очередь."
    if next_user:
        msg += f"\nСледующий: {next_user.mention_html()}!"
    await callback.message.answer(msg, parse_mode="HTML")
    await callback.message.answer(queue_text(), parse_mode="HTML", reply_markup=get_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "cancel")
async def cancel_queue(callback: types.CallbackQuery):
    user = callback.from_user
    if user in queue:
        queue.remove(user)
        await callback.message.answer(f"{user.mention_html()} передумал(а).", parse_mode="HTML")
    await callback.message.answer(queue_text(), parse_mode="HTML", reply_markup=get_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "list")
async def show_list(callback: types.CallbackQuery):
    await callback.message.answer(queue_text(), parse_mode="HTML", reply_markup=get_keyboard())
    await callback.answer()

async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

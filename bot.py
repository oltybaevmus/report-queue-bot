from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram import F
import asyncio
import os

# === 🔍 ОТЛАДКА ПЕРЕМЕННОЙ ОКРУЖЕНИЯ ===
print("=== DEBUG INFO START ===")
print("All environment variables (filtered):")
for key, value in os.environ.items():
    if "TOKEN" in key or "RAILWAY" in key:
        print(f"{key} = {value}")
print("===")

# Чтение токена
TOKEN = os.getenv("BOT_TOKEN")
print(f"DEBUG: BOT_TOKEN from os.getenv = {repr(TOKEN)}")

if not TOKEN:
    # Если токен не найден — выводим понятное сообщение
    raise ValueError("❌ BOT_TOKEN не найден! Проверь, что переменная окружения задана в Railway и сервис использует её.")

# === ИНИЦИАЛИЗАЦИЯ БОТА ===
bot = Bot(token=TOKEN)
dp = Dispatcher()

queue = []  # простая очередь в памяти

# === КЛАВИАТУРА ===
def get_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟩 Встать в очередь", callback_data="join")],
        [InlineKeyboardButton(text="⬜ Покинуть очередь", callback_data="leave")],
        [InlineKeyboardButton(text="🔹 Список очереди", callback_data="list")],
        [InlineKeyboardButton(text="🚫 Передумал", callback_data="cancel")]
    ])

# === ТЕКСТ ОЧЕРЕДИ ===
def queue_text():
    if not queue:
        return "Очередь пуста 🕊"
    text = "📋 Текущая очередь:\n"
    for i, user in enumerate(queue, start=1):
        text += f"{i}. {user.mention_html()}\n"
    return text

# === КОМАНДА /START ===
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! 👋 Я помогу вести очередь по отчетам.", reply_markup=get_keyboard())

# === CALLBACK HANDLERS ===
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

# === MAIN ===
async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

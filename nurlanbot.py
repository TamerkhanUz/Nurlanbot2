import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton
from keep_alive import keep_alive

keep_alive()

API_TOKEN = '8486401103:AAGHrZKqnXlEGPh2xRZSDqCdoGS63tAn8ZA'  # Бу ерга ўз бот токенингизни қўйинг
CHANNEL_ID = -1001513266536       # Бу ерга канал ID қўйинг

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_data = {}

next_step_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Кейингисига ўтиш", callback_data="next_step")]
])

ready_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Тайёр", callback_data="ready")]
])

restart_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    user_data[message.from_user.id] = {
        "photos": [],
        "description": None,
        "price": None,
    }
    await message.answer(
        "Салом! Илтимос 1 дан 8 тасигача фотоларни юборинг.\n"
        "Ҳар бир фотодан сўнг «Кейингисига ўтиш» тугмасини босишингиз мумкин.",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message(lambda m: m.photo)
async def handle_photos(message: types.Message):
    data = user_data.get(message.from_user.id)
    if data is None:
        await message.answer("Илтимос /start буйруғини киритинг.")
        return

    if len(data["photos"]) >= 8:
        await message.answer("Максимум 8 та фото қабул қилинади. Энди фотоларни юборишни тугатиш учун «Кейингисига ўтиш» тугмасини босинг.")
        return

    data["photos"].append(message.photo[-1].file_id)
    await message.answer(f"Фото қабул қилинди. Ҳозирда {len(data['photos'])} та фото бор.", reply_markup=next_step_kb)

@dp.callback_query(lambda c: c.data == "next_step")
async def next_step_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = user_data.get(user_id)

    if not data or len(data["photos"]) == 0:
        await callback.message.answer("Илтимос, камида 1 та фото юборинг.")
        await callback.answer()
        return

    await callback.message.answer("Илтимос, эълон матнини (📝 Матн) киритинг.")
    await callback.answer()

@dp.message(lambda m: not m.photo and user_data.get(m.from_user.id) and user_data[m.from_user.id]["description"] is None)
async def handle_description(message: types.Message):
    data = user_data[message.from_user.id]
    data["description"] = message.text
    await message.answer("Нархни (💰 Цена:) киритинг.")

@dp.message(lambda m: not m.photo and user_data.get(m.from_user.id) and user_data[m.from_user.id]["description"] is not None and user_data[m.from_user.id]["price"] is None)
async def handle_price(message: types.Message):
    data = user_data[message.from_user.id]
    data["price"] = message.text
    await message.answer("Маълумотлар сақланди. Эълонни каналга жўнатиш учун «Тайёр» тугмасини босинг.", reply_markup=ready_kb)

@dp.callback_query(lambda c: c.data == "ready")
async def send_ad_to_channel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = user_data.get(user_id)

    if not data:
        await callback.message.answer("Илтимос /start буйруғини киритинг.")
        await callback.answer()
        return

    media = [InputMediaPhoto(media=photo_id) for photo_id in data["photos"]]

    caption = (
        f"1) 📝 {data['description']}\n\n"
        f"2) 💰 Цена: {data['price']}\n\n"
        f"❗️Если у вас вопросы есть то:\n\n"
        f"3) ☎️ +998-(97)-757-13-53 Нурлан\n"
        f"4) 📍Мне напишите:  @Nurlan_mebel"
    )

    try:
        if len(media) == 1:
            await bot.send_photo(CHANNEL_ID, media[0].media, caption=caption)
        else:
            media[0].caption = caption
            await bot.send_media_group(CHANNEL_ID, media)

        await callback.message.answer(
            "Эълон каналга жўнатилди!\n\nЯна бир эълон юбориш учун /start ни босинг.",
            reply_markup=restart_kb
        )

        user_data[user_id] = {
            "photos": [],
            "description": None,
            "price": None,
        }
    except Exception as e:
        await callback.message.answer(f"Хато юз берди: {e}")

    await callback.answer()

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
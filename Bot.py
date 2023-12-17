import asyncio
from aiogram import Bot, Dispatcher, types, F
from enum import Enum
import nest_asyncio
import google.generativeai as genai
from PIL import Image

# region AI
GOOGLE_API_KEY = 'AIzaSyBe_IriVABmCfYEo4h_bZC3JPwXDdqUw_A'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
c = model.start_chat(history=[])
webhook_endpoint = ''


def ask(prompt):
    response = model.generate_content(prompt)
    return response.text


def chat(prompt):
    response = c.send_message(prompt)
    return response.text


def ask_img(prompt, user_id):
    m = genai.GenerativeModel('gemini-pro-vision')
    img = Image.open(f'{user_id}.jpeg')
    response = m.generate_content([prompt, img])
    return response.text


def get_chat_history():
    res = ''
    for message in c.history:
        res += f'**{message.role}**: {message.parts[0].text} \n '

    if res == '':
        res = 'No history'

    return res
# endregion


class PromptType(Enum):
    regular = 1
    chat = 2
    image = 3


TOKEN = '6784222020:AAFolTH9gyiO_uKfWQU27Iz1hKdFs8Uegg4'
nest_asyncio.apply()
dp = Dispatcher()
bot = Bot(TOKEN)
prompt_type = PromptType.regular


@dp.message(F.text == '/history')
async def display_chat_history(message: types.Message) -> None:
    res = get_chat_history()
    await message.answer(res)


@dp.message(F.text == '/image')
async def switch_to_img(message: types.Message) -> None:
    global prompt_type
    prompt_type = PromptType.image


@dp.message(F.text == '/chat')
async def switch_to_chat(message: types.Message) -> None:
    global prompt_type
    prompt_type = PromptType.chat


@dp.message(F.text == '/regular')
async def switch_to_reg(message: types.Message) -> None:
    global prompt_type
    prompt_type = PromptType.regular


@dp.message(F.content_type == 'photo')
async def save_img(message: types.Message) -> None:
    global prompt_type
    if prompt_type == PromptType.image:
        try:
            file = message.photo[-1].file_id
            f = await bot.get_file(file)
            path = f.file_path
            await bot.download_file(path, f"{message.from_user.id}.jpeg")
        except Exception as e:
            await message.answer('Some error occurred. Try Again')
            print(e)


@dp.message()
async def handler(message: types.Message) -> None:
    global prompt_type
    try:
        answer = ''
        prompt = message.text
        if prompt_type == PromptType.regular:
            answer = ask(prompt)
        elif prompt_type == PromptType.chat:
            answer = chat(prompt)
        elif prompt_type == PromptType.image:
            answer = ask_img(prompt, message.from_user.id)
        await message.answer(answer)
    except Exception as e:
        await message.answer('Some error occurred. Try Again')
        print(e)


async def start_bot() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())

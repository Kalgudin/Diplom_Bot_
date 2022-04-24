from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = "files/expo.jpg"
FONT_PATH = "files/fonts/Roboto-Medium.ttf"
FONT_SIZE = 40
WHITE = (220, 220, 220, 255)
NAME_OFFSET = (650, 120)
EMAIL_OFFSET = (650, 200)
AVATAR_SIZE = 100
AVATAR_OFFSET = (120, 120)


def generate_ticket(name, email):
    # get an image
    with Image.open(TEMPLATE_PATH).convert("RGBA") as base:
        # get a font
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        # get a drawing context
        draw = ImageDraw.Draw(base)
        draw.text(NAME_OFFSET, name, font=font, fill=WHITE)
        draw.text(EMAIL_OFFSET, email, font=font, fill=WHITE)

        response = requests.get(url='https://cs6.pikabu.ru/avatars/404/x404070-828004264.png') # 'https://avatars.dicebear.com/api/bottts/Kalgudin@mail.svg'
        avatar_file_like = BytesIO(response.content)
        with Image.open(fp=avatar_file_like, mode="r") as avatar:
            base.paste(avatar, AVATAR_OFFSET)
        # with open('files/expo_ticket.png', 'wb') as output_file:
        #     base.save(output_file, 'png')
        temp_file = BytesIO()
        base.save(temp_file, 'png')
        temp_file.seek(0)  # переводим курсор в начала файла
        return temp_file


generate_ticket(name='Николай Калгудин', email='kalgudin@mail.ru')

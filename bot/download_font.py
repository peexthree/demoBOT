import urllib.request
import os

font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
os.makedirs(font_dir, exist_ok=True)

font_url = 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf'
bold_font_url = 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf'

urllib.request.urlretrieve(font_url, os.path.join(font_dir, 'Roboto-Regular.ttf'))
urllib.request.urlretrieve(bold_font_url, os.path.join(font_dir, 'Roboto-Bold.ttf'))
print("Шрифты скачаны успешно.")

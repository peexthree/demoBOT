import os
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

class PDFReportGenerator:
    def __init__(self, filename: str, title: str):
        self.filename = filename
        self.title = title
        self.width, self.height = A4
        self.c = canvas.Canvas(filename, pagesize=A4)

        self.font_regular = "Helvetica"
        self.font_bold = "Helvetica-Bold"

        # Подключаем кириллицу
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        reg_font_path = os.path.join(font_dir, 'Roboto-Regular.ttf')
        bold_font_path = os.path.join(font_dir, 'Roboto-Bold.ttf')

        try:
            if os.path.exists(reg_font_path) and os.path.exists(bold_font_path):
                pdfmetrics.registerFont(TTFont('Roboto-Regular', reg_font_path))
                pdfmetrics.registerFont(TTFont('Roboto-Bold', bold_font_path))
                self.font_regular = "Roboto-Regular"
                self.font_bold = "Roboto-Bold"
        except Exception as e:
            logging.warning(f"Ошибка загрузки TTF шрифтов: {e}")

        self.c.setFont(self.font_regular, 12)

    def _draw_watermark(self):
        self.c.saveState()
        self.c.setFont(self.font_bold, 50)
        # Полупрозрачный циановый цвет (rgb(102, 252, 241) / 255)
        self.c.setFillColorRGB(102/255, 252/255, 241/255, alpha=0.1)
        self.c.translate(self.width / 2, self.height / 2)
        self.c.rotate(45)
        self.c.drawCentredString(0, 0, "EIDOS MARKETING")
        self.c.restoreState()

    def add_title(self):
        self.c.setFont(self.font_bold, 24)
        self.c.drawCentredString(self.width / 2, self.height - 80, self.title)

    def add_content(self, content_lines: list[str]):
        y_position = self.height - 120
        self.c.setFont(self.font_regular, 12)
        line_height = 14
        margin_left = 50
        max_width = self.width - 100

        for line in content_lines:
            wrapped_lines = simpleSplit(line, self.font_regular, 12, max_width)
            for wrapped in wrapped_lines:
                if y_position < 50:
                    self.c.showPage()
                    self._draw_watermark()
                    y_position = self.height - 50
                    self.c.setFont(self.font_regular, 12)

                self.c.drawString(margin_left, y_position, wrapped)
                y_position -= line_height
            y_position -= line_height

    def generate(self, content_text: str):
        self._draw_watermark()
        self.add_title()

        lines = content_text.split('\n')
        self.add_content(lines)

        self.c.save()
        return self.filename

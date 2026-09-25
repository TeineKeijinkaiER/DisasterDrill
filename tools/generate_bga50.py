from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Disaster_BGA" / "21_No50_血液ガス.pdf"
FONT = "NotoSansJP"
FONT_PATH = ROOT / "assets" / "fonts" / "NotoSansJP-VF.ttf"

ROWS = [
    ("pH", "7.34", "7.35-7.45", True),
    ("pO2", "82 mmHg", "80-100", False),
    ("pCO2", "35 mmHg", "35-45", False),
    ("HCO3-", "19 mmol/L", "22-26", True),
    ("BE", "-6 mmol/L", "-2〜+2", True),
    ("Lac（乳酸）", "36.0 mg/dL", "4.5-14.4", True),
    ("Hb", "11.5 g/dL", "13-17", True),
    ("Na+", "140 mmol/L", "138-145", False),
    ("K+", "4.1 mmol/L", "3.6-4.8", False),
    ("Cl-", "105 mmol/L", "101-108", False),
    ("iCa2+", "1.10 mmol/L", "1.15-1.30", True),
    ("Glu", "135 mg/dL", "73-109", True),
]


def main() -> None:
    pdfmetrics.registerFont(TTFont(FONT, str(FONT_PATH)))
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    width, height = A4
    margin = 12 * mm
    table_width = width - 2 * margin
    col1 = 0.42 * table_width
    col2 = 0.34 * table_width
    col3 = table_width - col1 - col2

    navy = colors.HexColor("#2E3A4E")
    pale = colors.HexColor("#E9EFF3")
    border = colors.HexColor("#B8C6CE")
    muted = colors.HexColor("#7F909C")
    red = colors.HexColor("#C53B2F")
    pink = colors.HexColor("#FCE9E6")

    c.setTitle("症例 No.50 血液ガス分析")
    c.setAuthor("TeineKeijinkaiER")

    top = height - 24 * mm
    c.setFillColor(navy)
    c.roundRect(margin, top - 15 * mm, table_width, 15 * mm, 3 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(FONT, 20)
    c.drawString(margin + 5 * mm, top - 10.5 * mm, "症例 No.50")

    c.setFillColor(colors.black)
    c.setFont(FONT, 11)
    c.drawString(margin + 5 * mm, top - 23 * mm, "血液ガス分析（動脈血・室内気・圧迫止血後）")

    y = top - 32 * mm
    row_h = 9 * mm
    headers = (("項目", col1), ("結果", col2), ("基準値", col3))
    x = margin
    c.setFillColor(pale)
    c.rect(margin, y, table_width, row_h, fill=1, stroke=0)
    c.setStrokeColor(border)
    c.rect(margin, y, table_width, row_h, fill=0, stroke=1)
    c.setFillColor(colors.black)
    c.setFont(FONT, 8.8)
    for label, column_width in headers:
        c.drawString(x + 3 * mm, y + 3 * mm, label)
        x += column_width

    for label, value, normal, abnormal in ROWS:
        y -= row_h
        if abnormal:
            c.setFillColor(pink)
            c.rect(margin + col1, y, col2, row_h, fill=1, stroke=0)
        c.setStrokeColor(border)
        c.line(margin, y, margin + table_width, y)
        c.setFillColor(colors.black)
        c.setFont(FONT, 8.8)
        c.drawString(margin + 3 * mm, y + 3 * mm, label)
        c.setFillColor(red if abnormal else colors.black)
        c.drawString(margin + col1 + 3 * mm, y + 3 * mm, value)
        c.setFillColor(muted)
        c.drawString(margin + col1 + col2 + 3 * mm, y + 3 * mm, normal)

    c.setStrokeColor(border)
    c.rect(margin, y, table_width, row_h * (len(ROWS) + 1), fill=0, stroke=1)
    c.line(margin + col1, y, margin + col1, y + row_h * (len(ROWS) + 1))
    c.line(margin + col1 + col2, y, margin + col1 + col2, y + row_h * (len(ROWS) + 1))

    c.setFillColor(red)
    c.setFont(FONT, 8.2)
    c.drawString(margin, y - 11 * mm, "※右下腿開放骨折・持続出血および検体検査結果から作成した推定模擬値")
    c.setFillColor(muted)
    c.setFont(FONT, 7.5)
    c.drawString(margin, y - 20 * mm, "2026年度 手稲渓仁会病院 災害訓練／訓練用の模擬検査データ")
    c.save()


if __name__ == "__main__":
    main()

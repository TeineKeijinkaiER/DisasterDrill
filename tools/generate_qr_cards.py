from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "pdf"

REPOSITORY = "TeineKeijinkaiER/DisasterDrill"
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPOSITORY}/{BRANCH}"

CARD_WIDTH = 91 * mm
CARD_HEIGHT = 55 * mm
MARGIN_X = 14 * mm
MARGIN_TOP = 11 * mm

FONT_PATHS = (
    Path(r"C:\Windows\Fonts\NotoSansJP-VF.ttf"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
)
FONT_NAME = "NotoSansJP"

BLUE = HexColor("#17689B")
PALE_BLUE = HexColor("#EAF4FB")
TEXT = HexColor("#24313D")
MUTED = HexColor("#8798AA")
HAIRLINE = HexColor("#CFDCE8")


PATIENTS = {
    1: ("45歳", "サトウユキ"),
    2: ("52歳", "スズキユウキ"),
    3: ("38歳", "タカハシヒロミ"),
    13: ("13歳前後", "身元不明（ID未確認）"),
    14: ("31歳", "マツモトレイ"),
    19: ("69歳", "シミズカズミ"),
    21: ("78歳", "アベノア"),
    22: ("50歳", "モリアサヒ"),
    23: ("74歳", "イケダハルカ"),
    24: ("81歳", "ハシモトミドリ"),
    35: ("55歳", "エンドウミノル"),
    36: ("10歳", "タナカソラ"),
    38: ("76歳", "フジイカイ"),
    39: ("61歳", "ニシムラヨシミ"),
    40: ("36歳", "フクダリツ"),
    41: ("53歳", "オウタミオ"),
    45: ("67歳", "ナカガワチアキ"),
    46: ("57歳", "ナカノヤヨイ"),
    47: ("43歳", "ハラダアキラ"),
    48: ("13歳", "オノシノブ"),
    50: ("40歳", "タケウチハルキ"),
}


def register_fonts() -> None:
    global FONT_NAME
    for font_path in FONT_PATHS:
        if font_path.exists():
            pdfmetrics.registerFont(TTFont(FONT_NAME, str(font_path)))
            return
    FONT_NAME = "HeiseiKakuGo-W5"
    pdfmetrics.registerFont(UnicodeCIDFont(FONT_NAME))


def parse_id(path: Path) -> int:
    match = re.search(r"_No(\d+)_", path.name)
    if not match:
        raise ValueError(f"Could not determine ID from {path.name}")
    return int(match.group(1))


def target_url(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    return f"{RAW_BASE}/{quote(relative, safe='/')}"


def draw_qr(c: canvas.Canvas, url: str, x: float, y: float, size: float) -> None:
    qr = QrCodeWidget(url, barLevel="M")
    x1, y1, x2, y2 = qr.getBounds()
    width = x2 - x1
    height = y2 - y1
    drawing = Drawing(size, size, transform=[size / width, 0, 0, size / height, 0, 0])
    drawing.add(qr)
    renderPDF.draw(drawing, c, x, y)
    c.linkURL(url, (x, y, x + size, y + size), relative=0)


def draw_card(
    c: canvas.Canvas,
    x: float,
    y: float,
    patient_id: int,
    age: str,
    name: str,
    label: str,
    url: str,
) -> None:
    c.setFillColor(white)
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.35)
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=1)

    c.setFillColor(BLUE)
    c.rect(x, y + CARD_HEIGHT - 1.25 * mm, CARD_WIDTH, 1.25 * mm, fill=1, stroke=0)

    left = x + 4 * mm
    c.setFillColor(MUTED)
    c.setFont(FONT_NAME, 6.2)
    c.drawString(left, y + CARD_HEIGHT - 7.2 * mm, label)

    c.setFillColor(TEXT)
    c.setFont(FONT_NAME, 20)
    c.drawString(left, y + CARD_HEIGHT - 19.2 * mm, f"ID{patient_id:02d}")

    name_size = 10.2 if len(name) <= 10 else 8.8
    c.setFont(FONT_NAME, name_size)
    c.drawString(left, y + CARD_HEIGHT - 27.0 * mm, name)

    c.setFillColor(MUTED)
    c.setFont(FONT_NAME, 8.2)
    c.drawString(left, y + CARD_HEIGHT - 34.0 * mm, age)

    box_x = left
    box_y = y + 5.2 * mm
    box_w = 41.5 * mm
    box_h = 13.2 * mm
    c.setFillColor(PALE_BLUE)
    c.roundRect(box_x, box_y, box_w, box_h, 2.2 * mm, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont(FONT_NAME, 5.7)
    c.drawString(box_x + 2.1 * mm, box_y + 8.7 * mm, "画像")
    c.setFillColor(TEXT)
    c.setFont(FONT_NAME, 11.2)
    c.drawString(box_x + 2.1 * mm, box_y + 3.0 * mm, label)

    qr_size = 29.5 * mm
    qr_x = x + 54.0 * mm
    qr_y = y + 14.0 * mm
    draw_qr(c, url, qr_x, qr_y, qr_size)

    c.setFillColor(MUTED)
    c.setFont(FONT_NAME, 5.2)
    c.drawCentredString(qr_x + qr_size / 2, y + 6.0 * mm, "QRを読み取って画像を表示")


def build_pdf(source_dir: Path, label: str, output_path: Path) -> None:
    files = sorted(source_dir.glob("*.jpg"), key=lambda p: int(p.name.split("_", 1)[0]))
    if not files:
        raise RuntimeError(f"No JPEG files found in {source_dir}")

    c = canvas.Canvas(str(output_path), pagesize=A4, pageCompression=1)
    c.setTitle(f"災害訓練 {label} QRカード")
    c.setAuthor("TeineKeijinkaiER")
    c.setSubject("A4 名刺用紙 91mm x 55mm / 10面")

    page_width, page_height = A4
    for index, image_path in enumerate(files):
        position = index % 10
        if position == 0 and index:
            c.showPage()

        col = position % 2
        row = position // 2
        x = MARGIN_X + col * CARD_WIDTH
        y = page_height - MARGIN_TOP - (row + 1) * CARD_HEIGHT

        patient_id = parse_id(image_path)
        age, name = PATIENTS.get(patient_id, ("年齢未登録", "氏名未登録"))
        draw_card(c, x, y, patient_id, age, name, label, target_url(image_path))

    c.save()


def main() -> None:
    register_fonts()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_pdf(
        ROOT / "Disaster_lab",
        "LAB",
        OUTPUT_DIR / "Disaster_Lab_QR_cards_A4_10up.pdf",
    )
    build_pdf(
        ROOT / "Disaster_BGA",
        "BGA",
        OUTPUT_DIR / "Disaster_BGA_QR_cards_A4_10up.pdf",
    )


if __name__ == "__main__":
    main()

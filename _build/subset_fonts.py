# -*- coding: utf-8 -*-
"""重新產生字型子集

改過文案之後執行：掃描全站 HTML，把標題實際用到的字挑出來，
子集化 Noto Serif CJK TC 與 Nimbus Sans Narrow，輸出 woff2。

    cd _build && python3 subset_fonts.py
"""
import os, sys, glob
from html.parser import HTMLParser
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONT_DIR = os.path.join(ROOT, "assets", "font")

SERIF_SRC = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
SERIF_IDX = 3                      # ttc 內的 Noto Serif CJK TC
NUM_SRC_R = "/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Regular.otf"
NUM_SRC_B = "/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Bold.otf"

# 這些元素會套用襯線標題字（對應 CSS 的 --f-display）
DISPLAY_TAGS = {"h1", "h2", "h3", "h4", "h5", "summary"}
DISPLAY_CLASS = {"tag", "nm"}

# 預留字：日後改文案常會用到，先納入以免缺字
RESERVE = (
    "材料防水塗裝施工程序層底漆面主膜厚度伸長率彈性水泥環氧樹脂地坪仿石外牆屋頂浴室廚房"
    "地下擋土基混凝素含乾燥間隔包裝重量公斤平方米毫升溫濕攪拌滾筒噴槍壓力桶空機"
    "營造建築設計監驗收樣板報價詢問聯絡電話傳真信箱地址時間服務技術支援供貨系統配套"
    "產品規格特性適用場所參考建議數值一二三四五六七八九十百千萬年月日第共張版次"
    "０１２３４５６７８９，。、；：？！（）「」『』—…／·　"
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,:;-–—/()&'\"%°"
)

NUM_CHARS = ("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
             ".,:;/()[]-–—+×÷%²³°§&'\"®© ")


class Grab(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.buf = []

    def handle_starttag(self, tag, attrs):
        cls = set((dict(attrs).get("class") or "").split())
        if tag in DISPLAY_TAGS or (cls & DISPLAY_CLASS):
            self.depth += 1
        elif self.depth:
            self.depth += 1

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.buf.append(data)


def collect():
    chars = set()
    pages = 0
    for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        if os.sep + "_build" + os.sep in f:
            continue
        g = Grab()
        g.feed(open(f, encoding="utf-8").read())
        chars |= set("".join(g.buf))
        pages += 1
    chars = {c for c in chars if not c.isspace()}
    return chars | set(RESERVE), pages


def build(src, index, out, chars, label):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.desubroutinize = True
    opts.layout_features = ["kern", "palt", "locl", "ccmp"]
    opts.notdef_outline = False
    f = TTFont(src, fontNumber=index) if index is not None else TTFont(src)
    s = subset.Subsetter(options=opts)
    s.populate(text="".join(sorted(chars)))
    s.subset(f)
    f.flavor = "woff2"
    f.save(out)
    print(f"  {label:<10} {len(chars):>5} 字 → {os.path.getsize(out)/1024:>6.1f} KB")


if __name__ == "__main__":
    for p in (SERIF_SRC, NUM_SRC_R, NUM_SRC_B):
        if not os.path.exists(p):
            sys.exit(f"找不到字型來源：{p}\n"
                     "此腳本需要系統已安裝 Noto CJK 與 URW base35 字型。")
    os.makedirs(FONT_DIR, exist_ok=True)
    chars, pages = collect()
    print(f"掃描 {pages} 頁，標題用字 {len(chars)} 個")
    build(SERIF_SRC, SERIF_IDX, os.path.join(FONT_DIR, "serif-tc-700.woff2"), chars, "標題")
    build(NUM_SRC_R, None, os.path.join(FONT_DIR, "num-500.woff2"), set(NUM_CHARS), "數值 400")
    build(NUM_SRC_B, None, os.path.join(FONT_DIR, "num-700.woff2"), set(NUM_CHARS), "數值 700")
    print("完成。若新增了大量新文案，建議重新整理瀏覽器快取確認無缺字。")

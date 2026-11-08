# -*- coding: utf-8 -*-
"""剖面圖產生器 — 以工程圖的剖面大樣為語彙"""

INK, RULE, HATCH, REV, MUTED = "#1A2430", "#CDD2D8", "#B7BEC7", "#C8102E", "#7A8493"

# 各層的填充方式，對應製圖的材料剖面線
FILLS = {
    "solid":  '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#1A2430"/>',
    "mid":    '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#7A8493"/>',
    "light":  '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#DDE1E5" stroke="#1A2430" stroke-width="1"/>',
    "hatch":  '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#h45)" stroke="#1A2430" stroke-width="1"/>',
    "back":   '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#h135)" stroke="#1A2430" stroke-width="1"/>',
    "grit":   '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#grit)" stroke="#1A2430" stroke-width="1"/>',
    "line":   '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FCFCFB" stroke="#1A2430" stroke-width="1"/>',
}

FILLS_REV = {
    "solid":  '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF"/>',
    "mid":    '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#8FA6B8"/>',
    "light":  '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#2B4A5E" stroke="#DCE8F1" stroke-width="1"/>',
    "hatch":  '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#h45r)" stroke="#DCE8F1" stroke-width="1"/>',
    "back":   '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#h135r)" stroke="#DCE8F1" stroke-width="1"/>',
    "grit":   '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#gritr)" stroke="#DCE8F1" stroke-width="1"/>',
    "line":   '<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#12303F" stroke="#DCE8F1" stroke-width="1"/>',
}

DEFS_REV = '''<defs>
<pattern id="h45r" width="7" height="7" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
<line x1="0" y1="0" x2="0" y2="7" stroke="#DCE8F1" stroke-width="1"/></pattern>
<pattern id="h135r" width="9" height="9" patternTransform="rotate(-45)" patternUnits="userSpaceOnUse">
<line x1="0" y1="0" x2="0" y2="9" stroke="#5C7par" stroke-width="1.4"/></pattern>
<pattern id="gritr" width="8" height="8" patternUnits="userSpaceOnUse">
<rect width="8" height="8" fill="#1B3B4D"/>
<circle cx="2" cy="2" r="1.1" fill="#8FA6B8"/><circle cx="6.2" cy="5.4" r="1.4" fill="#FFFFFF"/>
<circle cx="6.6" cy="1.4" r=".8" fill="#5C7A8F"/><circle cx="2.4" cy="6.2" r=".9" fill="#A9BCCB"/></pattern>
</defs>'''.replace("#5C7par", "#5C7A8F")

DEFS = '''<defs>
<pattern id="h45" width="7" height="7" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
<line x1="0" y1="0" x2="0" y2="7" stroke="#1A2430" stroke-width="1"/></pattern>
<pattern id="h135" width="9" height="9" patternTransform="rotate(-45)" patternUnits="userSpaceOnUse">
<line x1="0" y1="0" x2="0" y2="9" stroke="#B7BEC7" stroke-width="1.4"/></pattern>
<pattern id="grit" width="8" height="8" patternUnits="userSpaceOnUse">
<rect width="8" height="8" fill="#EDEEEA"/>
<circle cx="2" cy="2" r="1.1" fill="#7A8493"/><circle cx="6.2" cy="5.4" r="1.4" fill="#1A2430"/>
<circle cx="6.6" cy="1.4" r=".8" fill="#B7BEC7"/><circle cx="2.4" cy="6.2" r=".9" fill="#47525F"/></pattern>
</defs>'''


def _spread(ys, gap=19.0, lo=12.0):
    """引線標籤防重疊：由上而下推開，維持最小間距"""
    out = list(ys)
    for i in range(1, len(out)):
        if out[i] - out[i - 1] < gap:
            out[i] = out[i - 1] + gap
    if out and out[0] < lo:
        shift = lo - out[0]
        out = [v + shift for v in out]
    return out


def stack(layers, *, w=520, lw=290, anim=False, marked=None, rev=False,
          labels=True, scale=1.0, aria="塗層剖面示意"):
    """水平層疊剖面：layers = [(名稱, 厚度px, 填充, 數值), ...] 由上而下
       labels=False 時不畫任何文字與引線，層體放大填滿整個畫面"""
    pad_t, pad_b, x0 = 16, 16, 10
    if not labels:
        lw = w - 2 * x0
    ths = [l[1] * scale for l in layers]
    body_h = sum(ths)
    # 先算各層中心，再推開標籤
    cys, y = [], pad_t
    for th in ths:
        cys.append(y + th / 2)
        y += th
    lys = _spread(cys)
    h = (pad_t + body_h + pad_b) if not labels else max(pad_t + body_h + pad_b, lys[-1] + pad_b + 6)

    F = FILLS_REV if rev else FILLS
    o = [f'<svg viewBox="0 0 {w} {h:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{aria}">',
         DEFS_REV if rev else DEFS]
    o.append('<g class="fig-anim">' if anim else '<g>')
    y = pad_t
    for (name, _, fill, val), th, cy, ly in zip(layers, ths, cys, lys):
        o.append('<g class="lay">')
        o.append(F[fill].format(x=x0, y=round(y, 1), w=lw, h=round(th, 1)))
        if labels:
            o.append(f'<path d="M{x0+lw} {cy:.1f} L{x0+lw+14} {cy:.1f} L{x0+lw+24} {ly:.1f} L{x0+lw+32} {ly:.1f}" '
                     f'fill="none" class="lay-ld"/>')
            cls = "lay-l lay-r" if (marked and name == marked) else "lay-l"
            o.append(f'<text x="{x0+lw+38}" y="{ly+4.5:.1f}" class="{cls}">{name}</text>')
            if val:
                o.append(f'<text x="{w-10}" y="{ly+4.5:.1f}" class="lay-n" text-anchor="end">{val}</text>')
        o.append('</g>')
        y += th
    o.append('</g>')
    if labels:
        # 總厚度標註
        bt, bb = pad_t, pad_t + body_h
        dim = "#6E8598" if rev else MUTED
        o.append(f'<line x1="{x0-5}" y1="{bt}" x2="{x0-5}" y2="{bb:.1f}" stroke="{dim}" stroke-width=".8"/>')
        o.append(f'<line x1="{x0-8}" y1="{bt}" x2="{x0-2}" y2="{bt}" stroke="{dim}" stroke-width=".8"/>')
        o.append(f'<line x1="{x0-8}" y1="{bb:.1f}" x2="{x0-2}" y2="{bb:.1f}" stroke="{dim}" stroke-width=".8"/>')
    o.append('</svg>')
    return "\n".join(o)


def wall(layers, *, w=372, h=290, marked=None, rev=False, lang="zh"):
    """垂直層疊剖面（牆體）：由外而內"""
    x0, y0, hh = 16, 26, 168
    F = FILLS_REV if rev else FILLS
    o = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="牆體剖面示意">',
         DEFS_REV if rev else DEFS]
    o.append(f'<text x="{x0}" y="16" class="lay-l">{"室外" if lang == "zh" else "Outside"}</text>')
    o.append(f'<text x="{w-14}" y="16" class="lay-l" text-anchor="end">{"室內" if lang == "zh" else "Inside"}</text>')
    o.append('<g>')
    x = x0
    labels = []
    for name, th, fill, val in layers:
        o.append(F[fill].format(x=x, y=y0, w=th, h=hh))
        labels.append((x + th / 2, name, val, name == marked))
        x += th
    o.append('</g>')
    step = 0
    for cx, name, val, mk in labels:
        ly = y0 + hh + 26 + (step % 2) * 34
        o.append(f'<line x1="{cx:.1f}" y1="{y0+hh}" x2="{cx:.1f}" y2="{ly-9}" class="lay-ld"/>')
        cls = "lay-l lay-r" if mk else "lay-l"
        o.append(f'<text x="{cx:.1f}" y="{ly}" class="{cls}" text-anchor="middle">{name}</text>')
        if val:
            o.append(f'<text x="{cx:.1f}" y="{ly+15}" class="lay-n" text-anchor="middle">{val}</text>')
        step += 1
    o.append('</svg>')
    return "\n".join(o)


def corner(*, w=520, h=290, rev=False, lang="zh"):
    """浴室：牆面翻邊＋地坪＋地排的 L 型剖面"""
    Z = lang == "zh"
    ink = "#DCE8F1" if rev else "#1A2430"
    red = "#D8CFB4" if rev else "#24506B"
    box = "#12303F" if rev else "#FCFCFB"
    hp = "url(#h135r)" if rev else "url(#h135)"
    o = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="浴室防水翻邊剖面示意">',
         DEFS_REV if rev else DEFS]
    o.append('<g>')
    # 結構體
    o.append(f'<rect x="40" y="30" width="46" height="200" fill="{hp}" stroke="{ink}"/>')
    o.append(f'<rect x="40" y="230" width="420" height="42" fill="{hp}" stroke="{ink}"/>')
    # 防水層（牆面翻邊 → 轉角 → 地坪）
    o.append(f'<path d="M86 42 L86 230 L460 230" fill="none" stroke="{ink}" stroke-width="7"/>')
    o.append(f'<path d="M86 42 L86 224 Q86 224 92 224 L460 224" fill="none" stroke="{red}" stroke-width="2.6"/>')
    # 地排
    o.append(f'<rect x="330" y="224" width="52" height="48" fill="{box}" stroke="{ink}"/>')
    o.append(f'<path d="M330 224 L330 258 M382 224 L382 258" stroke="{red}" stroke-width="2.6" fill="none"/>')
    o.append('</g>')
    # 標註
    t1 = "牆面翻邊 ≥ 300 mm" if Z else "Upstand ≥ 300 mm"
    t2 = "淋浴區翻至 1800 mm 以上" if Z else "Shower zone ≥ 1800 mm"
    t3 = "防水層須連續不中斷" if Z else "Membrane continuous, no breaks"
    t4 = "地排包覆至內緣" if Z else "Sealed into the gully"
    o.append('<line x1="86" y1="52" x2="106" y2="52" class="lay-ld"/>')
    o.append(f'<text x="112" y="56" class="lay-l">{t1}</text>')
    o.append('<line x1="86" y1="78" x2="106" y2="78" class="lay-ld"/>')
    o.append(f'<text x="112" y="82" class="lay-l">{t2}</text>')
    o.append('<line x1="220" y1="224" x2="220" y2="196" class="lay-ld"/>')
    o.append(f'<text x="220" y="190" class="lay-l lay-r" text-anchor="middle">{t3}</text>')
    o.append('<line x1="356" y1="272" x2="356" y2="284" class="lay-ld"/>')
    o.append(f'<text x="356" y="288" class="lay-l" text-anchor="middle">{t4}</text>')
    o.append('</svg>')
    return "\n".join(o)


def water_sides(*, w=520, h=282, rev=False, lang="zh"):
    """地下室：迎水面與背水面對照"""
    Z = lang == "zh"
    ink = "#DCE8F1" if rev else "#1A2430"
    sol = "#FFFFFF" if rev else "#1A2430"
    red = "#D8CFB4" if rev else "#24506B"
    arw = "#8FA6B8" if rev else "#7A8493"
    hp = "url(#h135r)" if rev else "url(#h135)"
    o = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="迎水面與背水面對照示意">',
         DEFS_REV if rev else DEFS, '<g>']
    o.append(f'<rect x="228" y="34" width="58" height="168" fill="{hp}" stroke="{ink}"/>')
    o.append(f'<rect x="218" y="34" width="10" height="168" fill="{sol}"/>')
    o.append(f'<rect x="286" y="34" width="7" height="168" fill="{red}" opacity=".85"/>')
    # 水壓箭頭
    for i, yy in enumerate((66, 106, 146, 186)):
        o.append(f'<path d="M150 {yy} L212 {yy}" stroke="{arw}" stroke-width="1.2"/>')
        o.append(f'<path d="M212 {yy} l-7 -3.6 l0 7.2 z" fill="{arw}"/>')
    o.append('</g>')
    o.append(f'<text x="150" y="26" class="lay-l">{"水壓方向" if Z else "Water pressure"}</text>')
    o.append('<line x1="218" y1="222" x2="218" y2="212" class="lay-ld"/>')
    o.append(f'<text x="196" y="238" class="lay-l" text-anchor="middle">{"迎水面" if Z else "Positive side"}</text>')
    o.append('<text x="196" y="254" class="lay-n" text-anchor="middle">outside</text>')
    o.append('<line x1="290" y1="222" x2="290" y2="212" class="lay-ld"/>')
    o.append(f'<text x="330" y="238" class="lay-l lay-r" text-anchor="middle">{"背水面" if Z else "Negative side"}</text>')
    o.append('<text x="330" y="254" class="lay-n lay-r" text-anchor="middle">inside</text>')
    c3 = ("滲透結晶", "滲入混凝土內部", "生成結晶堵塞毛孔") if Z else \
         ("Crystalline slurry", "penetrates the concrete", "and seals capillaries")
    o.append(f'<text x="330" y="82" class="lay-l">{c3[0]}</text>')
    o.append(f'<text x="330" y="100" class="lay-l">{c3[1]}</text>')
    o.append(f'<text x="330" y="118" class="lay-l">{c3[2]}</text>')
    o.append('<line x1="296" y1="90" x2="322" y2="90" class="lay-ld"/>')
    m2 = ("彈性水泥或", "複合式防水塗膜") if Z else ("Flexible cement or", "compound membrane")
    o.append(f'<text x="150" y="118" class="lay-l" text-anchor="end">{m2[0]}</text>')
    o.append(f'<text x="150" y="136" class="lay-l" text-anchor="end">{m2[1]}</text>')
    o.append('</svg>')
    return "\n".join(o)


# ── 各頁面用的圖（zh／en 標註）───────────────────

def fig_roof(anim=False, rev=False, labels=True, scale=1.0, lang="zh"):
    L = [("面漆／保護層", 15, "solid", "0.2"),
         ("主防水層", 40, "hatch", "1.0–1.6"),
         ("防水底漆", 11, "mid", "0.1"),
         ("RC 素地", 52, "back", "")] if lang == "zh" else \
        [("Topcoat / protection", 15, "solid", "0.2"),
         ("Main membrane", 40, "hatch", "1.0–1.6"),
         ("Waterproof primer", 11, "mid", "0.1"),
         ("RC substrate", 52, "back", "")]
    return stack(L, anim=anim, rev=rev, labels=labels, scale=scale,
                 lw=290 if lang == "zh" else 236,
                 marked=L[1][0], aria="屋頂防水標準三層構成剖面示意" if lang == "zh"
                 else "Standard three-layer roof waterproofing section")


def fig_floor(anim=False, rev=False, labels=True, scale=1.0, lang="zh"):
    L = [("面塗", 14, "solid", "0.3"),
         ("中塗（結構層）", 46, "hatch", "1–3 mm"),
         ("底塗", 11, "mid", "0.1"),
         ("混凝土素地", 52, "back", "")] if lang == "zh" else \
        [("Topcoat", 14, "solid", "0.3"),
         ("Body coat (structure)", 46, "hatch", "1–3 mm"),
         ("Primer", 11, "mid", "0.1"),
         ("Concrete substrate", 52, "back", "")]
    return stack(L, anim=anim, rev=rev, labels=labels, scale=scale,
                 lw=290 if lang == "zh" else 236,
                 marked=L[1][0], aria="環氧樹脂地坪三層構成剖面示意" if lang == "zh"
                 else "Three-stage epoxy floor build-up section")


def fig_stone(anim=False, rev=False, labels=True, scale=1.0, lang="zh"):
    L = [("透明保護面塗", 12, "line", "≥ 0.2"),
         ("多彩花崗岩塗料", 38, "grit", "0.9–1.2"),
         ("有色面塗", 15, "mid", "0.2–0.3"),
         ("紋理造型漆", 22, "light", "≥ 1.0"),
         ("接著底漆", 11, "solid", "≥ 0.15"),
         ("RC 素地", 48, "back", "")] if lang == "zh" else \
        [("Clear protective coat", 12, "line", "≥ 0.2"),
         ("Multi-colour granite", 38, "grit", "0.9–1.2"),
         ("Coloured topcoat", 15, "mid", "0.2–0.3"),
         ("Texture coat", 22, "light", "≥ 1.0"),
         ("Bonding primer", 11, "solid", "≥ 0.15"),
         ("RC substrate", 48, "back", "")]
    return stack(L, anim=anim, rev=rev, labels=labels, scale=scale,
                 lw=290 if lang == "zh" else 236,
                 marked=L[1][0], aria="外牆仿石塗料五層塗裝結構剖面示意" if lang == "zh"
                 else "Five-layer stone-effect coating section")


def fig_wall(rev=False, lang="zh"):
    L = [("面漆", 40, "solid", "0.2"),
         ("主防水層", 72, "hatch", "1.0"),
         ("底漆", 28, "mid", "0.1"),
         ("RC 牆體", 152, "back", "")] if lang == "zh" else \
        [("Topcoat", 40, "solid", "0.2"),
         ("Membrane", 72, "hatch", "1.0"),
         ("Primer", 28, "mid", "0.1"),
         ("RC wall", 152, "back", "")]
    return wall(L, marked=L[1][0], rev=rev, lang=lang)


FIGS = {
    "roof": fig_roof, "floor": fig_floor, "stone": fig_stone,
    "wall": fig_wall, "bath": corner, "basement": water_sides,
}

# -*- coding: utf-8 -*-
"""website-v2 全站產生器（第二部分）"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from layout2 import head, titleblock, masthead, ask_band, foot, plate, fig, hero, T, SITE
from build_all import (ld, crumb, faq_ld, list_ld, qa_block, write, pfx, dep,
                       series_rows, brief_split, DATA, build_home, build_waterproofing)
import figures as F
from content import EPOXY, SOLUTIONS, ARTICLES

EPX = EPOXY
SOL = SOLUTIONS
ART = ARTICLES

L = {
 "zh": dict(h5a="產品特性", h5b="適用場所", h5c="參考資訊", faq="常見問題",
            gal="地坪實景", swatch="色卡", sys="地坪系統", layers="配套材料",
            step="工序", tool="工具", qty="用量", gap="間隔", other="其他施作部位",
            rel="相關文章", sup="補充", form="工程詢價單", formno="表單 ENQ-01",
            send="用 Gmail 傳送", send_alt="用電子郵件軟體", copy="複製內容", copied="已複製",
            callus="或直接來電 %%TEL1%%",
            note="選擇一種寄送方式，上方內容會自動帶入。也可以複製後貼到任何地方寄給我們。",
            co="公司資料", svc="服務內容", lines="三條產品線"),
 "en": dict(h5a="Characteristics", h5b="Applications", h5c="Reference", faq="Frequently asked questions",
            gal="Installed floors", swatch="Colour range", sys="Floor systems", layers="System components",
            step="Step", tool="Tools", qty="Coverage", gap="Interval", other="Other applications",
            rel="Related insights", sup="Supplementary", form="Project enquiry", formno="Form ENQ-01",
            send="Send with Gmail", send_alt="Use email app", copy="Copy details", copied="Copied",
            callus="Or call us on %%TEL1_INTL%%",
            note="Pick how you'd like to send it — the details above are filled in for you. You can also copy them and send from anywhere.",
            co="Company details", svc="Services", lines="Three product lines"),
}


# ══════════════════════════════════ 環氧樹脂地坪

def build_epoxy(lang):
    C, T_ = EPX[lang], T[lang]
    d, u, up = dep(lang), ("../" if lang == "en" else ""), pfx(lang)
    path = f"/{up}epoxy.html"
    jump = "".join(f'<a href="#{s["id"]}">{s["name"]}</a>' for s in C["series"])
    rows = series_rows(lang, [dict(id=s["id"], name=s["name"], tagline=s["tag"],
                                   k=(("基礎" if lang == "zh" else "Base") if s["id"] in ("primer", "body") else None),
                                   desc=s["desc"], feat=s["feat"], use=s["use"], spec=s["spec"])
                              for s in C["series"]], L[lang]["h5a"], L[lang]["h5b"], L[lang]["h5c"])
    o = [head(lang, C["title"], C["desc"], path, depth=d, kw=C["kw"],
              preload=u + "assets/img/floor/epoxy-05.jpg",
              ld=ld(crumb(lang, [(T_["nav"][0][0], f"/{up}"), (C["h1"], path)]), faq_ld(C["faq"]),
                    list_ld(C["series_h2"], path, [(s["name"], s["id"]) for s in C["series"] if s["id"] not in ("primer", "body")]))),
         titleblock(lang, "epoxy.html"),
         masthead(lang, "epoxy.html", depth=d),
         hero(lang, photo=u + "assets/img/floor/epoxy-05.jpg",
              tag=L[lang]["sys"], h1=C["h1"], lead=C["lead"], sub=True,
              figure=fig(F.fig_floor(rev=True, lang=lang),
                         "地坪三層構成" if lang == "zh" else "Three-stage build-up",
                         "大樣 C-01" if lang == "zh" else "Detail C-01", rev=True)),
         f'''
<section class="band grey">
  <div class="page">
    <div class="cap"><div class="no">{C["series_kick"]}</div><h2>{C["series_h2"]}</h2><p>{C["series_p"]}</p></div>
    <div class="jump">{jump}</div>
    <div class="schedule">{rows}</div>
  </div>
</section>''',
         qa_block(C["faq"], C["faq_h2"]),
         ask_band(lang, depth=d),
         foot(lang, depth=d)]
    write(up + "epoxy.html", "\n".join(o))


# ══════════════════════════════════ 外牆仿石塗料

STONE = {
 "zh": dict(title="外牆多彩仿石塗料｜仿花崗岩塗料、塗裝系統與色卡｜暉盈國際",
   desc="水性多彩仿花崗岩外牆塗料，一槍成型、仿真度達 90% 以上。提供五層塗裝結構、七道施工工序與 %%N_SW%% 組色系。",
   kw="外牆仿石塗料, 仿花崗岩塗料, 多彩塗料, 外牆拉皮, 崗石塗料",
   tag="塗裝系統", h1="外牆多彩仿石塗料",
   lead="精仿天然花崗岩的水性多彩塗料，主材一槍成型即可形成高仿花崗岩效果，是高檔石材的環保替代方案。",
   figcap="五層塗裝結構", figcode="大樣 B-01",
   sys_p="從素地整理到透明保護面塗共七道工序，每一道的用量與乾燥時間都影響最終效果。",
   lay_p="五個塗層缺一不可，每一層都有各自的功能與建議用量。",
   sw_p="單一色板中可同時呈現白點、黑點、灰點、橘點、鏽點等多種顆粒，色彩可依設計需求調整。實際顏色請以現場樣板為準。",
   sw_note="現場樣板為準", faq_h="常見問題",
   spec_h="施工設備需求",
   spec=[("空壓機", "功率 7.5 KW 以上，氣承壓力 ≥ 8 kg（建議 11–12 kg）"),
         ("壓力桶", "氣壓 0.6–0.8 kg，不可超過 2.5 kg"),
         ("噴槍管道", "直徑 8 mm × 12 mm，出料管長度小於 4 米"),
         ("其他", "滾筒、專用噴槍；每日完工須清理管線")]),
 "en": dict(title="Stone-Effect Wall Coating｜Granite-Look Facade System and Colours｜Huiying",
   desc="Water-based multi-colour granite-effect exterior coating, sprayed in one pass. Five-layer build-up, seven-step sequence and %%N_SW%% colourways.",
   kw="stone effect coating, granite look wall coating, multicolour facade coating",
   tag="Coating system", h1="Stone-effect wall coating",
   lead="A water-based multi-colour coating closely reproducing natural granite, formed in a single spray pass — an environmentally responsible alternative to stone cladding.",
   figcap="Five-layer build-up", figcode="Detail B-01",
   sys_p="Seven steps from substrate preparation to clear protective coat; coverage and drying times govern the result.",
   lay_p="Five coats, none optional, each with a distinct function and coverage rate.",
   sw_p="A single panel can carry white, black, grey, orange and rust particles simultaneously, and colours can be adjusted to the design. Final colour should be confirmed against a site sample panel.",
   sw_note="Confirm on site", faq_h="Frequently asked questions",
   spec_h="Equipment required",
   spec=[("Compressor", "7.5 KW or above, working pressure ≥ 8 kg (11–12 kg recommended)"),
         ("Pressure pot", "Regulated to 0.6–0.8 kg, never above 2.5 kg"),
         ("Spray line", "8 mm × 12 mm; delivery hose under 4 m"),
         ("Other", "Roller and dedicated spray gun; clean lines daily")]),
}

FAQ_ST = {
 "zh": [("仿石塗料和真的花崗石差在哪？",
   "外觀上仿真度可達 90% 以上。主要差異在重量與成本：塗料不需要石材的吊掛與乾式工法結構，大幅降低結構載重與施工成本，也避免天然石材開採對環境的破壞。"),
  ("完整的塗裝系統有哪幾層？",
   "共五個塗層：接著底漆 → 紋理造型漆 → 有色面塗 → 多彩花崗岩塗料 → 透明保護面塗。施作前需先整理素地；如需分割立面，可在紋理層前貼溝縫膠帶，主材噴塗後立即撕除。"),
  ("整個工序要多久？",
   "取決於乾燥時間。紋理造型漆、有色面塗與多彩主材噴塗後，各需乾燥硬化 24 小時以上才能進行下一道。以正常天候計算，單一立面約需 4–6 個工作天。"),
  ("顏色可以指定嗎？",
   "可以。建議先製作現場樣板，經監造單位與業主確認顏色與紋路後再大面積施作，樣板同時作為驗收的比對憑據。")],
 "en": [("How does stone-effect coating compare with real granite?",
   "Visually it reaches over 90% match. The main differences are weight and cost: a coating needs no cladding support structure, which substantially reduces structural load and installation cost, and avoids the environmental impact of quarrying."),
  ("What layers make up the complete system?",
   "Five coats: bonding primer, texture coat, coloured topcoat, multi-colour granite coat and clear protective coat. The substrate is prepared first; where the elevation is to be divided, joint tape is applied before the texture coat and removed immediately after the main coat."),
  ("How long does the full sequence take?",
   "It is governed by drying times: the texture coat, coloured topcoat and multi-colour coat each need at least 24 hours before the next coat. In normal weather a single elevation takes four to six working days."),
  ("Can colours be specified?",
   "Yes. We recommend producing a site sample panel for client and supervisor approval before proceeding, which then serves as the reference for handover inspection.")],
}


def build_stone(lang):
    C, T_, LL = STONE[lang], T[lang], L[lang]
    d, u, up = dep(lang), ("../" if lang == "en" else ""), pfx(lang)
    path = f"/{up}stone.html"
    D = DATA[lang]

    # 配套材料：收合列＋跳轉選單
    ljump = "".join(f'<a href="#lay-{i+1:02d}">{p["name"]}</a>'
                    for i, p in enumerate(D["STONE_PRODUCTS"]))
    lay_rows = []
    for i, p in enumerate(D["STONE_PRODUCTS"]):
        b, _ = brief_split(p["desc"], lang)
        rp = f'<p>{p["desc"]}</p>'
        feats = "".join(f"<li>{x}</li>" for x in p["feat"])
        lay_rows.append(f'''<details class="acc" id="lay-{i+1:02d}">
  <summary>
    <span class="k">{i+1:02d}</span>
    <span class="t"><h3>{p["name"]}</h3></span>
    <span class="brief">{b}</span>
    <span class="tg" aria-hidden="true"></span>
  </summary>
  <div class="rb">
    {rp}
    <div class="cols">
      <div><h5>{LL["h5a"]}</h5><ul class="marks">{feats}</ul></div>
      <div><h5>{LL["h5c"]}</h5><div class="data">
        <div><span>{LL["qty"]}</span><b>{p["qty"]}</b></div>
        <div><span>{"包裝" if lang == "zh" else "Packaging"}</span><b>{p["pack"]}</b></div>
      </div></div>
    </div>
  </div>
</details>''')
    layers = "".join(lay_rows)
    sw = "".join(
        f'<button type="button" class="sw"><img loading="lazy" '
        f'src="{u}{s["img"]}" alt="{s["name"]}">'
        f'<span class="nm">{s["name"]}</span></button>' for s in D["STONE_SWATCHES"])
    spec = "".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in C["spec"])

    o = [head(lang, C["title"], C["desc"], path, depth=d, kw=C["kw"],
              preload=u + "assets/img/photo/hero-3.jpg",
              ld=ld(crumb(lang, [(T_["nav"][0][0], f"/{up}"), (C["h1"], path)]), faq_ld(FAQ_ST[lang]),
                    list_ld(LL["layers"], path,
                            [(p["name"], f"lay-{i+1:02d}") for i, p in enumerate(D["STONE_PRODUCTS"])]))),
         titleblock(lang, "stone.html"),
         masthead(lang, "stone.html", depth=d),
         hero(lang, photo=u + "assets/img/photo/hero-3.jpg",
              tag=C["tag"], h1=C["h1"], lead=C["lead"], sub=True,
              figure=fig(F.fig_stone(rev=True, lang=lang), C["figcap"], C["figcode"], rev=True)),
         f'''
<section class="band grey">
  <div class="page">
    <div class="cap"><div class="no">{LL["layers"]}</div><h2>{LL["layers"]}</h2><p>{C["lay_p"]}</p></div>
    <div class="jump">{ljump}</div>
    <div class="schedule">{layers}</div>
  </div>
</section>

<section class="band" id="swatch">
  <div class="page">
    <div class="cap"><div class="no">{LL["swatch"]}</div><h2>{LL["swatch"]}</h2><p>{C["sw_p"]}</p></div>
    <div class="swgrid">{sw}</div>
  </div>
</section>''',
         qa_block(FAQ_ST[lang], C["faq_h"]),
         f'''
<section class="band grey slim">
  <div class="page">
    <div class="cap" style="margin-bottom:22px"><div class="no">{LL["sup"]}</div><h2 style="font-size:20px">{C["spec_h"]}</h2></div>
    <div class="tbl-wrap"><table class="tbl">
      {spec}
    </table></div>
  </div>
</section>''',
         ask_band(lang, depth=d),
         foot(lang, depth=d)]
    write(up + "stone.html", "\n".join(o))


# ══════════════════════════════════ 應用場景頁

SOL_FIG = {"roof-waterproofing": ("roof", "屋頂標準構成", "Standard roof build-up", "大樣 D-05", "Detail D-05"),
           "bathroom-waterproofing": ("bath", "浴室翻邊與地排", "Upstand and gully detail", "大樣 D-06", "Detail D-06"),
           "basement-waterproofing": ("basement", "迎水面與背水面", "Positive and negative side", "大樣 D-07", "Detail D-07"),
           "exterior-wall-coating": ("wall", "外牆層次", "External wall build-up", "大樣 D-08", "Detail D-08"),
           "parking-floor": ("floor", "地坪三層構成", "Three-stage floor build-up", "大樣 D-09", "Detail D-09")}
SOL_FN = {"roof": F.fig_roof, "bath": F.corner, "basement": F.water_sides,
          "wall": F.fig_wall, "floor": F.fig_floor}


def build_solution(lang, s, allsol):
    LL, T_ = L[lang], T[lang]
    d, u, up = dep(lang), ("../" if lang == "en" else ""), pfx(lang)
    path = f"/{up}{s['slug']}.html"
    key, cz, ce, nz, ne = SOL_FIG[s["slug"]]
    figure = fig(SOL_FN[key](rev=True, lang=lang), cz if lang == "zh" else ce,
                 nz if lang == "zh" else ne, rev=True)

    body = []
    for i, sec in enumerate(s["sections"]):
        inner = "".join(f"<p>{p}</p>" for p in sec.get("p", []))
        if sec.get("list"):
            inner += '<ul class="marks" style="margin-top:6px">' + "".join(
                f"<li>{x}</li>" for x in sec["list"]) + "</ul>"
        if sec.get("table"):
            tb = sec["table"]
            inner += ('<div class="tbl-wrap" style="margin-top:14px"><table class="tbl"><tr>'
                      + "".join(f"<th>{c}</th>" for c in tb["head"]) + "</tr>"
                      + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in tb["rows"])
                      + "</table></div>")
        if sec.get("link"):
            lab, href = sec["link"]
            inner += f'<p style="margin-top:16px"><a class="btn line" href="{u}{href}">{lab}</a></p>'
        body.append(f'<div class="clause"><div class="s">§ {i+1}.0</div><div class="b">'
                    f'<h2>{sec["h"]}</h2>{inner}</div></div>')

    others = "".join(
        f'<a href="{u}{o["slug"]}.html">'
        f'<h3>{o["h1"]}</h3><span class="desc">{o["desc"][:56]}…</span><span class="go">→</span></a>'
        for o in allsol if o["slug"] != s["slug"])

    o = [head(lang, s["title"], s["desc"], path, depth=d, kw=s.get("kw"),
              preload=u + "assets/img/" + s.get("photo", "photo/hero-2.jpg"),
              ld=ld(crumb(lang, [(T_["nav"][0][0], f"/{up}"),
                                 (T_["nav"][0][0], f"/{up}waterproofing.html"), (s["h1"], path)]))),
         titleblock(lang, s["slug"] + ".html"),
         masthead(lang, "waterproofing.html", depth=d),
         hero(lang, photo=u + "assets/img/" + s.get("photo", "photo/hero-2.jpg"),
              tag="施作部位" if lang == "zh" else "Application",
              h1=s["h1"], lead=s["lead"], figure=figure, sub=True),
         f'''
<section class="band grey">
  <div class="text"><div class="doc">{"".join(body)}</div></div>
</section>

<section class="band dark">
  <div class="page">
    <div class="cap"><div class="no">{LL["other"]}</div><h2>{LL["other"]}</h2></div>
    <div class="index">{others}</div>
  </div>
</section>

<section class="ask-band">
  <div class="page">
    <div><h2>{"需要材料建議？" if lang == "zh" else "Need a specification?"}</h2><p>{s["cta"]}</p></div>
    <a class="btn" href="{u}contact.html">{T_["ask_b"]}</a>
  </div>
</section>''',
         foot(lang, depth=d)]
    write(up + s["slug"] + ".html", "\n".join(o))

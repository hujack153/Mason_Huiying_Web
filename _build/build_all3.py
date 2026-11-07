# -*- coding: utf-8 -*-
"""website-v2 全站產生器（第三部分：專欄、關於、詢價、404、執行）"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from layout2 import head, titleblock, masthead, ask_band, foot, plate, fig, T, SITE
from build_all import ld, crumb, faq_ld, qa_block, write, pfx, dep, DATA, build_home, build_waterproofing
from build_all2 import build_epoxy, build_stone, build_solution, SOL, ART, L
import figures as F

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

INTRO = {
 "zh": dict(title="技術專欄｜防水材料選材與施工知識｜暉盈國際",
   desc="防水材料選材指南、材料差異比較與施工常見問題。由實際供料與現場經驗整理，提供給營造廠、防水工程行與建築設計單位參考。",
   h1="技術專欄", tag="技術說明",
   lead="材料規格表看得懂，不等於知道該用哪一個。這裡整理我們在供料與現場最常被問到的問題。"),
 "en": dict(title="Insights｜Waterproofing Material Selection and Application｜Huiying",
   desc="Practical guides on choosing waterproofing materials, comparing types and avoiding common application failures, drawn from site experience.",
   h1="Insights", tag="Technical notes",
   lead="Reading a data sheet is not the same as knowing which product to use. These are the questions we are asked most often on site."),
}


def build_insights_index(lang):
    C, T_, LL = INTRO[lang], T[lang], L[lang]
    d, u, up = dep(lang, sub=True), ("../" * dep(lang, sub=True)), pfx(lang)
    path = f"/{up}insights/"
    arts = ART[lang]
    rows = "".join(
        f'<a href="{a["slug"]}.html">'
        f'<span class="th"><img loading="lazy" src="{u}{a["hero"]}" alt=""></span>'
        f'<span><h3>{a["title"]}</h3><p>{a["desc"]}</p></span>'
        f'<span class="meta">TN-{i+1:02d}<br>{a["date"]}</span></a>'
        for i, a in enumerate(arts))
    coll = {"@context": "https://schema.org", "@type": "CollectionPage",
            "name": C["h1"], "description": C["desc"], "inLanguage": T_["lang"], "url": SITE + path,
            "hasPart": [{"@type": "Article", "headline": a["title"], "datePublished": a["date"],
                         "url": SITE + f"/{up}insights/{a['slug']}.html"} for a in arts]}
    o = [head(lang, C["title"], C["desc"], path, depth=d, ld=ld(coll)),
         titleblock(lang, "insights/index.html"),
         masthead(lang, "insights/index.html", depth=d),
         f'''
<div class="head">
  <div class="page">
    <span class="tag">{C["tag"]}</span>
    <h1>{C["h1"]}</h1>
    <p class="lead">{C["lead"]}</p>
  </div>
</div>

<section class="band">
  <div class="page"><div class="posts">{rows}</div></div>
</section>''',
         ask_band(lang, depth=d),
         foot(lang, depth=d)]
    write(up + "insights/index.html", "\n".join(o))


def build_article(lang, a, idx, arts):
    T_, LL = T[lang], L[lang]
    d = dep(lang, sub=True)
    u = "../" * d
    up = pfx(lang)
    path = f"/{up}insights/{a['slug']}.html"

    body = []
    n = 0
    for sec in a["sections"]:
        n += 1
        inner = "".join(f"<p>{p}</p>" for p in sec.get("p", []))
        clauses = [f'<div class="clause"><div class="s">§ {n}.0</div>'
                   f'<div class="b"><h2>{sec["h"]}</h2>{inner or ""}</div></div>']
        if sec.get("list"):
            lst = '<ul class="marks">' + "".join(f"<li>{x}</li>" for x in sec["list"]) + "</ul>"
            clauses.append(f'<div class="clause note"><div class="s">§ {n}.1</div>'
                           f'<div class="b">{lst}</div></div>')
        if sec.get("table"):
            tb = sec["table"]
            t = ('<div class="tbl-wrap"><table class="tbl"><tr>'
                 + "".join(f"<th>{c}</th>" for c in tb["head"]) + "</tr>"
                 + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in tb["rows"])
                 + "</table></div>")
            clauses.append(f'<div class="clause"><div class="s">§ {n}.1</div><div class="b">{t}</div></div>')
        body += clauses

    rel = "".join(
        f'<a href="{o["slug"]}.html"><span class="code">TN-{j+1:02d}</span>'
        f'<h3>{o["title"]}</h3><span class="desc">{o["desc"][:58]}…</span><span class="go">→</span></a>'
        for j, o in enumerate(arts) if o["slug"] != a["slug"])

    art_ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
              "description": a["desc"], "datePublished": a["date"], "dateModified": a["date"],
              "inLanguage": T_["lang"], "image": SITE + "/" + a["hero"],
              "author": {"@type": "Organization", "name": T["zh"]["co"], "url": SITE + "/"},
              "publisher": {"@type": "Organization", "name": T["zh"]["co"],
                            "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/brand/icon-512.png"}},
              "mainEntityOfPage": {"@type": "WebPage", "@id": SITE + path}}

    o = [head(lang, a["title"], a["desc"], path, depth=d, kw=a.get("kw"), art=True,
              ld=ld(art_ld, crumb(lang, [(T_["nav"][0][0], f"/{up}"),
                                         (T_["insights"], f"/{up}insights/"), (a["title"], path)]))),
         titleblock(lang, "insights/index.html", extra=f"TN-{idx+1:02d}"),
         masthead(lang, "insights/index.html", depth=d),
         f'''
<div class="head">
  <div class="page">
    <span class="tag">{INTRO[lang]["tag"]} TN-{idx+1:02d}</span>
    <h1 style="max-width:26ch">{a["title"]}</h1>
    <p class="lead num" style="font-size:15px">{T_["pub"]} {a["date"]}</p>
  </div>
</div>

<section class="band">
  <div class="text">
    <p class="abstract">{a["lead"]}</p>
    <div style="max-width:560px;margin-bottom:44px">{plate(u + a["hero"], T_["photo"], f"PH-{idx+31}")}</div>
    <div class="doc">{"".join(body)}</div>
    <p style="margin-top:32px"><a class="btn line" href="index.html">← {T_["back"]}</a></p>
  </div>
</section>

<section class="band grey">
  <div class="page">
    <div class="cap"><div class="no">{LL["rel"]}</div><h2>{LL["rel"]}</h2></div>
    <div class="index">{rel}</div>
  </div>
</section>''',
         ask_band(lang, depth=d),
         foot(lang, depth=d)]
    html = "\n".join(o)
    # 只有單一語言版本的文章：另一語言的對照連結改指向該語言的專欄列表，避免連到不存在的頁面
    other = "en" if lang == "zh" else "zh"
    if a["slug"] not in {x["slug"] for x in ART[other]}:
        o_hl = "en" if other == "en" else "zh-Hant"
        o_idx = SITE + ("/en/insights/" if other == "en" else "/insights/")
        html = re.sub(rf'(<link rel="alternate" hreflang="{o_hl}" href=")[^"]*(")', rf"\g<1>{o_idx}\g<2>", html)
        if other == "zh":  # 沒有中文版時，x-default 指向英文版本身
            html = re.sub(r'(<link rel="alternate" hreflang="x-default" href=")[^"]*(")', rf"\g<1>{SITE}{path}\g<2>", html)
    write(up + f"insights/{a['slug']}.html", html)


# ══════════════════════════════════ 關於

ABOUT = {
 "zh": dict(title="關於暉盈｜建材供應與技術服務｜暉盈國際事業有限公司",
   desc="暉盈國際事業有限公司專營建築防水材料、外牆裝飾塗料與環氧樹脂地坪系統的銷售與技術服務，服務營造廠、防水工程行、建築師事務所與物業管理單位。",
   tag="公司資料", h1="關於暉盈",
   lead="我們的價值在於：選對材料、配出完整系統、在工地現場解決問題。",
   p1="暉盈國際事業有限公司位於新北市新莊區，專營建築防水材料、外牆裝飾塗料與環氧樹脂地坪系統的銷售與技術服務，服務對象包含營造廠、專業防水工程行、建築師事務所與物業管理單位。",
   p2="除了供貨之外，我們也協助客戶進行材料選配、樣板施作與現場技術說明。防水工程的成敗往往不在單一材料，而在整套系統的搭配與施工細節，這也是我們最花心力的地方。",
   rows=[("公司名稱", "暉盈國際事業有限公司　Huiying Int'l Business Co."),
         ("統一編號", "%%TAX%%"), ("電話", "%%TEL1%%　%%TEL2%%"),
         ("傳真", "%%FAX%%"), ("電子信箱", "%%EMAIL%%"),
         ("地址", "%%ADDR_ZH_FULL%%"),
         ("洽詢時間", "週一至週五 08:30–17:30"),
         ("主要業務", "建築防水材料、外牆裝飾塗料、環氧樹脂地坪材料之銷售與技術服務")],
   svc=[("材料選配", "依施作部位、基材狀況、氣候條件與工期，配出底漆、主防水層與面漆的完整組合。"),
        ("樣板與確認", "外牆裝飾工程可先製作樣板，經監造單位與業主確認後作為驗收憑據。"),
        ("供貨與技術支援", "依工程進度分批供貨；開工前可安排施工說明，施作期間持續協助。")],
   lines=[("02", "建築防水材料", "waterproofing.html", "%%N_WP_ZH%%大系列，涵蓋屋頂、外牆、浴廁與地下室工程"),
          ("03", "外牆多彩仿石塗料", "stone.html", "五層塗裝結構、七道工序、%%N_SW%% 組色系"),
          ("04", "環氧樹脂地坪系統", "epoxy.html", "%%N_EPX_ZH%%套系統，適用廠房、無塵室、停車場與醫療空間")]),
 "en": dict(title="About Huiying｜Building Material Supply and Technical Service｜Taiwan",
   desc="Huiying Int'l supplies waterproofing materials, decorative exterior coatings and epoxy flooring, with technical service for contractors in Taiwan.",
   tag="Company details", h1="About Huiying",
   lead="What we offer is judgement: the right material, specified as a complete system, with someone who will solve problems on site.",
   p1="Huiying Int'l Business Co. is based in Xinzhuang District, New Taipei City, supplying construction waterproofing materials, exterior decorative coatings and epoxy flooring systems, together with the technical service to specify and install them.",
   p2="Beyond supply, we assist with material selection, sample panels and pre-start technical briefings. Waterproofing rarely fails because of one product; it fails in the interaction between layers and in the detail of installation.",
   rows=[("Company", "Huiying Int'l Business Co.　暉盈國際事業有限公司"),
         ("Tax ID", "%%TAX%%"), ("Telephone", "%%TEL1_INTL%%　%%TEL2_INTL%%"),
         ("Fax", "%%FAX_INTL%%"), ("Email", "%%EMAIL%%"),
         ("Address", "%%ADDR_EN_FULL%%"),
         ("Hours", "Monday to Friday, 08:30–17:30 (GMT+8)"),
         ("Business", "Supply and technical service of waterproofing materials, exterior coatings and epoxy flooring")],
   svc=[("Material specification", "A complete build-up of primer, membrane and topcoat matched to location, substrate, climate and programme."),
        ("Sample panels", "Sample panels for client and supervisor approval, used as the reference at handover inspection."),
        ("Supply and support", "Phased delivery to programme, pre-start briefings, and continuing technical assistance.")],
   lines=[("02", "Waterproofing materials", "waterproofing.html", "%%N_WP_EN%% series covering roofs, walls, wet rooms and basements"),
          ("03", "Stone-effect wall coating", "stone.html", "Five-layer build-up, seven-step sequence, %%N_SW%% colourways"),
          ("04", "Epoxy resin flooring", "epoxy.html", "%%N_EPX_EN%% systems for factories, cleanrooms, car parks and healthcare")]),
}


def build_about(lang):
    C, T_, LL = ABOUT[lang], T[lang], L[lang]
    d, u, up = dep(lang), ("../" if lang == "en" else ""), pfx(lang)
    path = f"/{up}about.html"
    rows = "".join(f'<tr><td style="width:150px">{k}</td><td>{v}</td></tr>' for k, v in C["rows"])
    svc = "".join(f'<div class="row"><div class="k">{i+1:02d}</div><div class="v">'
                  f'<h3>{h}</h3><p style="margin-bottom:0">{p}</p></div></div>'
                  for i, (h, p) in enumerate(C["svc"]))
    lines = "".join(f'<a href="{u}{h}"><h3>{n}</h3>'
                    f'<span class="desc">{ds}</span><span class="go">→</span></a>'
                    for no, n, h, ds in C["lines"])
    o = [head(lang, C["title"], C["desc"], path, depth=d,
              ld=ld(crumb(lang, [(T_["nav"][0][0], f"/{up}"), (C["h1"], path)]))),
         titleblock(lang, "about.html"),
         masthead(lang, "about.html", depth=d),
         f'''
<div class="head">
  <div class="page">
    <span class="tag">{C["tag"]}</span>
    <h1>{C["h1"]}</h1>
    <p class="lead">{C["lead"]}</p>
  </div>
</div>

<section class="band">
  <div class="page" style="display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:start">
    <div>
      <p style="color:var(--ink-2);margin-bottom:18px">{C["p1"]}</p>
      <p style="color:var(--ink-2)">{C["p2"]}</p>
      <div style="margin-top:34px;max-width:460px">{plate(u + "assets/img/photo/hero-1.jpg", T_["photo"], "PH-41")}</div>
    </div>
    <div class="tbl-wrap"><table class="tbl">{rows}</table></div>
  </div>
</section>

<section class="band grey">
  <div class="page">
    <div class="cap"><div class="no">{LL["svc"]}</div><h2>{LL["svc"]}</h2></div>
    <div class="schedule">{svc}</div>
  </div>
</section>

<section class="band">
  <div class="page">
    <div class="cap"><div class="no">{LL["lines"]}</div><h2>{LL["lines"]}</h2></div>
    <div class="index">{lines}</div>
  </div>
</section>''',
         ask_band(lang, depth=d),
         foot(lang, depth=d)]
    write(up + "about.html", "\n".join(o))


# ══════════════════════════════════ 詢價單

CONTACT = {
 "zh": dict(title="詢價與洽詢｜暉盈國際事業有限公司｜新北市新莊區",
   desc="暉盈國際事業有限公司聯絡方式與工程詢價。電話 %%TEL1%%、%%TEL2%%，地址%%ADDR_ZH%%。",
   tag="詢價單", h1="詢價與洽詢",
   lead="提供部位、基材、面積與預計施工時間，我們會回覆材料配套建議與報價。若已有圖說或規範，也可直接寄到我們信箱。",
   fields=[("01", "公司／單位名稱", "company", "text", "例：○○營造股份有限公司", True),
           ("02", "聯絡人", "person", "text", "", True),
           ("03", "聯絡電話", "phone", "tel", "", True),
           ("04", "電子信箱", "email", "email", "", False),
           ("05", "詢問項目", "topic", "select", "", False),
           ("06", "施作部位／面積／工期", "detail", "textarea",
            "例：新北市某案屋頂 850 m²，既有 PU 面層老化，預計 9 月中進場。", False)],
   opts=["防水材料", "外牆仿石塗料", "環氧樹脂地坪", "樣板施作", "其他"],
   info_h="公司資訊", staff_h="業務窗口",
   info=[("公司", "暉盈國際事業有限公司"), ("統一編號", "%%TAX%%"),
         ("電話", "%%TEL1%%　%%TEL2%%"), ("傳真", "%%FAX%%"),
         ("電子信箱", "%%EMAIL%%"),
         ("地址", "%%ADDR_ZH_FULL%%"),
         ("洽詢時間", "週一至週五 08:30–17:30")],
   staff=[("陳偉源", "0931-133-448"), ("王苡菖", "0915-007-915")]),
 "en": dict(title="Contact and Enquiry｜Huiying Int'l Business Co.｜New Taipei City",
   desc="Contact details and project enquiry form. Tel %%TEL1_INTL%%. %%ADDR_EN%%.",
   tag="Enquiry form", h1="Contact and enquiry",
   lead="Tell us the location, substrate, area and expected start date, and we will return a material specification and quotation. Drawings can be emailed directly.",
   fields=[("01", "Company", "company", "text", "", True),
           ("02", "Contact name", "person", "text", "", True),
           ("03", "Telephone", "phone", "tel", "", True),
           ("04", "Email", "email", "email", "", False),
           ("05", "Subject", "topic", "select", "", False),
           ("06", "Location / area / programme", "detail", "textarea",
            "e.g. 850 m² roof in New Taipei City, existing PU membrane degraded, start mid-September.", False)],
   opts=["Waterproofing materials", "Stone-effect wall coating", "Epoxy flooring", "Sample panel", "Other"],
   info_h="Company details", staff_h="Sales contacts",
   info=[("Company", "Huiying Int'l Business Co."), ("Tax ID", "%%TAX%%"),
         ("Telephone", "%%TEL1_INTL%%　%%TEL2_INTL%%"), ("Fax", "%%FAX_INTL%%"),
         ("Email", "%%EMAIL%%"),
         ("Address", "%%ADDR_EN_FULL%%"),
         ("Hours", "Monday to Friday, 08:30–17:30 (GMT+8)")],
   staff=[("Chen Wei-yuan", "+886-931-133-448"), ("Wang Yi-chang", "+886-915-007-915")]),
}


def build_contact(lang):
    C, T_, LL = CONTACT[lang], T[lang], L[lang]
    d, up = dep(lang), pfx(lang)
    path = f"/{up}contact.html"
    flds = []
    for no, label, name, kind, ph, req in C["fields"]:
        r = " required" if req else ""
        if kind == "select":
            ctl = f'<select name="{name}">' + "".join(f"<option>{o}</option>" for o in C["opts"]) + "</select>"
        elif kind == "textarea":
            ctl = f'<textarea name="{name}" placeholder="{ph}"></textarea>'
        else:
            ctl = f'<input name="{name}" type="{kind}" placeholder="{ph}"{r}>'
        cls = "fld full" if kind == "textarea" else "fld"
        flds.append(f'<div class="{cls}"><label for="{name}"><i>{no}</i>{label}</label>{ctl}</div>')
    info = "".join(f'<tr><td style="width:120px">{k}</td><td>{v}</td></tr>' for k, v in C["info"])
    staff = "".join(f'<tr><td style="width:120px">{k}</td><td class="num" style="font-size:16px">{v}</td></tr>'
                    for k, v in C["staff"])
    cp = {"@context": "https://schema.org", "@type": "ContactPage", "url": SITE + path,
          "name": C["h1"], "about": {"@id": SITE + "/#organization"}}
    o = [head(lang, C["title"], C["desc"], path, depth=d,
              ld=ld(crumb(lang, [(T_["nav"][0][0], f"/{up}"), (C["h1"], path)]), cp)),
         titleblock(lang, "contact.html"),
         masthead(lang, "contact.html", depth=d),
         f'''
<div class="head">
  <div class="page">
    <span class="tag">{C["tag"]}</span>
    <h1>{C["h1"]}</h1>
    <p class="lead">{C["lead"]}</p>
  </div>
</div>

<section class="band">
  <div class="page contact-2col">
    <form class="form-sheet" id="enq">
      <div class="form-hd"><b>{LL["form"]}</b><span>{LL["formno"]}</span></div>
      <div class="fields">{"".join(flds)}</div>
      <div class="form-ft">
        <small>{LL["note"]}</small>
        <div class="send-acts">
          <button class="btn" type="submit">{LL["send"]}</button>
          <button class="btn line" type="button" id="enqMail">{LL["send_alt"]}</button>
        </div>
        <button class="linkbtn" type="button" id="enqCopy" data-done="{LL["copied"]}">{LL["copy"]}</button>
      </div>
    </form>
    <div>
      <h2 style="font-size:19px;margin-bottom:16px">{C["info_h"]}</h2>
      <div class="tbl-wrap"><table class="tbl">{info}</table></div>
    </div>
  </div>
</section>''',
         foot(lang, depth=d).replace('<script src=', f'''<script>
(function () {{
  var TO = '%%EMAIL%%';
  var f = document.getElementById('enq');

  function pack() {{
    return {{
      subject: '[{LL["form"]}] ' + f.topic.value + ' - ' + f.company.value,
      body: [
        '{C["fields"][0][1]}: ' + f.company.value,
        '{C["fields"][1][1]}: ' + f.person.value,
        '{C["fields"][2][1]}: ' + f.phone.value,
        '{C["fields"][3][1]}: ' + f.email.value,
        '{C["fields"][4][1]}: ' + f.topic.value, '',
        '{C["fields"][5][1]}:', f.detail.value
      ].join('\\n')
    }};
  }}

  // Gmail 網頁版撰寫視窗（新分頁開啟，不影響原本填的內容）
  f.addEventListener('submit', function (e) {{
    e.preventDefault();
    if (!f.reportValidity()) return;
    var m = pack();
    window.open('https://mail.google.com/mail/?view=cm&fs=1&tf=1&to=' + encodeURIComponent(TO)
      + '&su=' + encodeURIComponent(m.subject)
      + '&body=' + encodeURIComponent(m.body), '_blank', 'noopener');
  }});

  // 電腦內建的郵件軟體（Outlook、Mail 等）
  document.getElementById('enqMail').addEventListener('click', function () {{
    if (!f.reportValidity()) return;
    var m = pack();
    window.location.href = 'mailto:' + TO + '?subject=' + encodeURIComponent(m.subject)
      + '&body=' + encodeURIComponent(m.body);
  }});

  // 複製全文，貼到 LINE、公司信箱或任何地方
  document.getElementById('enqCopy').addEventListener('click', function () {{
    var b = this, m = pack(), txt = m.subject + '\\n\\n' + m.body + '\\n\\n{{TO_LABEL}}: ' + TO;
    var done = function () {{
      var old = b.textContent;
      b.textContent = b.dataset.done;
      setTimeout(function () {{ b.textContent = old; }}, 1800);
    }};
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(txt).then(done, done);
    }} else {{
      var t = document.createElement('textarea');
      t.value = txt; document.body.appendChild(t); t.select();
      try {{ document.execCommand('copy'); }} catch (err) {{}}
      document.body.removeChild(t); done();
    }}
  }});
}})();
</script>
<script src=''').replace("{TO_LABEL}", "收件信箱" if lang == "zh" else "Send to")]
    write(up + "contact.html", "\n".join(o))


def build_404():
    import re as _re
    _h = head("zh", "查無此圖｜暉盈國際事業有限公司", "找不到這個頁面。", "/404.html", depth=0).replace(
            '<meta name="robots" content="index, follow, max-image-preview:large">',
            '<meta name="robots" content="noindex, follow">')
    # 404 沒有英文對應頁，移除 hreflang 交叉宣告
    _h = _re.sub(r'\n?<link rel="alternate" hreflang="[^"]*"[^>]*>', '', _h)
    _h = _re.sub(r'\n?<link rel="canonical"[^>]*>', '', _h)  # noindex 頁不需要 canonical
    o = [_h,
         titleblock("zh", "index.html", extra="查無此圖"),
         masthead("zh", "", depth=0),
         '''
<div class="head lg">
  <div class="page" style="text-align:center">
    <span class="tag">404</span>
    <h1 style="max-width:none">查無此圖</h1>
    <p class="lead" style="margin:0 auto">網址可能已經變更或輸入有誤。可以從下列圖號繼續，或直接與我們聯絡。</p>
    <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;margin-top:30px">
      <a class="btn" href="/index.html">回封面</a>
      <a class="btn line" href="/waterproofing.html">防水材料</a>
      <a class="btn line" href="/stone.html">仿石塗料</a>
      <a class="btn line" href="/epoxy.html">環氧地坪</a>
      <a class="btn line" href="/contact.html">詢價單</a>
    </div>
  </div>
</div>''',
         foot("zh", depth=0)]
    write("404.html", "\n".join(o))


def build_sitemap():
    import datetime
    D = datetime.date.today().isoformat()
    zh = [("/", "1.0", "monthly"), ("/waterproofing.html", "0.9", "monthly"),
          ("/stone.html", "0.9", "monthly"), ("/epoxy.html", "0.9", "monthly"),
          ("/roof-waterproofing.html", "0.9", "monthly"),
          ("/bathroom-waterproofing.html", "0.9", "monthly"),
          ("/basement-waterproofing.html", "0.9", "monthly"),
          ("/exterior-wall-coating.html", "0.9", "monthly"),
          ("/parking-floor.html", "0.9", "monthly"),
          ("/insights/", "0.8", "weekly")]
    # 專欄文章依 content/ 實際存在的文章產生（中英文以相同代稱對應）
    slugs = sorted({a["slug"] for l in ("zh", "en") for a in ART[l]},
                   key=lambda x: min(a["date"] for l in ("zh", "en") for a in ART[l] if a["slug"] == x))
    has = {l: {a["slug"] for a in ART[l]} for l in ("zh", "en")}
    zh += [(f"/insights/{x}.html", "0.7", "monthly", x) for x in slugs]
    zh += [("/about.html", "0.6", "yearly"), ("/contact.html", "0.8", "yearly")]
    enp = lambda p: "/en/" if p == "/" else "/en" + p
    o = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
         '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for p, pri, fq, *slug in zh:
        langs = [l for l in ("zh", "en") if not slug or slug[0] in has[l]]
        for loc, isz in ((p, True), (enp(p), False)):
            if ("zh" if isz else "en") not in langs:
                continue
            alt = []
            if "zh" in langs:
                alt.append(f'    <xhtml:link rel="alternate" hreflang="zh-Hant" href="{SITE}{p}"/>')
            if "en" in langs:
                alt.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}{enp(p)}"/>')
            alt.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{p if "zh" in langs else enp(p)}"/>')
            o += ['  <url>', f'    <loc>{SITE}{loc}</loc>', *alt,
                  f'    <lastmod>{D}</lastmod>', f'    <changefreq>{fq}</changefreq>',
                  f'    <priority>{pri if isz else round(float(pri)-0.1,1)}</priority>', '  </url>']
    o.append('</urlset>')
    write("sitemap.xml", "\n".join(o) + "\n")
    from build_all import PREVIEW
    tpl = lambda f: open(os.path.join(os.path.dirname(__file__), f), encoding="utf-8").read()
    write("robots.txt", "User-agent: *\nDisallow: /\n" if PREVIEW else tpl("robots_template.txt"))
    write("llms.txt", tpl("llms_template.txt"))


def copy_static():
    """dist/ 重新建立；靜態檔（圖片、字型、CSS、JS、後台）原樣複製"""
    import shutil
    from build_all import OUT
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for name in ("assets", "admin"):
        shutil.copytree(os.path.join(ROOT, name), os.path.join(OUT, name))
    for name in ("favicon.ico", "site.webmanifest", "_headers"):
        shutil.copy2(os.path.join(ROOT, "static", name), os.path.join(OUT, name))


if __name__ == "__main__":
    copy_static()
    n = 0
    for lang in ("zh", "en"):
        build_home(lang); n += 1
        build_waterproofing(lang); n += 1
        build_stone(lang); n += 1
        build_epoxy(lang); n += 1
        for s in SOL[lang]:
            build_solution(lang, s, SOL[lang]); n += 1
        build_insights_index(lang); n += 1
        for i, a in enumerate(ART[lang]):
            build_article(lang, a, i, ART[lang]); n += 1
        build_about(lang); n += 1
        build_contact(lang); n += 1
    build_404(); n += 1
    build_sitemap()
    print(f"完成：{n} 頁 ＋ sitemap ＋ robots ＋ llms → dist/" + ("（預覽版，已設 noindex）" if __import__("build_all").PREVIEW else ""))

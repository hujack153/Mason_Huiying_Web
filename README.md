# 暉盈國際事業有限公司 官方網站

https://huiyingmaterials.com

純靜態 HTML／CSS／JS，繁體中文為主，`/en/` 為英文版。推送到 GitHub `main` 後由 Cloudflare 自動部署，沒有建置步驟。

## 本機預覽

直接用瀏覽器開 `index.html`，不需連外網。

## 檔案結構

```
website-v2/
├── index.html …………………… 首頁
├── waterproofing.html ……… 建築防水材料
├── stone.html ……………………… 外牆多彩仿石塗料
├── epoxy.html ……………………… 環氧樹脂地坪
├── roof-waterproofing.html     屋頂防水
├── bathroom-waterproofing.html 浴室防水
├── basement-waterproofing.html 地下室防水
├── exterior-wall-coating.html  外牆塗裝
├── parking-floor.html ……… 停車場地坪
├── insights/ ………………………… 技術專欄與 3 篇文章
├── about.html／contact.html／404.html
├── en/ ……………………………………… 英文版（與中文版一一對應，共 15 頁）
├── assets/
│   ├── css/site.css
│   ├── js/nav.js ……………… 手機選單、輪播、語言切換、hover 預載
│   ├── js/products*.js ……… 產品與色卡資料
│   ├── font/ …………………… 數值用字型（num-500／700）
│   └── img/{brand,photo,floor,stone}
├── sitemap.xml／robots.txt／llms.txt／site.webmanifest
└── _build/ ……………………………… 頁面產生器（本機專用，不上傳）
```

## 重新產生頁面

HTML 由 Python 產生，請改內容來源後重新產生，不要直接改 HTML：

```bash
cd _build
python3 build_all3.py
```

| 來源 | 內容 |
|---|---|
| `data_zh.json`／`data_en.json` | 防水系列、仿石工序與色卡 |
| `content_epoxy.py` | 環氧地坪八套系統 |
| `content_sol_zh.py`／`content_sol_en.py` | 五個施作部位頁 |
| `content_zh.py`／`content_en.py` | 技術專欄文章 |
| `figures.py` | 剖面圖 SVG |
| `layout2.py` | 頁首、版頭、頁尾 |
| `build_all.py`／`build_all2.py`／`build_all3.py` | 頁面產生器（執行第三支即可） |

## 設計規格

| 項目 | 選擇 |
|---|---|
| 字型 | 系統黑體：PingFang TC → Microsoft JhengHei → Noto Sans CJK TC；數值用自行託管的窄體（約 8–10 KB） |
| 紙面 | `#EFE9DB`，內容帶為白色 |
| 石板藍 | `#24506B`／`#2F6183` |
| 暖灰點綴 | `#D8CFB4`（僅用在深色面） |
| 墨色 | `#131C26` |
| 按鈕與框線 | 實心 2px |

主視覺是各施作部位的剖面大樣圖；首頁以三張剖面圖輪播（每 6 秒，可手動切換，`prefers-reduced-motion` 時停用）。

## 效能

- 跨頁淡入轉場（`@view-transition`），不支援的瀏覽器自動忽略
- 滑鼠移到站內連結時預載目標頁
- 版頭大圖使用 preload 與 `fetchpriority="high"`，單張約 240–260 KB

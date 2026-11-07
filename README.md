# 暉盈國際事業有限公司 官方網站

https://huiyingmaterials.com

防水材料、外牆多彩仿石塗料、環氧樹脂地坪的產品網站。純靜態 HTML／CSS／JS，繁體中文為主，英文版在 `/en/`。

## 結構

```
├── index.html                 首頁
├── waterproofing.html         建築防水材料
├── stone.html                 外牆多彩仿石塗料
├── epoxy.html                 環氧樹脂地坪
├── roof-waterproofing.html    屋頂防水
├── bathroom-waterproofing.html  浴室防水
├── basement-waterproofing.html  地下室防水
├── exterior-wall-coating.html   外牆塗裝
├── parking-floor.html         停車場地坪
├── insights/                  技術專欄
├── about.html · contact.html · 404.html
├── en/                        英文版（與中文版一一對應）
├── assets/
│   ├── css/site.css
│   ├── js/nav.js              選單、輪播、語言切換
│   ├── js/products*.js        產品與色卡資料
│   ├── font/
│   └── img/{brand,photo,floor,stone}
└── sitemap.xml · robots.txt · llms.txt · site.webmanifest
```

## 部署

推送到 `main` 後由 Cloudflare 自動部署。本機預覽直接用瀏覽器開 `index.html`。

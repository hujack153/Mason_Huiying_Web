# website-v2 — 製圖語彙版本

暉盈國際事業有限公司網站的**設計改版方案**，與現行的 `website/` 平行存在。

## 這個資料夾不會被推上 GitHub

`website/` 才是 git repo（`website/.git`）。
`website-v2/` 在 repo 之外，你在 `website/` 裡做任何 commit 或 push 都不會動到這裡。

要正式採用時，再把 `website-v2/` 的內容複製進 `website/` 即可。

## 怎麼看

直接用瀏覽器開 `index.html`。不需連外網。

## 字型：固定系統黑體

全站標題與內文固定使用**系統黑體**：PingFang TC（蘋方）→ Microsoft JhengHei（微軟正黑體）→ Noto Sans CJK TC。不下載任何中文字檔，載入零閃爍。先前的字體切換器已依需求移除。

唯一自行託管的字檔是數值用的 `assets/font/num-500.woff2` / `num-700.woff2`（各約 8–10 KB，只含拉丁字母數字），用於表格與圖面標註對齊。

## 換頁速度

- **跨頁淡入轉場**：`@view-transition { navigation: auto }`，支援的瀏覽器（Chrome、Edge、Safari 18+）換頁時淡入 0.16 秒，不支援的瀏覽器自動忽略
- **hover 預載**：滑鼠移上任何站內連結即 `prefetch` 目標頁，點擊時 HTML 已在快取（file:// 本機瀏覽時自動停用）
- **版頭大圖 preload ＋ fetchpriority="high"**，且已壓縮（每張約 240–260 KB）
- `prefers-reduced-motion` 會停用轉場與動畫

## 設計依據

| 項目 | 選擇 | 理由 |
|---|---|---|
| 標題 | 系統黑體（固定） | 零下載、零閃爍 |
| 數值 | Nimbus Sans Narrow 子集（8 KB） | 窄體，對應圖面的數字註記；表格數字對齊 |
| 紙面 | `#EFE9DB`（內容帶為白色） | 主要內容區塊一律白色，避免顏色過多 |
| 石板藍 | `#24506B` / `#2F6183` | 大版頭、深色帶、反白剖面圖、hover 與強調 |
| 暖灰點綴 | `#D8CFB4` | 只出現在深色面上：眉標、剖面圖標記層 |
| 墨色 | `#131C26` | 按鈕與框線都用實心 2px，不用淡灰 |
| 紅色 | 已全部移除 | 全站不再使用紅色，配色收斂為 藍／墨／白／暖灰 四色 |

**簽名元素**：剖面大樣圖。每個施作部位頁都有對應的剖面（屋頂層疊、浴室翻邊、地下室迎水／背水面、外牆、地坪）；首頁用的是**反白曬圖版**（深底白線），載入時逐層疊起。

**圖號**：頁首的圖紙標題欄（第 N 張／版次）已依需求移除；技術文章仍編 TN-01～03。

## 檔案結構

```
website-v2/
├── index.html …………………… 第 01 張　封面
├── waterproofing.html ……… 第 02 張　防水材料
├── stone.html ……………………… 第 03 張　外牆仿石塗料
├── epoxy.html ……………………… 第 04 張　環氧樹脂地坪
├── roof-waterproofing.html … 第 05 張
├── bathroom-waterproofing.html
├── basement-waterproofing.html
├── exterior-wall-coating.html
├── parking-floor.html
├── insights/ ………………………… 第 10 張　技術專欄＋3 篇
├── about.html ……………………… 第 11 張
├── contact.html …………………… 第 12 張　詢價單
├── 404.html
├── en/ ……………………………………… 英文版全套 15 頁
├── assets/
│   ├── css/site.css
│   ├── js/nav.js ……………… 手機選單＋輪播＋語言切換＋hover 預載
│   └── img/{brand,photo,floor,stone}
└── _build/ ……………………………… 產生器（不需部署）
```

## 重新產生

改內容後執行：

```bash
cd _build
python3 build_all3.py
```

內容來源：

- `data_zh.json` / `data_en.json` — 防水系列、仿石工序與色卡（由 `assets/js/products*.js` 匯出）
- `content_epoxy.py` — 環氧地坪八套系統
- `content_sol_zh.py` / `_en.py` — 五個施作部位頁（含各自的照片與圖號）
- `content_zh.py` / `content_en.py` — 技術專欄文章
- `figures.py` — 剖面圖 SVG 產生器（含反白曬圖版）
- `layout2.py` — 頁首、深色大版頭、頁尾
- `build_all.py` / `build_all2.py` / `build_all3.py` — 頁面產生器，執行第三支即可

## 與現行版本的差異

- 首頁版頭：**三張無字剖面圖輪播**（標準三層構成／七層塗裝結構／地坪三層構成），每 6 秒自動換張、可手動滑動或點圓點，滑鼠移入即暫停；`prefers-reduced-motion` 停用自動輪播
- 三個產品線頁與五個部位頁的版頭，統一改為**深色底圖大版頭**：照片為底、大標在左、反白剖面圖（含圖名與大樣編號）在右
- 八個內容頁的主資訊帶統一為**白色**，FAQ 一律白色，部位索引一律深藍
- 系列明細／配套材料改為**收合式**：收起時只露出編號、名稱、小標與一句簡述，點＋號展開產品特性與規格；跳轉選單點擊會自動展開對應列
- 仿石頁：配套材料上方加**五項跳轉選單**；「施工設備需求」移到頁尾成**補充**區塊；色卡改為**緊湊格狀**（不列色號，hover 或點擊顯示色名）
- **已移除**：首頁「材料配置圖」眉標、產品卡與部位索引的編號、施作實景照片牆、環氧頁「地坪實景」、仿石頁「塗裝工序」
- 按鈕全部**實心／2px 實線邊框**；hover 有明確回饋（卡片上浮、照片微放大、箭頭位移）
- 詢價表單為**紙本詢價單**；技術文章有 **§ 條號邊欄**，「正確做法」以藍色左線標記

## 驗證狀態

最近一次全站檢查（31 頁）：

- HTML 標籤結構：無異常
- 站內連結：0 個死連結
- hreflang 對應頁：全部存在
- JSON-LD：46 段，全數可解析
- 每頁皆有 title／description／canonical／og:image
- sitemap：30 個 URL

## 尚待處理

- 圖片版權：建築照、色卡與地坪照取自原廠型錄，正式對外使用前應更換為自有照片或取得授權
- 那些照片不是暉盈的實績，長期應換成自有案場照

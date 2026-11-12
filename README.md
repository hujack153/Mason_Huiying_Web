# 暉盈國際事業有限公司 官方網站

https://huiyingmaterials.com

防水材料、外牆多彩仿石塗料、環氧樹脂地坪的產品網站。新版後台位於 `/admin/`，提供首頁文字與防水產品編輯、線上草稿和發布。內容存成 `content/` 裡的 JSON；部署時由 `_build/` 的產生器輸出靜態 HTML 到 `dist/`。

## 結構

```
├── content/                 網站內容（後台編輯的就是這裡）
│   ├── company.json         公司資訊：電話、地址、Email、統編
│   ├── zh/ · en/
│   │   ├── waterproofing.json   防水材料系列
│   │   ├── stone.json           仿石塗層產品與色卡
│   │   ├── epoxy.json           環氧地坪：基礎層＋系統、FAQ
│   │   ├── articles/*.json      技術專欄（檔名＝網址代稱）
│   │   └── solutions/*.json     五個施作部位頁
├── _build/                  產生器（Python 3，只用標準函式庫）
│   ├── build_all3.py        主程式：python3 _build/build_all3.py
│   ├── content.py           讀取 content/，處理 **粗體**、代號、數量
│   ├── build_all*.py · layout2.py · figures.py
│   ├── robots_template.txt · llms_template.txt
├── admin/                   原有 Decap CMS 與設定，建置後保留在 /admin/classic.html
├── cms-auth/                Worker 登入、線上內容 API、GitHub 草稿與發布
├── assets/                  CSS、JS、字型、圖片（後台上傳的圖在 assets/img/uploads/）
├── static/                  原樣複製到 dist/ 的檔案：favicon、manifest、_headers
├── wrangler.jsonc           Cloudflare Workers 設定（公開目錄 dist/）
└── dist/                    建置輸出，不進 git
```

## 修改流程

1. 打開 https://huiyingmaterials.com/admin/ ，輸入原本的後台密碼。
2. 在「修改首頁文字」或「管理防水產品」編輯。草稿會自動儲存，可切換中英文與預覽。
3. 按「檢查修改並發布」，補齊提示的內容後按「確認發布到網站」。
4. 後台將相關內容一次提交到 `main`，顯示建置進度。看到「網站已更新」後可開啟網站檢查。

「其他內容管理」保留文章、仿石、環氧、施作部位及公司資訊的原有後台，使用原有登入和發布流程。

線上版沿用 Cloudflare Secrets `ADMIN_PASSWORD`、`GITHUB_TOKEN`。新版登入以 HttpOnly Cookie 保存 8 小時的簽章工作階段，GitHub 憑證由 Worker 使用。線上草稿加密後存於 `cms/studio` 分支的 `.cms/studio-draft.json`，發布只更新允許的四份內容檔。多個視窗共用同一份草稿，版本不同時提示重新確認。更換後台密碼或 GitHub 憑證後，尚未發布的舊草稿可能需要重設。

建置時會產生新版工作台、四份預覽模板和網站版本標記。所有 `/admin` 頁面與 API 經 Worker 驗證登入後提供。測試可在建置後執行 `node --test cms-auth/studio.test.mjs cms-auth/studio-ui.test.mjs`。

改程式時直接推到 `main` 即可（推了就上線）。

## 本機建置

```bash
python3 _build/build_all3.py      # 輸出到 dist/
python3 -m http.server -d dist    # http://localhost:8000
```

## 本機內容工作台

Windows 可雙擊 `start-studio.cmd`。也可從此目錄執行 `python -B _build/studio.py`，再開啟 [本機工作台](http://127.0.0.1:8765)。工作台開啟時請保留啟動視窗。

1. 在「修改首頁文字」選擇中文或英文。點預覽裡金色框線的主標或引言，即可修改。停止輸入後會自動儲存，畫面顯示儲存時間。
2. 在「管理防水產品」搜尋、新增、編輯或排序系列。產品代號自動產生。新增產品可先填中文，按「儲存並返回清單」直接存成草稿，之後再補英文。產品可從預覽隱藏並恢復顯示。
3. 按「檢查修改並送審」查看變更摘要與待補欄位，可直接前往補齊。內容檢查通過後按「下載送審檔」，把檔案交給網站維護人員確認與發布。

「復原上一步」可復原本次開啟工作台後的最近操作。產品編輯視窗關閉前會提醒尚未儲存的修改。草稿若與更新後的來源衝突，可先下載備份再重新載入。

線上原有 `/admin` 的「首頁文字」也提供中英文主標、引言表單及文字預覽，依原有的發布流程處理。

草稿保存在 Git 忽略的 `.ai-local/studio-draft.json`，工作台只在本機開啟。預覽使用官網模板，首頁輪播等依賴前端腳本的互動以靜態方式呈現。

## 規則

- **不要直接改 `dist/` 或在 GitHub 網頁上改 HTML**，下次建置會被蓋掉。
- 公司資訊只改 `content/company.json`。頁尾、聯絡頁、JSON-LD、`llms.txt` 會自動同步，英文版電話會自動轉成 +886 格式。
- 「X 大系列」「X 組色系」「X 套系統」依資料筆數自動計算。環氧頁自己的標題與引言（`epoxy.json`）是手寫的，系統數量變動時要一起改。
- 環氧 `id` 為 `primer`、`body` 的兩項是基礎層，不計入系統數量。
- 仿石塗層增減時，`_build/figures.py` 的剖面圖要手動更新。
- 文章中英文版用相同檔名對應。只有單一語言時，另一語言的切換連結會指向該語言的專欄列表。
- 非 `main` 分支的建置（`WORKERS_CI_BRANCH` 不是 `main`）會自動整站加上 `noindex`，`robots.txt` 擋全站。
- `/admin/` 以 `noindex` 標頭、`robots.txt` 排除。登入密碼與 GitHub 金鑰是 Cloudflare 上的 Secret：`ADMIN_PASSWORD`、`GITHUB_TOKEN`（`hujack153` 建立的 fine-grained token，只授權本 repo，Contents 讀寫）。

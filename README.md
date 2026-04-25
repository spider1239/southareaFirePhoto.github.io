# 南區小火照片網頁

這是一個部署在 GitHub Pages 的靜態相簿網站，用來展示 `2026/04/18&19 南區小火` 的照片成果。

線上網址：

- `https://spider1239.github.io/southareaFirePhoto.github.io/`

## 專案結構

- `index.html`
  - 網站主頁面結構
- `public/app.js`
  - 前端互動邏輯
  - 分類導覽、照片列表、Lightbox、分享、下載、回頂部按鈕
- `public/styles.css`
  - 桌機版與手機版樣式
- `src/`
  - 各分類縮圖來源
- `drive-file-map.json`
  - 照片檔名與 Google Drive 檔案 ID 的對應表
- `gallery-data.json`
  - 線上模式使用的相簿資料
- `gallery-data.js`
  - 本機 `file://` 開啟時使用的嵌入資料
- `tools/build-gallery.py`
  - 掃描縮圖與 Drive 對應表後，產出相簿資料檔

## 目前資料策略

- GitHub repo 內只保留頁面、程式碼與縮圖
- 原圖不放在 repo 內
- 原圖預覽、單張下載、分享連結都來自 Google Drive
- 網站不會即時掃描 Google Drive，而是讀取建置後的 `gallery-data.json` / `gallery-data.js`

## 更新照片時的正確流程

只要有以下變動，就要重新建置並 push：

- 新增照片
- 刪除照片
- 改檔名
- 改分類名稱
- 換新的 Google Drive 檔案
- 改縮圖
- 改 `drive-file-map.json`

建議固定照這個流程執行：

1. 先整理本機縮圖
   - 更新 `src/分類名稱/縮略圖/...`
   - 縮圖檔名需和原圖對應檔名一致

2. 更新 Google Drive 原圖
   - 若重新上傳造成新的檔案 ID，後面一定要更新 `drive-file-map.json`

3. 更新 `drive-file-map.json`
   - 讓網站知道分類、檔名與 Drive file ID 的對應關係

4. 重新產生相簿資料

```bash
python3 /Users/user/Documents/Codex/2026-04-19-finder-plugin-computer-use-openai-bundled/gallery-site/tools/build-gallery.py
```

5. 本機檢查
   - 確認分類是否正確
   - 確認縮圖是否正確
   - 確認 Lightbox 是否開到正確原圖
   - 確認下載 / 分享是否正常

6. push 到 GitHub

```bash
git -C /Users/user/Documents/Codex/2026-04-19-finder-plugin-computer-use-openai-bundled/gallery-site add -A
git -C /Users/user/Documents/Codex/2026-04-19-finder-plugin-computer-use-openai-bundled/gallery-site commit -m "更新相簿資料"
git -C /Users/user/Documents/Codex/2026-04-19-finder-plugin-computer-use-openai-bundled/gallery-site push -u origin main
```

7. 等 GitHub Pages 更新
   - 通常等待 1 到 3 分鐘
   - 再重新整理網站確認結果

## 重要注意事項

- 網站不是直接讀取 Google Drive 資料夾內容，而是讀取建置後的靜態清單
- 如果只是修改雲端資料夾內容，但沒有重建資料檔，網站通常不會自動反映新照片
- 如果只是覆蓋同一個 Google Drive 檔案內容，且檔案 ID 沒變，理論上可能繼續顯示，但仍可能受快取影響，不建議把這當正式流程

## 後續可優化方向

### 1. 分享與下載穩定性

- 針對 `navigator.clipboard` 失敗情況補更完整的 fallback
- 針對不同手機瀏覽器優化下載體驗
- 若未來空間允許，可改成提供 zip 壓縮檔下載

### 2. 導覽體驗

- 加入目前所在分類高亮
- 加入關鍵字搜尋
- 加入分類篩選或快速定位

### 3. 效能優化

- 將縮圖進一步壓縮成更一致的尺寸
- 對大型分類採分段渲染或延遲掛載
- 改善初始載入時的快取策略

### 4. 維護流程優化

- 製作自動更新 `drive-file-map.json` 的工具
- 製作一鍵建置與一鍵 push 腳本
- 增加更新照片用的檢查清單，避免漏改縮圖或 Drive ID

### 5. 視覺與互動優化

- 增加目前分類定位提示
- 增加更完整的按鈕狀態與動效
- 視需要再微調手機縮圖牆與 Lightbox 介面

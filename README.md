# 成品相簿網站

這是一個靜態相簿網站，會讀取來源資料夾：

- `/Users/user/Pictures/Photo/20260418_南區小火/成品`

## 內容

- 依子資料夾作為分類
- 顯示每張照片
- 支援單張下載
- 支援分享；若瀏覽器不支援原生分享，會改為複製照片連結
- 開發模式可從頁面頂部按鈕重新讀取照片

## 使用方式

1. 重新掃描並產生相簿資料：

```bash
python3 /Users/user/Documents/Codex/2026-04-19-finder-plugin-computer-use-openai-bundled/gallery-site/tools/build-gallery.py
```

2. 啟動可支援頁面內「重新讀取照片」按鈕的本機伺服器：

```bash
python3 /Users/user/Documents/Codex/2026-04-19-finder-plugin-computer-use-openai-bundled/gallery-site/tools/dev-server.py
```

3. 用瀏覽器開啟：

- `http://127.0.0.1:8000`

## 部署前

部署到 GitHub Pages 前，請移除首頁頂部的「重新讀取照片」按鈕與其對應前端程式，因為純靜態主機無法直接執行本機 Python 腳本。

# 🌐 File Translator Tool

Ứng dụng desktop dịch tài liệu đa định dạng, hỗ trợ dịch **giữ nguyên cấu trúc file** (Excel, Word, CSV), giao diện dark-mode hiện đại xây dựng bằng PyQt6.

---

## ✨ Tính năng

| Tính năng | Mô tả |
|---|---|
| **Đa định dạng** | Hỗ trợ `.txt` `.docx` `.pdf` `.csv` `.xlsx` |
| **Giữ cấu trúc file** | Excel: dịch từng cell, giữ nguyên tất cả sheet — Word: giữ paragraph — CSV: giữ cột hàng |
| **Batch translation** | Thêm nhiều file vào hàng đợi, dịch 1 lần, tải về dạng ZIP |
| **Paste Text mode** | Dán text trực tiếp vào app, không cần file |
| **Chọn ngôn ngữ nguồn** | Tự động phát hiện hoặc chọn thủ công |
| **API Provider** | Google Translate (miễn phí) hoặc MyMemory (miễn phí) |
| **Custom Glossary** | Định nghĩa thuật ngữ không được dịch tự động theo ý muốn |
| **Translation History** | Lưu lịch sử các lần dịch |
| **Split View** | Xem song song bản gốc và bản dịch |
| **Chỉnh sửa bản dịch** | Sửa tay bản dịch trước khi tải về |
| **Cancel** | Dừng quá trình dịch giữa chừng |
| **Drag & Drop** | Kéo thả file vào cửa sổ ứng dụng |

### Ngôn ngữ hỗ trợ
Tiếng Việt · English · 日本語 · 中文 · 한국어 · Français · Deutsch · Español · Italiano · Português · Русский · العربية · हिन्दी · ภาษาไทย · Indonesia

---

## 🗂 Cấu trúc dự án

```
tool-translate/
├── main.py                # Giao diện chính (PyQt6)
├── file_handler.py        # Đọc/ghi và dịch có cấu trúc cho từng định dạng
├── translator_module.py   # Engine dịch (Google Translate / MyMemory)
├── glossary_manager.py    # Quản lý thuật ngữ tùy chỉnh
├── history_manager.py     # Lưu lịch sử dịch
├── requirements.txt       # Danh sách thư viện cần cài
└── README.md
```

---

## ⚙️ Yêu cầu hệ thống

- **Python** 3.10 trở lên (khuyến nghị 3.12+)
- **Kết nối internet** (để gọi API dịch)
- **Windows / macOS / Linux**

---

## 🚀 Cài đặt

### 1. Clone hoặc tải source code

```bash
git clone <repo-url>
cd tool-translate
```

Hoặc tải ZIP về và giải nén.

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

| Thư viện | Chức năng |
|---|---|
| `PyQt6` | Giao diện đồ họa |
| `deep-translator` | Gọi API Google Translate / MyMemory |
| `python-docx` | Đọc/ghi file `.docx` |
| `pypdf` | Đọc file `.pdf` |
| `pandas` + `openpyxl` | Đọc/ghi file `.xlsx` và `.csv` |
| `langdetect` | Tự động phát hiện ngôn ngữ nguồn |

---

## ▶️ Chạy ứng dụng

```bash
python main.py
```

---

## 📖 Hướng dẫn sử dụng

### Dịch một file
1. **Kéo thả** file vào vùng upload, hoặc nhấn **Browse File…**
2. Chọn **Target** (ngôn ngữ đích) và **Source** (ngôn ngữ gốc, mặc định Auto-detect)
3. Chọn **Provider**: `Google Translate (Free)` hoặc `MyMemory (Free)`
4. Nhấn **⚡ Translate File**
5. Xem kết quả trong tab **🔤 Translated** — có thể **sửa tay** trước khi lưu
6. Nhấn **💾 Download Translated File** để tải về

### Dịch nhiều file (Batch)
1. Nhấn **+ Batch** để thêm nhiều file vào hàng đợi
2. Nhấn **📦 Translate All (N files)**
3. Theo dõi tiến trình từng file trong Batch Queue (⏳ → 🔄 → ✅)
4. Nhấn **📦 Download All as ZIP** để tải tất cả về một lần

### Dịch text dán trực tiếp
1. Chuyển sang tab **📝 Paste Text** trong phần Preview
2. Dán nội dung cần dịch vào
3. Nhấn **⚡ Translate Text**

### Split View (xem song song)
- Nhấn **⇔ Split View** để xem bản gốc và bản dịch cạnh nhau

### Glossary (thuật ngữ tùy chỉnh)
- Nhấn **🔤 Glossary** trên thanh tiêu đề
- Thêm cặp **Source Term → Target Translation**
- Các thuật ngữ này sẽ được áp dụng trước khi gửi lên API → đảm bảo dịch đúng tên riêng, thuật ngữ kỹ thuật
- Glossary lưu tại: `~/.file_translator_glossary.json`

### Lịch sử dịch
- Nhấn **📋 History** để xem toàn bộ lịch sử
- Lưu tại: `~/.file_translator_history.json` (tối đa 200 mục)

---

## 📝 Lưu ý

- **PDF**: do giới hạn kỹ thuật, file PDF được lưu dưới dạng `.txt` sau khi dịch (không tái tạo layout PDF)
- **Google Translate Free**: không cần API key, nhưng có thể bị rate limit nếu dịch quá nhiều liên tục — hãy chờ vài giây rồi thử lại
- **MyMemory Free**: giới hạn ~5.000 ký tự/ngày với anonymous, tăng lên 50.000/ngày nếu đăng ký email tại [mymemory.translated.net](https://mymemory.translated.net)
- **Glossary**: sử dụng cơ chế placeholder — term nguồn được thay bằng mã đặc biệt trước khi dịch, sau đó khôi phục đúng term đích

---

## 🛠 Troubleshooting

| Lỗi | Cách xử lý |
|---|---|
| `Translation Error` | Kiểm tra kết nối internet, đợi vài giây rồi thử lại |
| `Error Reading File` | File bị hỏng hoặc định dạng không được hỗ trợ |
| App mở rồi đóng ngay | Đảm bảo đã cài đủ thư viện: `pip install -r requirements.txt` |
| Bản dịch trống | File không có text (PDF scan ảnh không thể trích xuất text) |
| `NotValidLength` | Đoạn văn quá dài — tool tự xử lý, thử lại nếu vẫn lỗi |

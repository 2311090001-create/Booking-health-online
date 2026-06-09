# 🏥 Đặt Lịch Hẹn Khám Sức Khỏe Online có tích hợp AI

Ứng dụng web đặt lịch hẹn khám bệnh trực tuyến, xây dựng bằng **Python + Streamlit**.

---

## 📁 Cấu trúc thư mục

```
gemini-web/
├── app.py                  # File chạy ứng dụng chính
├── send_reminders.py       # Script gửi email nhắc lịch hàng ngày
├── requirements.txt        # Danh sách thư viện cần cài
├── README.md               # Tài liệu này
│
├── src/                    # Mã nguồn
│   ├── __init__.py
│   ├── config.py           # Cấu hình app (email, đường dẫn, ...)
│   ├── data_manager.py     # Xử lý dữ liệu CSV
│   ├── email_service.py    # Gửi email qua Gmail SMTP
│   └── ui_components.py    # Các component giao diện Streamlit
│
└── data/                   # Dữ liệu CSV
    ├── patients.csv        # Bệnh nhân
    ├── clinics.csv         # Phòng khám
    ├── doctors.csv         # Bác sĩ
    ├── symptoms.csv        # Triệu chứng → Chuyên khoa
    └── appointments.csv    # Lịch hẹn
```

---

## 🚀 Hướng dẫn cài đặt và chạy (từng bước cho người mới)

### Bước 1: Kiểm tra Python

Mở **Command Prompt** (Windows) và chạy:
```bash
python --version
```
Nếu thấy `Python 3.x.x` → OK. Nếu chưa có, tải tại https://python.org/downloads

---

### Bước 2: Di chuyển vào thư mục dự án

```bash
cd C:\Users\An\Documents\gemini-web
```

---

### Bước 3: (Tùy chọn) Tạo môi trường ảo

**Khuyến nghị** tạo môi trường ảo để tránh xung đột thư viện:

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt (Windows)
venv\Scripts\activate

# Kích hoạt (Mac/Linux)
source venv/bin/activate
```

---

### Bước 4: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

Chờ vài phút để cài xong. Nếu thấy `Successfully installed` → OK.

---

### Bước 5: Chạy ứng dụng

```bash
streamlit run app.py
```

Trình duyệt sẽ tự động mở tại **http://localhost:8501** 🎉

---

## ⚙️ Cấu hình Gmail SMTP để gửi email

> **Lưu ý:** Bước này cần thiết để ứng dụng gửi được email xác nhận và nhắc lịch.
> Nếu chưa cấu hình, ứng dụng vẫn chạy bình thường nhưng không gửi được email.

### Bước 1: Bật xác thực 2 bước cho Gmail

1. Truy cập: https://myaccount.google.com/security
2. Cuộn xuống phần **"Đăng nhập vào Google"**
3. Bật **"Xác minh 2 bước"** (nếu chưa bật)

### Bước 2: Tạo App Password (Mật khẩu ứng dụng)

1. Truy cập: https://myaccount.google.com/apppasswords
2. Chọn **"Chọn ứng dụng"** → **"Thư"**
3. Chọn **"Chọn thiết bị"** → **"Khác (tên tùy chỉnh)"** → Nhập `HealthApp`
4. Bấm **"Tạo"**
5. **Copy** mật khẩu 16 ký tự được tạo ra (dạng: `xxxx xxxx xxxx xxxx`)

### Bước 3: Cập nhật file `src/config.py`

Mở file `src/config.py` và thay đổi:

```python
EMAIL_CONFIG = {
    "smtp_server":    "smtp.gmail.com",
    "smtp_port":      587,
    "sender_email":   "gmail_cua_ban@gmail.com",      # ← Thay bằng Gmail của bạn
    "sender_password": "xxxx xxxx xxxx xxxx",         # ← Thay bằng App Password 16 ký tự
    "sender_name":    "Hệ Thống Đặt Lịch Khám",
}
```

> ⚠️ **Bảo mật:** Không chia sẻ file `config.py` chứa App Password cho người khác.

---

## 📋 Hướng dẫn sử dụng ứng dụng

### Đặt lịch khám (4 bước đơn giản):

| Bước | Thao tác |
|------|----------|
| 1 | Nhập triệu chứng (VD: "đau ngực", "đau răng") |
| 2 | Chọn chuyên khoa phù hợp |
| 3 | Chọn bác sĩ → Nhập thông tin → Chọn ngày giờ |
| 4 | Nhận xác nhận + Email tự động |

### Xem lịch hẹn của mình:
- Vào menu **"Lịch hẹn của tôi"**
- Nhập email để tra cứu

### Gửi nhắc lịch:
- Vào menu **"Gửi nhắc lịch"**
- Bấm nút để gửi email nhắc cho tất cả bệnh nhân có lịch ngày mai

---

## 🤖 Gửi nhắc lịch tự động hàng ngày

### Windows (Task Scheduler):

1. Mở **Task Scheduler** (tìm trong Start Menu)
2. Bấm **"Create Basic Task"**
3. Đặt tên: `Healthcare Reminder`
4. Trigger: **Daily** lúc **08:00**
5. Action: **Start a program**
   - Program: `python`
   - Arguments: `C:\Users\An\Documents\gemini-web\send_reminders.py`
6. Bấm Finish

### Kiểm tra thủ công:

```bash
python send_reminders.py
```

Kết quả được ghi vào file `reminder_log.txt`.

---

## 🛠️ Xử lý lỗi thường gặp

| Lỗi | Giải pháp |
|-----|-----------|
| `ModuleNotFoundError: streamlit` | Chạy `pip install -r requirements.txt` |
| `SMTPAuthenticationError` | Kiểm tra email và App Password trong `config.py` |
| `streamlit: command not found` | Thử `python -m streamlit run app.py` |
| Ứng dụng không mở trình duyệt | Mở thủ công: http://localhost:8501 |
| Dữ liệu không lưu | Kiểm tra quyền ghi file trong thư mục `data/` |

---

## 📞 Thông tin liên hệ

Dự án được xây dựng phục vụ mục đích học tập.
Nếu cần hỗ trợ, vui lòng liên hệ qua email cấu hình trong `config.py`.

---

*© 2026 Hệ Thống Đặt Lịch Khám Sức Khỏe Online – Phiên bản 1.0*

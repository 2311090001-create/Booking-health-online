"""
Cấu hình ứng dụng Đặt lịch hẹn khám sức khỏe online
"""

import os

# ============================================================
# CẤU HÌNH ĐƯỜNG DẪN FILE DỮ LIỆU
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

PATIENTS_CSV    = os.path.join(DATA_DIR, "patients.csv")
CLINICS_CSV     = os.path.join(DATA_DIR, "clinics.csv")
DOCTORS_CSV     = os.path.join(DATA_DIR, "doctors.csv")
SYMPTOMS_CSV    = os.path.join(DATA_DIR, "symptoms.csv")
APPOINTMENTS_CSV = os.path.join(DATA_DIR, "appointments.csv")

# ============================================================
# CẤU HÌNH EMAIL GMAIL SMTP
# (Thay bằng thông tin Gmail của bạn)
# ============================================================
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "maithanhan2005@gmail.com",       # <-- Thay email của bạn vào đây
    "sender_password": "nzok uavm ytjo ywvp",  # <-- Thay App Password Gmail vào đây
    "sender_name": "Hệ Thống Đặt Lịch Khám",
}

# ============================================================
# CẤU HÌNH THỜI GIAN
# ============================================================
TIME_SLOT_DURATION_MINUTES = 30   # Mỗi khung giờ 30 phút
SUGGEST_SLOTS_COUNT        = 3    # Số khung giờ gợi ý khi bị trùng

# Khung giờ làm việc
WORKING_HOURS_START = "07:00"
WORKING_HOURS_END   = "17:00"

# ============================================================
# CẤU HÌNH GIAO DIỆN
# ============================================================
APP_TITLE       = "🏥 Đặt Lịch Khám Sức Khỏe Online"
APP_DESCRIPTION = "Hệ thống đặt lịch hẹn khám bệnh trực tuyến - Nhanh chóng, Tiện lợi, Tin cậy"
APP_ICON        = "🏥"
PRIMARY_COLOR   = "#2563EB"

# ============================================================
# CẤU HÌNH ADMIN
# ============================================================
ADMIN_CONFIG = {
    "username": "admin",
    "password": "admin123",   # Đổi mật khẩu trước khi deploy thật
}

# ============================================================
# CẤU HÌNH GEMINI AI
# ============================================================
# Khi deploy Streamlit Cloud: thêm vào Secrets với key "GEMINI_API_KEY"
# Khi chạy local: dùng giá trị bên dưới
GEMINI_API_KEY = "AQ.Ab8RN6LTjtLaMmdrImAKfKsxvqOFh5Pac8-urhmWOBaozT9-PQ"


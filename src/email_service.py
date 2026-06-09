"""
Module gửi email qua Gmail SMTP
- Gửi email xác nhận lịch khám
- Gửi email nhắc lịch (reminder)
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime, timedelta

from src.config import EMAIL_CONFIG


# ============================================================
# HÀM GỬI EMAIL CƠ BẢN
# ============================================================

def send_email(to_email: str, subject: str, html_body: str) -> tuple[bool, str]:
    """
    Gửi email HTML qua Gmail SMTP.
    
    Args:
        to_email:  Địa chỉ email người nhận.
        subject:   Tiêu đề email.
        html_body: Nội dung email dạng HTML.
    
    Returns:
        (True, "") nếu thành công,
        (False, thông báo lỗi) nếu thất bại.
    """
    cfg = EMAIL_CONFIG
    
    # Kiểm tra cấu hình email
    if cfg["sender_email"] == "your_email@gmail.com":
        return (False, "⚠️ Chưa cấu hình email. Vui lòng chỉnh sửa file src/config.py")
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = formataddr((cfg["sender_name"], cfg["sender_email"]))
        msg["To"]      = to_email
        
        # Gắn phần HTML
        part = MIMEText(html_body, "html", "utf-8")
        msg.attach(part)
        
        # Kết nối SMTP và gửi
        with smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(cfg["sender_email"], cfg["sender_password"])
            server.sendmail(cfg["sender_email"], to_email, msg.as_string())
        
        return (True, "")
    
    except smtplib.SMTPAuthenticationError:
        return (False, "❌ Sai email/mật khẩu Gmail. Hãy kiểm tra lại App Password.")
    except smtplib.SMTPException as e:
        return (False, f"❌ Lỗi SMTP: {str(e)}")
    except Exception as e:
        return (False, f"❌ Lỗi không xác định: {str(e)}")


# ============================================================
# EMAIL XÁC NHẬN LỊCH KHÁM
# ============================================================

def build_confirmation_email(
    patient_name: str,
    doctor_name: str,
    specialty: str,
    clinic_name: str,
    appointment_date: str,
    appointment_time: str,
    appointment_id: str,
    consultation_fee: float = 0,
) -> str:
    """Tạo nội dung HTML cho email xác nhận lịch khám"""
    
    fee_str = f"{consultation_fee:,.0f} VNĐ" if consultation_fee else "Liên hệ phòng khám"
    
    # Định dạng ngày giờ đẹp hơn
    try:
        dt = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
        date_display = dt.strftime("%A, ngày %d tháng %m năm %Y")
        time_display = dt.strftime("%H:%M")
    except Exception:
        date_display = appointment_date
        time_display = appointment_time
    
    html = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Xác nhận lịch khám</title>
</head>
<body style="margin:0;padding:0;background-color:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f4f8;padding:30px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
          
          <!-- HEADER -->
          <tr>
            <td style="background:linear-gradient(135deg,#1d4ed8,#3b82f6);padding:40px 40px 30px;text-align:center;">
              <p style="margin:0;font-size:48px;">🏥</p>
              <h1 style="margin:10px 0 0;color:#ffffff;font-size:24px;font-weight:700;">
                Xác Nhận Lịch Khám Bệnh
              </h1>
              <p style="margin:8px 0 0;color:#bfdbfe;font-size:14px;">
                Mã lịch hẹn: <strong style="color:#ffffff;">#{appointment_id}</strong>
              </p>
            </td>
          </tr>
          
          <!-- BODY -->
          <tr>
            <td style="padding:40px;">
              <p style="color:#374151;font-size:16px;margin:0 0 8px;">
                Xin chào, <strong>{patient_name}</strong> 👋
              </p>
              <p style="color:#6b7280;font-size:14px;margin:0 0 30px;">
                Lịch khám của bạn đã được xác nhận thành công. Vui lòng đọc kỹ thông tin dưới đây:
              </p>
              
              <!-- INFO BOX -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#eff6ff;border-radius:12px;border-left:4px solid #3b82f6;margin-bottom:24px;">
                <tr>
                  <td style="padding:24px;">
                    <table width="100%" cellpadding="8" cellspacing="0">
                      <tr>
                        <td style="color:#6b7280;font-size:13px;width:40%;">📅 Ngày khám</td>
                        <td style="color:#111827;font-size:14px;font-weight:600;">{date_display}</td>
                      </tr>
                      <tr>
                        <td style="color:#6b7280;font-size:13px;">⏰ Giờ khám</td>
                        <td style="color:#111827;font-size:14px;font-weight:600;">{time_display}</td>
                      </tr>
                      <tr>
                        <td style="color:#6b7280;font-size:13px;">👨‍⚕️ Bác sĩ</td>
                        <td style="color:#111827;font-size:14px;font-weight:600;">{doctor_name}</td>
                      </tr>
                      <tr>
                        <td style="color:#6b7280;font-size:13px;">🩺 Chuyên khoa</td>
                        <td style="color:#111827;font-size:14px;font-weight:600;">{specialty}</td>
                      </tr>
                      <tr>
                        <td style="color:#6b7280;font-size:13px;">🏥 Phòng khám</td>
                        <td style="color:#111827;font-size:14px;font-weight:600;">{clinic_name}</td>
                      </tr>
                      <tr>
                        <td style="color:#6b7280;font-size:13px;">💰 Phí khám</td>
                        <td style="color:#059669;font-size:14px;font-weight:700;">{fee_str}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
              
              <!-- LƯU Ý -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#fef9c3;border-radius:12px;border-left:4px solid #f59e0b;margin-bottom:24px;">
                <tr>
                  <td style="padding:20px 24px;">
                    <p style="margin:0;color:#92400e;font-size:13px;font-weight:600;">⚠️ Lưu ý quan trọng:</p>
                    <ul style="margin:8px 0 0;padding-left:18px;color:#78350f;font-size:13px;line-height:1.8;">
                      <li>Vui lòng đến trước giờ hẹn <strong>15 phút</strong> để làm thủ tục</li>
                      <li>Mang theo <strong>CMND/CCCD</strong> hoặc thẻ bảo hiểm y tế</li>
                      <li>Nếu cần hủy lịch, vui lòng thông báo trước <strong>24 giờ</strong></li>
                    </ul>
                  </td>
                </tr>
              </table>
              
              <p style="color:#6b7280;font-size:13px;text-align:center;margin:0;">
                Chúc bạn sức khỏe! 💪<br>
                Mọi thắc mắc vui lòng liên hệ hotline hoặc trả lời email này.
              </p>
            </td>
          </tr>
          
          <!-- FOOTER -->
          <tr>
            <td style="background:#f9fafb;padding:20px;text-align:center;border-top:1px solid #e5e7eb;">
              <p style="margin:0;color:#9ca3af;font-size:12px;">
                © 2026 Hệ Thống Đặt Lịch Khám Sức Khỏe Online<br>
                Email này được gửi tự động, vui lòng không reply trực tiếp.
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    return html


def send_confirmation_email(
    to_email: str,
    patient_name: str,
    doctor_name: str,
    specialty: str,
    clinic_name: str,
    appointment_date: str,
    appointment_time: str,
    appointment_id: str,
    consultation_fee: float = 0,
) -> tuple[bool, str]:
    """
    Gửi email xác nhận lịch khám cho bệnh nhân.
    """
    subject = f"✅ Xác nhận lịch khám - {appointment_date} lúc {appointment_time} | Mã: #{appointment_id}"
    html_body = build_confirmation_email(
        patient_name=patient_name,
        doctor_name=doctor_name,
        specialty=specialty,
        clinic_name=clinic_name,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        appointment_id=appointment_id,
        consultation_fee=consultation_fee,
    )
    return send_email(to_email, subject, html_body)


# ============================================================
# EMAIL NHẮC LỊCH (REMINDER)
# ============================================================

def build_reminder_email(
    patient_name: str,
    doctor_name: str,
    specialty: str,
    clinic_name: str,
    appointment_date: str,
    appointment_time: str,
    appointment_id: str,
) -> str:
    """Tạo nội dung HTML cho email nhắc lịch khám"""
    
    try:
        dt = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
        date_display = dt.strftime("ngày %d/%m/%Y")
        time_display = dt.strftime("%H:%M")
    except Exception:
        date_display = appointment_date
        time_display = appointment_time
    
    html = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Nhắc lịch khám</title>
</head>
<body style="margin:0;padding:0;background-color:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f4f8;padding:30px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
          
          <!-- HEADER -->
          <tr>
            <td style="background:linear-gradient(135deg,#7c3aed,#a855f7);padding:40px;text-align:center;">
              <p style="margin:0;font-size:48px;">⏰</p>
              <h1 style="margin:10px 0 0;color:#ffffff;font-size:24px;font-weight:700;">
                Nhắc Nhở Lịch Khám Bệnh
              </h1>
              <p style="margin:8px 0 0;color:#e9d5ff;font-size:14px;">
                Mã lịch hẹn: <strong style="color:#ffffff;">#{appointment_id}</strong>
              </p>
            </td>
          </tr>
          
          <!-- BODY -->
          <tr>
            <td style="padding:40px;">
              <p style="color:#374151;font-size:16px;margin:0 0 16px;">
                Xin chào, <strong>{patient_name}</strong> 👋
              </p>
              <p style="color:#6b7280;font-size:14px;margin:0 0 24px;">
                Đây là email nhắc nhở: Bạn có lịch khám bệnh vào <strong style="color:#7c3aed;">{date_display} lúc {time_display}</strong>.
                Đừng quên nhé! 🩺
              </p>
              
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#faf5ff;border-radius:12px;border-left:4px solid #7c3aed;margin-bottom:24px;">
                <tr>
                  <td style="padding:24px;">
                    <table width="100%" cellpadding="8" cellspacing="0">
                      <tr>
                        <td style="color:#6b7280;font-size:13px;width:40%;">📅 Ngày khám</td>
                        <td style="color:#111827;font-size:14px;font-weight:600;">{date_display}</td>
                      </tr>
                      <tr>
                        <td style="color:#6b7280;font-size:13px;">⏰ Giờ khám</td>
                        <td style="color:#111827;font-size:14px;font-weight:600;">{time_display}</td>
                      </tr>
                      <tr>
                        <td style="color:#6b7280;font-size:13px;">👨‍⚕️ Bác sĩ</td>
                        <td style="color:#111827;font-size:14px;font-weight:600;">{doctor_name}</td>
                      </tr>
                      <tr>
                        <td style="color:#6b7280;font-size:13px;">🩺 Chuyên khoa</td>
                        <td style="color:#111827;font-size:14px;font-weight:600;">{specialty}</td>
                      </tr>
                      <tr>
                        <td style="color:#6b7280;font-size:13px;">🏥 Phòng khám</td>
                        <td style="color:#111827;font-size:14px;font-weight:600;">{clinic_name}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
              
              <p style="color:#6b7280;font-size:13px;text-align:center;margin:0;">
                Hẹn gặp bạn tại phòng khám! 🌟
              </p>
            </td>
          </tr>
          
          <!-- FOOTER -->
          <tr>
            <td style="background:#f9fafb;padding:20px;text-align:center;border-top:1px solid #e5e7eb;">
              <p style="margin:0;color:#9ca3af;font-size:12px;">
                © 2026 Hệ Thống Đặt Lịch Khám Sức Khỏe Online
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    return html


def send_reminder_email(
    to_email: str,
    patient_name: str,
    doctor_name: str,
    specialty: str,
    clinic_name: str,
    appointment_date: str,
    appointment_time: str,
    appointment_id: str,
) -> tuple[bool, str]:
    """
    Gửi email nhắc lịch khám cho bệnh nhân.
    Thường được gọi 1 ngày trước lịch khám.
    """
    subject = f"⏰ Nhắc lịch khám - {appointment_date} lúc {appointment_time} | #{appointment_id}"
    html_body = build_reminder_email(
        patient_name=patient_name,
        doctor_name=doctor_name,
        specialty=specialty,
        clinic_name=clinic_name,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        appointment_id=appointment_id,
    )
    return send_email(to_email, subject, html_body)


# ============================================================
# HÀM TIỆN ÍCH GỬI EMAIL NHẮC LỊCH HÀNG LOẠT
# (Thiết kế sẵn – chạy bằng scheduler/cron job)
# ============================================================

def send_reminders_for_tomorrow(appointments_df, doctors_df, clinics_df, patients_df) -> list[dict]:
    """
    Gửi email nhắc lịch cho tất cả bệnh nhân có lịch khám vào ngày mai.
    Hàm này được thiết kế để chạy mỗi ngày qua scheduler/cron job.
    
    Args:
        appointments_df: DataFrame lịch hẹn
        doctors_df:      DataFrame bác sĩ
        clinics_df:      DataFrame phòng khám
        patients_df:     DataFrame bệnh nhân
    
    Returns:
        Danh sách kết quả gửi email
    """
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    results = []
    
    tomorrow_appts = appointments_df[appointments_df["appointment_date"] == tomorrow]
    
    for _, row in tomorrow_appts.iterrows():
        # Lấy thông tin bệnh nhân
        patient = patients_df[patients_df["patient_id"] == row["patient_id"]]
        if patient.empty:
            continue
        patient = patient.iloc[0]
        
        # Lấy thông tin bác sĩ
        doctor = doctors_df[doctors_df["doctor_id"] == row["doctor_id"]]
        if doctor.empty:
            continue
        doctor = doctor.iloc[0]
        
        # Lấy thông tin phòng khám
        clinic = clinics_df[clinics_df["clinic_id"] == doctor["clinic_id"]]
        clinic_name = clinic.iloc[0]["clinic_name"] if not clinic.empty else "N/A"
        
        success, error = send_reminder_email(
            to_email=patient["email"],
            patient_name=patient["patient_name"],
            doctor_name=doctor["doctor_name"],
            specialty=doctor["specialty"],
            clinic_name=clinic_name,
            appointment_date=row["appointment_date"],
            appointment_time=row["appointment_time"],
            appointment_id=row["appointment_id"],
        )
        
        results.append({
            "appointment_id": row["appointment_id"],
            "patient_email":  patient["email"],
            "success":        success,
            "error":          error,
        })
    
    return results

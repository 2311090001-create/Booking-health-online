"""
Module các component UI tái sử dụng cho Streamlit
Lưu ý: KHÔNG dùng <table> trong st.markdown() — dùng native Streamlit components thay thế.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta


def render_header():
    """Hiển thị header ứng dụng"""
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1d4ed8 0%,#3b82f6 50%,#06b6d4 100%);padding:2.5rem 2rem;border-radius:16px;margin-bottom:2rem;text-align:center;box-shadow:0 10px 40px rgba(37,99,235,0.3);">
        <h1 style="color:white;margin:0;font-size:2.2rem;font-weight:800;letter-spacing:-0.5px;">🏥 Đặt Lịch Khám Sức Khỏe Online</h1>
        <p style="color:#bfdbfe;margin:0.75rem 0 0;font-size:1.05rem;">Tìm bác sĩ · Đặt lịch · Nhận xác nhận ngay lập tức</p>
    </div>
    """, unsafe_allow_html=True)


def render_step_indicator(current_step: int, total_steps: int = 4):
    """Hiển thị thanh tiến trình các bước"""
    steps = ["Triệu chứng", "Chọn bác sĩ", "Đặt lịch", "Hoàn thành"]
    cols = st.columns(total_steps)

    for i, (col, label) in enumerate(zip(cols, steps), 1):
        with col:
            if i < current_step:
                color, text_color = "#22c55e", "#166534"
            elif i == current_step:
                color, text_color = "#3b82f6", "#1e40af"
            else:
                color, text_color = "#d1d5db", "#9ca3af"

            st.markdown(f"""
            <div style="text-align:center;padding:8px;">
                <div style="width:36px;height:36px;border-radius:50%;background:{color};color:white;display:flex;align-items:center;justify-content:center;margin:0 auto 6px;font-weight:700;font-size:14px;">{i}</div>
                <small style="color:{text_color};font-weight:600;font-size:12px;">{label}</small>
            </div>
            """, unsafe_allow_html=True)


def render_doctor_card(row: dict, index: int) -> bool:
    """Hiển thị card thông tin bác sĩ. Returns True nếu được chọn."""
    fee  = f"{row.get('consultation_fee', 0):,.0f}" if row.get('consultation_fee') else "N/A"
    dist = f"{row.get('distance_km', 0):.1f}" if row.get('distance_km') else "N/A"
    exp  = row.get('experience_years', 'N/A')

    if isinstance(exp, (int, float)):
        if exp >= 10:   badge_color, badge_label = "#22c55e", "⭐ Cao cấp"
        elif exp >= 5:  badge_color, badge_label = "#3b82f6", "🔷 Giỏi"
        else:           badge_color, badge_label = "#f59e0b", "🌱 Mới"
    else:
        badge_color, badge_label = "#6b7280", "N/A"

    st.markdown(f"""
    <div style="background:white;border:1px solid #e5e7eb;border-radius:12px;padding:1.2rem 1.4rem;margin-bottom:0.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
            <div>
                <h4 style="margin:0;color:#111827;font-size:1rem;font-weight:700;">👨‍⚕️ {row.get('doctor_name','N/A')}</h4>
                <p style="margin:4px 0 0;color:#6b7280;font-size:0.85rem;">🩺 {row.get('specialty','N/A')} &nbsp;·&nbsp; 🏥 {row.get('clinic_name','N/A')}</p>
            </div>
            <span style="background:{badge_color}22;color:{badge_color};border:1px solid {badge_color}44;border-radius:20px;padding:3px 12px;font-size:12px;font-weight:600;">{badge_label} · {exp} năm</span>
        </div>
        <div style="display:flex;gap:16px;margin-top:12px;padding-top:12px;border-top:1px solid #f3f4f6;">
            <span style="color:#374151;font-size:0.85rem;">📍 Cách <strong>{dist} km</strong></span>
            <span style="color:#059669;font-size:0.85rem;">💰 <strong>{fee} VNĐ</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return st.button(
        f"📅 Chọn {row.get('doctor_name','Bác sĩ')}",
        key=f"select_doctor_{index}_{row.get('doctor_id','')}",
        use_container_width=True,
        type="primary",
    )


def render_success_banner(
    appointment_id: str,
    patient_name: str,
    doctor_name: str,
    specialty: str,
    clinic_name: str,
    appointment_date: str,
    appointment_time: str,
    consultation_fee: float = 0,
    email_sent: bool = False,
):
    """Hiển thị thông tin lịch hẹn thành công — dùng hoàn toàn native Streamlit."""
    fee_str = f"{consultation_fee:,.0f} VNĐ" if consultation_fee else "Liên hệ phòng khám"

    try:
        dt = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
        date_display = dt.strftime("%d/%m/%Y")
        time_display = dt.strftime("%H:%M")
    except Exception:
        date_display = appointment_date
        time_display = appointment_time

    # --- Banner tiêu đề ---
    st.markdown("""
    <div style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:2px solid #86efac;border-radius:16px;padding:1.5rem;text-align:center;margin-bottom:1rem;">
        <div style="font-size:3rem;">🎉</div>
        <h2 style="color:#166534;margin:8px 0 4px;font-size:1.5rem;">Đặt lịch thành công!</h2>
    </div>
    """, unsafe_allow_html=True)

    # --- Mã lịch hẹn ---
    st.markdown(f'<div style="text-align:center;margin-bottom:1rem;"><span style="background:#dcfce7;color:#166534;font-size:1rem;font-weight:700;padding:6px 20px;border-radius:20px;border:1px solid #86efac;">Mã lịch hẹn: #{appointment_id}</span></div>', unsafe_allow_html=True)

    # --- Chi tiết lịch hẹn: mỗi dòng là 1 div hoàn chỉnh, độc lập ---
    rows_data = [
        ("👤", "Bệnh nhân",   patient_name,  "#111827"),
        ("📅", "Ngày khám",   date_display,  "#111827"),
        ("⏰", "Giờ khám",    time_display,  "#111827"),
        ("👨‍⚕️", "Bác sĩ",     doctor_name,   "#111827"),
        ("🩺", "Chuyên khoa", specialty,     "#111827"),
        ("🏥", "Phòng khám",  clinic_name,   "#111827"),
        ("💰", "Phí khám",    fee_str,       "#059669"),
    ]

    bg_colors = ["#ffffff", "#f9fafb"]
    for i, (icon, label, value, value_color) in enumerate(rows_data):
        bg = bg_colors[i % 2]
        col_l, col_v = st.columns([2, 3])
        with col_l:
            st.markdown(
                f'<div style="background:{bg};padding:8px 4px;font-size:13px;color:#6b7280;">{icon} {label}</div>',
                unsafe_allow_html=True
            )
        with col_v:
            st.markdown(
                f'<div style="background:{bg};padding:8px 4px;font-size:14px;font-weight:600;color:{value_color};">{value}</div>',
                unsafe_allow_html=True
            )

    # --- Trạng thái email ---
    if email_sent:
        st.success("📧 Email xác nhận đã được gửi đến hộp thư của bạn!")
    else:
        st.warning("⚠️ Không thể gửi email. Lịch hẹn vẫn được lưu thành công.")


def render_conflict_banner(
    doctor_name: str,
    appointment_date: str,
    appointment_time: str,
    suggestions: list[dict],
):
    """Hiển thị banner trùng lịch và gợi ý thay thế"""
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#fff7ed,#ffedd5);border:2px solid #fdba74;border-radius:16px;padding:1.5rem;margin:1rem 0;">
        <div style="font-size:2rem;margin-bottom:8px;">⚠️</div>
        <h3 style="color:#9a3412;margin:0 0 6px;">Lịch hẹn bị trùng!</h3>
        <p style="color:#c2410c;margin:0;font-size:0.9rem;"><strong>{doctor_name}</strong> đã có lịch khám lúc <strong>{appointment_time}</strong> ngày <strong>{appointment_date}</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    if suggestions:
        st.markdown("### 💡 Khung giờ thay thế được gợi ý:")
        cols = st.columns(len(suggestions))
        selected = None
        for i, (col, slot) in enumerate(zip(cols, suggestions)):
            with col:
                st.markdown(f"""
                <div style="background:white;border:2px solid #3b82f6;border-radius:12px;padding:1rem;text-align:center;margin-bottom:8px;">
                    <div style="font-size:1.5rem;">📅</div>
                    <div style="font-weight:700;color:#1e40af;margin:4px 0;">{slot['time']}</div>
                    <div style="font-size:12px;color:#6b7280;">{slot['date']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"✅ Chọn {slot['time']}", key=f"suggest_{i}_{slot['date']}_{slot['time']}", use_container_width=True):
                    selected = slot
        return selected
    return None


def render_info_card(title: str, value: str, icon: str = "📌", color: str = "#3b82f6"):
    """Hiển thị card thông tin nhỏ"""
    st.markdown(f"""
    <div style="background:{color}11;border:1px solid {color}33;border-radius:10px;padding:14px 16px;margin:4px 0;">
        <div style="font-size:12px;color:{color};font-weight:600;margin-bottom:3px;">{icon} {title}</div>
        <div style="font-size:15px;color:#111827;font-weight:700;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

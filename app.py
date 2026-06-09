"""
Ứng dụng Đặt Lịch Hẹn Khám Sức Khỏe Online
File chính chạy Streamlit

Chạy lệnh: streamlit run app.py
"""

import sys
import os

# Thêm thư mục gốc vào Python path để import được src/*
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta

from src.config import (
    APP_TITLE, APP_DESCRIPTION, APP_ICON,
    WORKING_HOURS_START, WORKING_HOURS_END,
    TIME_SLOT_DURATION_MINUTES, SUGGEST_SLOTS_COUNT,
    ADMIN_CONFIG,
)
from src.data_manager import (
    find_specialty_by_symptom,
    get_all_specialties,
    get_doctors_with_clinic_info,
    get_or_create_patient,
    check_appointment_conflict,
    suggest_alternative_slots,
    save_appointment,
    get_appointments_by_patient,
    get_doctor_info,
    load_patients,
    load_clinics,
    load_doctors,
    load_appointments,
)
from src.email_service import send_confirmation_email
from src.ui_components import (
    render_header,
    render_step_indicator,
    render_doctor_card,
    render_success_banner,
    render_conflict_banner,
    render_info_card,
)


# ============================================================
# CẤU HÌNH TRANG STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Đặt Lịch Khám Sức Khỏe Online",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS tùy chỉnh toàn cục
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Nền ứng dụng */
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0fdf4 100%);
        background-attachment: fixed;
    }

    /* ===== FIX MÀU CHỮ CHÍNH ===== */
    .main .block-container h1,
    .main .block-container h2,
    .main .block-container h3,
    .main .block-container h4,
    .main .block-container h5,
    .main .block-container h6 { color: #0f172a !important; font-weight: 700 !important; }

    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 { color: #0f172a !important; font-weight: 700 !important; }

    [data-testid="stMarkdownContainer"] p { color: #1e293b !important; }
    [data-testid="stMarkdownContainer"] li { color: #1e293b !important; }

    [data-testid="stWidgetLabel"] p,
    label { color: #0f172a !important; font-weight: 600 !important; }

    [data-testid="stMetricLabel"] p { color: #475569 !important; }
    [data-testid="stMetricValue"]   { color: #0f172a !important; }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span { color: #1e293b !important; }

    .stTextInput input { color: #0f172a !important; background: #ffffff !important; }
    details summary p,
    .streamlit-expanderHeader p { color: #0f172a !important; font-weight: 600 !important; }
    /* ================================ */

    /* Sidebar - giữ màu trắng */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e40af 0%, #1d4ed8 50%, #2563eb 100%);
        border-right: none;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 { color: #ffffff !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 { color: #ffffff !important; }
    /* Nút active (primary) trong sidebar: chữ trắng */
    section[data-testid="stSidebar"] button[kind="primary"] p { color: #ffffff !important; }
    /* Nút không active (secondary) trong sidebar: nền trắng → chữ xanh đậm */
    section[data-testid="stSidebar"] button[kind="secondary"] { background: rgba(255,255,255,0.92) !important; border: 1px solid rgba(255,255,255,0.5) !important; }
    section[data-testid="stSidebar"] button[kind="secondary"] p { color: #1e3a8a !important; font-weight: 600 !important; }
    section[data-testid="stSidebar"] button[kind="secondary"]:hover { background: rgba(255,255,255,1) !important; }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
        border: none;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37,99,235,0.35); }
    .stButton > button[kind="primary"] { background: linear-gradient(135deg, #1d4ed8, #3b82f6); color: white !important; }
    .stButton > button[kind="secondary"] { background: #ffffff; color: #374151 !important; border: 1px solid #d1d5db !important; }

    /* Input fields */
    .stTextInput > div > div > input,
    .stDateInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        background-color: #ffffff !important;
        color: #111827 !important;
    }
    .stTextInput > div > div > input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }

    .streamlit-expanderHeader { border-radius: 10px; font-weight: 600; background-color: #f8fafc !important; }
    hr { border: none; border-top: 2px solid #e5e7eb; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# KHỞI TẠO SESSION STATE
# ============================================================
def init_session_state():
    defaults = {
        "page":               "home",
        "step":               1,
        "symptom_input":      "",
        "matched_specialties": [],
        "selected_specialty": None,
        "doctors_df":         None,
        "selected_doctor":    None,
        "booking_result":     None,
        "suggestions":        [],
        "show_conflict":      False,
        "is_admin":           False,
        "chat_messages":      [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 1rem;">
        <div style="font-size:3rem;">🏥</div>
        <h2 style="color:white;margin:8px 0 4px;font-size:1.2rem;font-weight:800;">Đặt Lịch Khám</h2>
        <p style="color:#bfdbfe;font-size:0.8rem;margin:0;">Sức Khỏe Online</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📍 Menu chính")

    menu_options = {
        "🏠 Trang chủ":        "home",
        "📅 Đặt lịch khám":    "booking",
        "📋 Lịch hẹn của tôi": "my_appointments",
        "💬 Trợ lý AI":       "chat",
        "ℹ️ Hướng dẫn":        "guide",
    }

    for label, page_name in menu_options.items():
        is_active = st.session_state["page"] == page_name
        if st.button(
            label,
            key=f"nav_{page_name}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state["page"] = page_name
            if page_name != "booking":
                st.session_state["step"] = 1
                st.session_state["selected_doctor"] = None
                st.session_state["booking_result"] = None
                st.session_state["show_conflict"] = False
            st.rerun()

    st.divider()
    st.markdown("### 📊 Thống kê hệ thống")
    try:
        n_doctors  = len(load_doctors())
        n_clinics  = len(load_clinics())
        n_appts    = len(load_appointments())
        n_patients = len(load_patients())
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.15);border-radius:12px;padding:16px;">
            <div style="color:#bfdbfe;font-size:13px;margin-bottom:8px;">👨‍⚕️ Bác sĩ: <strong style="color:white;">{n_doctors}</strong></div>
            <div style="color:#bfdbfe;font-size:13px;margin-bottom:8px;">🏥 Phòng khám: <strong style="color:white;">{n_clinics}</strong></div>
            <div style="color:#bfdbfe;font-size:13px;margin-bottom:8px;">📅 Lịch hẹn: <strong style="color:white;">{n_appts}</strong></div>
            <div style="color:#bfdbfe;font-size:13px;">👥 Bệnh nhân: <strong style="color:white;">{n_patients}</strong></div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.warning("Không thể tải thống kê")

    st.divider()
    if st.session_state.get("is_admin"):
        st.markdown(
            "<p style='color:#bfdbfe;font-size:11px;text-align:center;margin-bottom:6px;'>⚙️ Đang đăng nhập Admin</p>",
            unsafe_allow_html=True,
        )
        if st.button("🔐 Vào trang Admin", key="nav_admin", use_container_width=True, type="primary"):
            st.session_state["page"] = "admin"
            st.rerun()
        if st.button("🚪 Đăng xuất Admin", key="admin_logout", use_container_width=True):
            st.session_state["is_admin"] = False
            st.session_state["page"] = "home"
            st.rerun()
    else:
        if st.button("🔐 Admin", key="nav_admin_login", use_container_width=True):
            st.session_state["page"] = "admin_login"
            st.rerun()


# ============================================================
# TRANG CHỦ
# ============================================================
def page_home():
    render_header()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:1.5rem;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.08);">
            <div style="font-size:2.5rem;margin-bottom:12px;">🔍</div>
            <h3 style="color:#1e40af;margin:0 0 8px;font-size:1rem;">Tìm Bác Sĩ</h3>
            <p style="color:#6b7280;font-size:0.85rem;margin:0;">Nhập triệu chứng, hệ thống tự động tìm chuyên khoa và bác sĩ phù hợp nhất</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:1.5rem;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.08);">
            <div style="font-size:2.5rem;margin-bottom:12px;">📅</div>
            <h3 style="color:#1e40af;margin:0 0 8px;font-size:1rem;">Đặt Lịch Ngay</h3>
            <p style="color:#6b7280;font-size:0.85rem;margin:0;">Chọn thời gian phù hợp, kiểm tra trùng lịch và xác nhận trong vài giây</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:1.5rem;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.08);">
            <div style="font-size:2.5rem;margin-bottom:12px;">📧</div>
            <h3 style="color:#1e40af;margin:0 0 8px;font-size:1rem;">Nhận Xác Nhận</h3>
            <p style="color:#6b7280;font-size:0.85rem;margin:0;">Email xác nhận và nhắc lịch tự động trước ngày khám</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("🚀 Bắt đầu đặt lịch ngay", use_container_width=True, type="primary"):
            st.session_state["page"] = "booking"
            st.session_state["step"] = 1
            st.rerun()

    st.markdown("---")
    st.markdown("### 🩺 Chuyên khoa phổ biến")
    specialties = get_all_specialties()

    spec_cols = st.columns(4)
    specialty_icons = {
        "Nội khoa": "💊", "Tim mạch": "❤️", "Nhi khoa": "👶",
        "Sản phụ khoa": "🤱", "Mắt": "👁️", "Răng hàm mặt": "🦷",
        "Da liễu": "🧴", "Thần kinh": "🧠", "Cơ xương khớp": "🦴",
        "Ngoại khoa": "🔪",
    }

    for i, spec in enumerate(specialties):
        with spec_cols[i % 4]:
            icon = specialty_icons.get(spec, "🩺")
            if st.button(f"{icon} {spec}", key=f"home_spec_{i}", use_container_width=True):
                st.session_state["page"] = "booking"
                st.session_state["step"] = 2
                st.session_state["selected_specialty"] = spec
                st.session_state["matched_specialties"] = [spec]
                st.session_state["doctors_df"] = get_doctors_with_clinic_info(spec)
                st.rerun()

    st.markdown("---")
    st.markdown("### 🏥 Phòng khám trong hệ thống")
    try:
        clinics_df = load_clinics()
        display_df = clinics_df[["clinic_name", "distance_km", "consultation_fee"]].copy()
        display_df.columns = ["Tên phòng khám", "Khoảng cách (km)", "Phí khám (VNĐ)"]
        display_df = display_df.sort_values("Khoảng cách (km)")
        display_df["Phí khám (VNĐ)"] = display_df["Phí khám (VNĐ)"].apply(
            lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Không thể tải danh sách phòng khám: {e}")


# ============================================================
# TRANG ĐẶT LỊCH KHÁM
# ============================================================
def page_booking():
    render_header()
    render_step_indicator(st.session_state["step"])
    st.markdown("<br>", unsafe_allow_html=True)

    # ------- BƯỚC 1: NHẬP TRIỆU CHỨNG -------
    if st.session_state["step"] == 1:
        st.markdown("## 🔍 Bước 1: Nhập triệu chứng của bạn")

        col_form, col_hint = st.columns([3, 2])

        with col_form:
            symptom_input = st.text_input(
                "Mô tả triệu chứng của bạn",
                placeholder="VD: đau ngực, đau răng, mờ mắt, đau lưng...",
                value=st.session_state.get("symptom_input", ""),
                key="symptom_text_input",
            )
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                search_btn = st.button("🔍 Tìm chuyên khoa", use_container_width=True, type="primary")
            with col_btn2:
                browse_btn = st.button("📋 Xem tất cả chuyên khoa", use_container_width=True)

            if search_btn and symptom_input.strip():
                st.session_state["symptom_input"] = symptom_input.strip()
                specialties = find_specialty_by_symptom(symptom_input.strip())

                if specialties:
                    st.session_state["matched_specialties"] = specialties
                    st.success(f"✅ Tìm thấy **{len(specialties)}** chuyên khoa phù hợp!")

                    if len(specialties) == 1:
                        spec = specialties[0]
                        st.session_state["selected_specialty"] = spec
                        st.session_state["doctors_df"] = get_doctors_with_clinic_info(spec)
                        st.session_state["step"] = 2
                        st.rerun()
                    else:
                        st.markdown("### Chọn chuyên khoa phù hợp nhất:")
                        for i, spec in enumerate(specialties):
                            if st.button(f"🩺 {spec}", key=f"spec_choice_{i}", use_container_width=True):
                                st.session_state["selected_specialty"] = spec
                                st.session_state["doctors_df"] = get_doctors_with_clinic_info(spec)
                                st.session_state["step"] = 2
                                st.rerun()
                else:
                    st.warning("⚠️ Không tìm thấy chuyên khoa. Thử từ khóa khác hoặc chọn thủ công bên dưới.")
                    st.session_state["matched_specialties"] = []

            if browse_btn:
                st.session_state["matched_specialties"] = get_all_specialties()

        with col_hint:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#eff6ff,#dbeafe);border-radius:16px;padding:1.5rem;border:1px solid #bfdbfe;">
                <h4 style="color:#1e40af;margin:0 0 12px;">💡 Gợi ý triệu chứng</h4>
                <p style="color:#3730a3;font-size:0.85rem;margin:0 0 8px;"><strong>Tim mạch:</strong> đau ngực, khó thở, tim đập nhanh</p>
                <p style="color:#3730a3;font-size:0.85rem;margin:0 0 8px;"><strong>Nội khoa:</strong> sốt, ho, đau đầu, mệt mỏi</p>
                <p style="color:#3730a3;font-size:0.85rem;margin:0 0 8px;"><strong>Nhi khoa:</strong> trẻ em sốt, trẻ em ho</p>
                <p style="color:#3730a3;font-size:0.85rem;margin:0 0 8px;"><strong>Mắt:</strong> mờ mắt, đau mắt, đỏ mắt</p>
                <p style="color:#3730a3;font-size:0.85rem;margin:0 0 8px;"><strong>Răng:</strong> đau răng, sâu răng</p>
                <p style="color:#3730a3;font-size:0.85rem;margin:0;"><strong>Da liễu:</strong> nổi mụn, ngứa da, phát ban</p>
            </div>
            """, unsafe_allow_html=True)

        if st.session_state.get("matched_specialties"):
            all_specs = st.session_state["matched_specialties"]
            if len(all_specs) > 1 or browse_btn:
                st.markdown("---")
                st.markdown("### 🩺 Chọn chuyên khoa:")
                spec_cols = st.columns(4)
                specialty_icons = {
                    "Nội khoa": "💊", "Tim mạch": "❤️", "Nhi khoa": "👶",
                    "Sản phụ khoa": "🤱", "Mắt": "👁️", "Răng hàm mặt": "🦷",
                    "Da liễu": "🧴", "Thần kinh": "🧠", "Cơ xương khớp": "🦴",
                    "Ngoại khoa": "🔪",
                }
                for i, spec in enumerate(all_specs):
                    with spec_cols[i % 4]:
                        icon = specialty_icons.get(spec, "🩺")
                        if st.button(f"{icon} {spec}", key=f"browse_spec_{i}", use_container_width=True):
                            st.session_state["selected_specialty"] = spec
                            st.session_state["doctors_df"] = get_doctors_with_clinic_info(spec)
                            st.session_state["step"] = 2
                            st.rerun()

    # ------- BƯỚC 2: CHỌN BÁC SĨ -------
    elif st.session_state["step"] == 2:
        st.markdown(f"## 👨‍⚕️ Bước 2: Chọn bác sĩ — Chuyên khoa **{st.session_state['selected_specialty']}**")

        if st.button("← Quay lại", key="back_step2"):
            st.session_state["step"] = 1
            st.session_state["selected_doctor"] = None
            st.rerun()

        doctors_df = st.session_state.get("doctors_df")

        if doctors_df is None or doctors_df.empty:
            st.warning("⚠️ Hiện chưa có bác sĩ nào trong chuyên khoa này.")
            if st.button("Chọn chuyên khoa khác"):
                st.session_state["step"] = 1
                st.rerun()
            return

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👨‍⚕️ Số bác sĩ", len(doctors_df))
        with col2:
            st.metric("🏥 Phòng khám", doctors_df["clinic_id"].nunique())
        with col3:
            st.metric("📍 Gần nhất", f"{doctors_df['distance_km'].min():.1f} km")

        st.markdown("---")
        st.markdown("### Danh sách bác sĩ (sắp xếp theo khoảng cách):")

        clinic_names = ["Tất cả"] + sorted(doctors_df["clinic_name"].dropna().unique().tolist())
        selected_clinic_filter = st.selectbox("🏥 Lọc theo phòng khám:", clinic_names, key="clinic_filter")

        filtered_df = doctors_df.copy()
        if selected_clinic_filter != "Tất cả":
            filtered_df = filtered_df[filtered_df["clinic_name"] == selected_clinic_filter]

        if filtered_df.empty:
            st.info("Không có bác sĩ nào trong phòng khám này.")
        else:
            for idx, row in filtered_df.iterrows():
                selected = render_doctor_card(row.to_dict(), idx)
                if selected:
                    st.session_state["selected_doctor"] = row.to_dict()
                    st.session_state["step"] = 3
                    st.rerun()

    # ------- BƯỚC 3: ĐẶT LỊCH -------
    elif st.session_state["step"] == 3:
        st.markdown("## 📅 Bước 3: Chọn ngày giờ khám")

        col_back, _ = st.columns([1, 4])
        with col_back:
            if st.button("← Quay lại", key="back_step3"):
                st.session_state["step"] = 2
                st.session_state["show_conflict"] = False
                st.session_state["suggestions"] = []
                st.rerun()

        doctor = st.session_state.get("selected_doctor", {})

        col_doc_info = st.columns([2, 3])
        with col_doc_info[0]:
            st.markdown("#### Bác sĩ đã chọn:")
            render_info_card("Tên bác sĩ", doctor.get("doctor_name", "N/A"), "👨‍⚕️", "#1d4ed8")
            render_info_card("Chuyên khoa", doctor.get("specialty", "N/A"), "🩺", "#7c3aed")
            render_info_card("Phòng khám", doctor.get("clinic_name", "N/A"), "🏥", "#059669")
            render_info_card("Khoảng cách", f"{doctor.get('distance_km', 0):.1f} km", "📍", "#f59e0b")
            render_info_card(
                "Phí khám",
                f"{doctor.get('consultation_fee', 0):,.0f} VNĐ" if doctor.get("consultation_fee") else "N/A",
                "💰", "#10b981"
            )

        with col_doc_info[1]:
            st.markdown("#### Thông tin đặt lịch:")

            with st.form("booking_form", clear_on_submit=False):
                patient_name = st.text_input("👤 Họ và tên bệnh nhân *", placeholder="Nguyễn Văn An")
                patient_email = st.text_input("📧 Email nhận xác nhận *", placeholder="example@gmail.com")

                col_date, col_time = st.columns(2)
                with col_date:
                    now = datetime.now()
                    end_t_today = datetime.strptime(WORKING_HOURS_END, "%H:%M").replace(
                        year=now.year, month=now.month, day=now.day
                    )
                    
                    if now >= end_t_today:
                        min_date = date.today() + timedelta(days=1)
                    else:
                        min_date = date.today()

                    appt_date = st.date_input(
                        "📅 Ngày khám *",
                        value=min_date,
                        min_value=min_date,
                        max_value=date.today() + timedelta(days=90),
                    )
                with col_time:
                    time_slots = []
                    current = datetime.strptime(WORKING_HOURS_START, "%H:%M")
                    end_t   = datetime.strptime(WORKING_HOURS_END, "%H:%M")
                    
                    while current <= end_t:
                        slot_str = current.strftime("%H:%M")
                        
                        if appt_date == date.today():
                            slot_time_today = current.replace(year=now.year, month=now.month, day=now.day)
                            if slot_time_today > now:
                                time_slots.append(slot_str)
                        else:
                            time_slots.append(slot_str)
                            
                        current += timedelta(minutes=TIME_SLOT_DURATION_MINUTES)
                    
                    if not time_slots:
                        st.warning("Đã hết giờ trống trong ngày này.")
                        appt_time = st.selectbox("⏰ Giờ khám *", ["Không có giờ hợp lệ"])
                    else:
                        appt_time = st.selectbox("⏰ Giờ khám *", time_slots)

                submit_btn = st.form_submit_button("📅 Xác nhận đặt lịch", use_container_width=True, type="primary")

                if submit_btn:
                    errors = []
                    if not patient_name.strip():
                        errors.append("Vui lòng nhập họ tên bệnh nhân")
                    if not patient_email.strip() or "@" not in patient_email:
                        errors.append("Vui lòng nhập email hợp lệ")
                    if not time_slots or appt_time == "Không có giờ hợp lệ":
                        errors.append("Vui lòng chọn ngày/giờ hợp lệ")

                    if errors:
                        for err in errors:
                            st.error(f"❌ {err}")
                    else:
                        appt_date_str = appt_date.strftime("%Y-%m-%d")
                        doctor_id = doctor.get("doctor_id", "")
                        is_conflict = check_appointment_conflict(doctor_id, appt_date_str, appt_time)

                        if is_conflict:
                            suggestions = suggest_alternative_slots(doctor_id, appt_date_str, appt_time, SUGGEST_SLOTS_COUNT)
                            st.session_state["suggestions"] = suggestions
                            st.session_state["show_conflict"] = True
                            st.session_state["pending_booking"] = {
                                "patient_name":  patient_name.strip(),
                                "patient_email": patient_email.strip(),
                                "doctor_id":     doctor_id,
                                "appt_date":     appt_date_str,
                                "appt_time":     appt_time,
                            }
                            st.rerun()
                        else:
                            _do_booking(patient_name.strip(), patient_email.strip(), doctor, appt_date_str, appt_time)

        if st.session_state.get("show_conflict"):
            pending = st.session_state.get("pending_booking", {})
            selected_slot = render_conflict_banner(
                doctor_name=doctor.get("doctor_name", ""),
                appointment_date=pending.get("appt_date", ""),
                appointment_time=pending.get("appt_time", ""),
                suggestions=st.session_state.get("suggestions", []),
            )
            if selected_slot:
                _do_booking(pending["patient_name"], pending["patient_email"], doctor, selected_slot["date"], selected_slot["time"])

    # ------- BƯỚC 4: THÀNH CÔNG -------
    elif st.session_state["step"] == 4:
        result = st.session_state.get("booking_result", {})
        render_success_banner(
            appointment_id=result.get("appointment_id", ""),
            patient_name=result.get("patient_name", ""),
            doctor_name=result.get("doctor_name", ""),
            specialty=result.get("specialty", ""),
            clinic_name=result.get("clinic_name", ""),
            appointment_date=result.get("appointment_date", ""),
            appointment_time=result.get("appointment_time", ""),
            consultation_fee=result.get("consultation_fee", 0),
            email_sent=result.get("email_sent", False),
        )

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("📅 Đặt lịch khác", use_container_width=True, type="primary"):
                for key in ["step", "selected_doctor", "booking_result", "show_conflict",
                            "suggestions", "pending_booking", "symptom_input",
                            "matched_specialties", "selected_specialty", "doctors_df"]:
                    if key in ["matched_specialties", "suggestions"]:
                        st.session_state[key] = []
                    elif key == "step":
                        st.session_state[key] = 1
                    else:
                        st.session_state[key] = None
                st.rerun()
        with col_b:
            if st.button("📋 Xem lịch hẹn", use_container_width=True):
                st.session_state["page"] = "my_appointments"
                st.rerun()
        with col_c:
            if st.button("🏠 Về trang chủ", use_container_width=True):
                st.session_state["page"] = "home"
                st.rerun()


def _do_booking(patient_name, patient_email, doctor, appt_date_str, appt_time):
    """Lưu lịch hẹn và gửi email xác nhận"""
    patient = get_or_create_patient(patient_name, patient_email)
    appt = save_appointment(
        patient_id=patient["patient_id"],
        doctor_id=doctor.get("doctor_id", ""),
        appointment_date=appt_date_str,
        appointment_time=appt_time,
    )
    email_ok, email_err = send_confirmation_email(
        to_email=patient_email,
        patient_name=patient_name,
        doctor_name=doctor.get("doctor_name", ""),
        specialty=doctor.get("specialty", ""),
        clinic_name=doctor.get("clinic_name", ""),
        appointment_date=appt_date_str,
        appointment_time=appt_time,
        appointment_id=appt["appointment_id"],
        consultation_fee=doctor.get("consultation_fee", 0),
    )
    st.session_state["booking_result"] = {
        "appointment_id":   appt["appointment_id"],
        "patient_name":     patient_name,
        "doctor_name":      doctor.get("doctor_name", ""),
        "specialty":        doctor.get("specialty", ""),
        "clinic_name":      doctor.get("clinic_name", ""),
        "appointment_date": appt_date_str,
        "appointment_time": appt_time,
        "consultation_fee": doctor.get("consultation_fee", 0),
        "email_sent":       email_ok,
        "email_error":      email_err,
    }
    st.session_state["step"] = 4
    st.session_state["show_conflict"] = False
    st.rerun()


# ============================================================
# TRANG LỊCH HẸN CỦA TÔI
# ============================================================
def page_my_appointments():
    render_header()
    st.markdown("## 📋 Lịch hẹn của tôi")

    with st.form("search_patient_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            email_search = st.text_input("📧 Nhập email để xem lịch hẹn", placeholder="example@gmail.com")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            search_btn = st.form_submit_button("🔍 Tìm kiếm", use_container_width=True, type="primary")

    if search_btn and email_search:
        from src.data_manager import get_patient_by_email
        patient = get_patient_by_email(email_search.strip())

        if not patient:
            st.warning("⚠️ Không tìm thấy bệnh nhân với email này trong hệ thống.")
        else:
            st.success(f"👋 Xin chào, **{patient['patient_name']}**!")
            appts = get_appointments_by_patient(patient["patient_id"])

            if appts.empty:
                st.info("📭 Bạn chưa có lịch hẹn nào.")
            else:
                st.markdown(f"### Tổng cộng **{len(appts)}** lịch hẹn:")
                for _, row in appts.iterrows():
                    try:
                        dt = datetime.strptime(f"{row['appointment_date']} {row['appointment_time']}", "%Y-%m-%d %H:%M")
                        is_future = dt.date() >= date.today()
                        status_badge = "🟢 Sắp tới" if is_future else "⚫ Đã qua"
                        status_color = "#22c55e" if is_future else "#9ca3af"
                    except Exception:
                        status_badge = "❓ Không rõ"
                        status_color = "#f59e0b"

                    st.markdown(f"""
                    <div style="background:white;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:0.8rem;border:1px solid #e5e7eb;box-shadow:0 2px 8px rgba(0,0,0,0.05);border-left:4px solid {status_color};">
                        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                            <div>
                                <strong style="color:#111827;">#{row.get('appointment_id','')}</strong>
                                &nbsp;&nbsp;
                                <span style="color:{status_color};font-size:13px;font-weight:600;">{status_badge}</span>
                            </div>
                            <div style="color:#6b7280;font-size:13px;">📅 {row.get('appointment_date','')} &nbsp; ⏰ {row.get('appointment_time','')}</div>
                        </div>
                        <div style="margin-top:8px;color:#374151;font-size:14px;">
                            👨‍⚕️ {row.get('doctor_name','N/A')} &nbsp;·&nbsp; 🩺 {row.get('specialty','N/A')} &nbsp;·&nbsp; 🏥 {row.get('clinic_name','N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


# ============================================================
# TRANG GỬI EMAIL NHẮC LỊCH
# ============================================================
def page_send_reminders():
    render_header()
    st.markdown("## 🔔 Gửi Email Nhắc Lịch")

    st.markdown("""
    <div style="background:#eff6ff;border-radius:12px;padding:1.2rem 1.5rem;border-left:4px solid #3b82f6;margin-bottom:1.5rem;">
        <p style="margin:0;color:#1e40af;font-size:0.95rem;">
            <strong>ℹ️ Chức năng này</strong> gửi email nhắc lịch đến tất cả bệnh nhân có lịch khám vào ngày mai.
            Trong thực tế, chạy script <code>python send_reminders.py</code> mỗi ngày qua Task Scheduler.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_display = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

    try:
        appts_df    = load_appointments()
        doctors_df  = load_doctors()
        clinics_df  = load_clinics()
        patients_df = load_patients()

        tomorrow_appts = appts_df[appts_df["appointment_date"] == tomorrow]
        st.markdown(f"### 📅 Lịch hẹn ngày mai ({tomorrow_display}): **{len(tomorrow_appts)}** lịch")

        if tomorrow_appts.empty:
            st.info("✅ Không có lịch hẹn nào vào ngày mai.")
        else:
            merged = tomorrow_appts.merge(
                doctors_df[["doctor_id", "doctor_name", "specialty"]], on="doctor_id", how="left"
            ).merge(
                patients_df[["patient_id", "patient_name", "email"]], on="patient_id", how="left"
            )

            for _, row in merged.iterrows():
                st.markdown(f"""
                <div style="background:white;color:#111827;border-radius:10px;padding:1rem 1.2rem;margin-bottom:8px;border:1px solid #e5e7eb;">
                    <strong>{row.get('patient_name','N/A')}</strong> ({row.get('email','N/A')}) &nbsp;·&nbsp;
                    {row.get('appointment_time','')} &nbsp;·&nbsp;
                    {row.get('doctor_name','N/A')} &nbsp;·&nbsp; {row.get('specialty','N/A')}
                </div>
                """, unsafe_allow_html=True)

            if st.button(f"📧 Gửi {len(tomorrow_appts)} email nhắc lịch ngay", type="primary", use_container_width=True):
                from src.email_service import send_reminders_for_tomorrow
                with st.spinner("Đang gửi email..."):
                    results = send_reminders_for_tomorrow(appts_df, doctors_df, clinics_df, patients_df)
                success_count = sum(1 for r in results if r["success"])
                fail_count    = len(results) - success_count
                if success_count > 0:
                    st.success(f"✅ Gửi thành công {success_count}/{len(results)} email!")
                if fail_count > 0:
                    st.error(f"❌ Gửi thất bại {fail_count} email. Kiểm tra lại cấu hình SMTP.")

    except Exception as e:
        st.error(f"Lỗi: {e}")


# ============================================================
# TRANG HƯỚNG DẪN
# ============================================================
def page_guide():
    render_header()
    st.markdown("## ℹ️ Hướng dẫn sử dụng")

    with st.expander("📖 Cách đặt lịch khám", expanded=True):
        st.markdown("""
        1. **Nhập triệu chứng**: Mô tả triệu chứng (ví dụ: đau ngực, đau răng...)
        2. **Chọn chuyên khoa**: Hệ thống tự động gợi ý chuyên khoa phù hợp
        3. **Chọn bác sĩ**: Xem danh sách bác sĩ kèm phòng khám, khoảng cách, phí khám
        4. **Đặt lịch**: Nhập tên, email và chọn ngày giờ
        5. **Nhận xác nhận**: Email xác nhận gửi tự động đến hộp thư
        """)


# ============================================================
# TRANG TRỢ LÝ AI CHAT
# ============================================================
def page_chat():
    from src.ai_service import get_gemini_response, build_system_prompt

    render_header()

    # Header chat
    st.markdown("""
    <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6,#a78bfa);
                border-radius:16px;padding:1.2rem 2rem;margin-bottom:1.5rem;
                display:flex;align-items:center;gap:1rem;">
        <span style="font-size:2.5rem;">🤖</span>
        <div>
            <h2 style="color:white;margin:0;font-size:1.4rem;font-weight:800;">Trợ lý AI Sức Khỏe</h2>
            <p style="color:#e0e7ff;margin:0;font-size:0.85rem;">
                Tư vấn triệu chứng · Gợi ý chuyên khoa · Hướng dẫn đặt lịch
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tải context dữ liệu hệ thống để AI "biết"
    try:
        _doctors  = load_doctors()
        _clinics  = load_clinics()
        _specs    = get_all_specialties()
    except Exception:
        _doctors = _clinics = None
        _specs = []

    system_prompt = build_system_prompt(
        doctors_df=_doctors,
        clinics_df=_clinics,
        specialties=_specs,
    )

    # Gợi ý câu hỏi nhanh (chỉ hiện khi chưa chat)
    if not st.session_state["chat_messages"]:
        st.markdown("""
        <p style="color:#6b7280;font-size:0.85rem;margin-bottom:0.5rem;">
            💡 Bạn có thể hỏi về:
        </p>
        """, unsafe_allow_html=True)
        quick_qs = [
            "🩺 Tôi bị đau ngực nên khám chuyên khoa gì?",
            "📅 Cách đặt lịch khám như thế nào?",
            "👁️ Mờ mắt nên gặp bác sĩ nào?",
            "💊 Hệ thống có những chuyên khoa nào?",
        ]
        cols = st.columns(2)
        for i, q in enumerate(quick_qs):
            with cols[i % 2]:
                if st.button(q, key=f"quick_q_{i}", use_container_width=True):
                    st.session_state["chat_messages"].append({
                        "role": "user", "content": q
                    })
                    with st.spinner("AI đang trả lời..."):
                        reply = get_gemini_response(
                            st.session_state["chat_messages"], system_prompt
                        )
                    st.session_state["chat_messages"].append({
                        "role": "model", "content": reply
                    })
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

    # Hiển thị lịch sử chat
    for msg in st.session_state["chat_messages"]:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])

    # Nút xóa lịch sử
    if st.session_state["chat_messages"]:
        col_clear, _ = st.columns([1, 4])
        with col_clear:
            if st.button("🗑️ Xóa lịch sử chat", key="clear_chat"):
                st.session_state["chat_messages"] = []
                st.rerun()

    # Ô nhập chat
    user_input = st.chat_input("Nhập câu hỏi của bạn... (VD: Tôi bị đau đầu nên khám gì?)")
    if user_input:
        st.session_state["chat_messages"].append({
            "role": "user", "content": user_input
        })
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Đang suy nghĩ..."):
                reply = get_gemini_response(
                    st.session_state["chat_messages"], system_prompt
                )
            st.markdown(reply)

        st.session_state["chat_messages"].append({
            "role": "model", "content": reply
        })
        st.rerun()


# ============================================================
# TRANG ĐĂNG NHẬP ADMIN
# ============================================================
def page_admin_login():

    render_header()
    st.markdown("## 🔐 Đăng nhập Quản trị viên")

    col_center = st.columns([1, 1.2, 1])
    with col_center[1]:
        st.markdown("""
        <div style="background:white;border-radius:20px;padding:2.5rem;
                    box-shadow:0 8px 32px rgba(30,64,175,0.15);
                    border:1px solid #e5e7eb;">
            <div style="text-align:center;margin-bottom:1.5rem;">
                <div style="font-size:3rem;">🛡️</div>
                <h3 style="color:#1e40af;margin:8px 0 4px;">Admin Panel</h3>
                <p style="color:#6b7280;font-size:0.85rem;margin:0;">
                    Chỉ dành cho quản trị viên hệ thống
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("admin_login_form"):
            username = st.text_input("👤 Tên đăng nhập", placeholder="admin")
            password = st.text_input("🔑 Mật khẩu", type="password", placeholder="••••••••")
            login_btn = st.form_submit_button("🔐 Đăng nhập", use_container_width=True, type="primary")

        if login_btn:
            if username == ADMIN_CONFIG["username"] and password == ADMIN_CONFIG["password"]:
                st.session_state["is_admin"] = True
                st.session_state["page"] = "admin"
                st.success("✅ Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("❌ Sai tên đăng nhập hoặc mật khẩu!")

        if st.button("← Quay lại trang chủ", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()


# ============================================================
# TRANG ADMIN PANEL
# ============================================================
def page_admin():
    if not st.session_state.get("is_admin"):
        st.session_state["page"] = "admin_login"
        st.rerun()
        return

    render_header()
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e3a8a,#1d4ed8);border-radius:16px;
                padding:1.2rem 2rem;margin-bottom:1.5rem;display:flex;
                align-items:center;gap:1rem;">
        <span style="font-size:2rem;">🛡️</span>
        <div>
            <h2 style="color:white;margin:0;font-size:1.4rem;font-weight:800;">Admin Panel</h2>
            <p style="color:#bfdbfe;margin:0;font-size:0.85rem;">Quản trị hệ thống đặt lịch khám sức khỏe</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard", "👨‍⚕️ Bác sĩ", "🏥 Phòng khám",
        "📅 Lịch hẹn", "👥 Bệnh nhân", "🔔 Nhắc lịch",
    ])

    # ─── TAB 1: DASHBOARD ────────────────────────────────────
    with tab1:
        st.markdown("### 📊 Tổng quan hệ thống")
        try:
            doctors_df  = load_doctors()
            clinics_df  = load_clinics()
            appts_df    = load_appointments()
            patients_df = load_patients()

            # KPI cards
            c1, c2, c3, c4 = st.columns(4)
            kpi_style = (
                "background:white;border-radius:16px;padding:1.2rem 1.5rem;"
                "text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.07);"
                "border-top:4px solid {color};"
            )
            kpis = [
                (c1, "👨‍⚕️", len(doctors_df), "Bác sĩ", "#3b82f6"),
                (c2, "🏥", len(clinics_df), "Phòng khám", "#10b981"),
                (c3, "📅", len(appts_df), "Lịch hẹn", "#f59e0b"),
                (c4, "👥", len(patients_df), "Bệnh nhân", "#8b5cf6"),
            ]
            for col, icon, value, label, color in kpis:
                with col:
                    st.markdown(f"""
                    <div style="{kpi_style.format(color=color)}">
                        <div style="font-size:2rem;">{icon}</div>
                        <div style="font-size:2rem;font-weight:800;color:{color};">{value}</div>
                        <div style="color:#6b7280;font-size:0.85rem;">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col_chart1, col_chart2 = st.columns(2)

            # Biểu đồ lịch hẹn 14 ngày gần nhất
            with col_chart1:
                st.markdown("#### 📈 Lịch hẹn theo ngày (14 ngày gần nhất)")
                if not appts_df.empty and "appointment_date" in appts_df.columns:
                    daily = (
                        appts_df.groupby("appointment_date")
                        .size()
                        .reset_index(name="Số lịch hẹn")
                        .sort_values("appointment_date")
                        .tail(14)
                    )
                    daily.columns = ["Ngày", "Số lịch hẹn"]
                    st.bar_chart(daily.set_index("Ngày"))
                else:
                    st.info("Chưa có dữ liệu lịch hẹn.")

            # Biểu đồ theo chuyên khoa
            with col_chart2:
                st.markdown("#### 🩺 Phân bổ theo chuyên khoa")
                if not appts_df.empty and not doctors_df.empty:
                    merged = appts_df.merge(
                        doctors_df[["doctor_id", "specialty"]], on="doctor_id", how="left"
                    )
                    spec_counts = merged["specialty"].value_counts().reset_index()
                    spec_counts.columns = ["Chuyên khoa", "Số lượng"]
                    st.bar_chart(spec_counts.set_index("Chuyên khoa"))
                else:
                    st.info("Chưa có dữ liệu.")

            # Lịch hẹn sắp tới
            st.markdown("#### 📅 10 lịch hẹn gần nhất")
            if not appts_df.empty:
                display = appts_df.sort_values("appointment_date", ascending=False).head(10)
                if not doctors_df.empty:
                    display = display.merge(
                        doctors_df[["doctor_id", "doctor_name", "specialty"]], on="doctor_id", how="left"
                    )
                if not patients_df.empty:
                    display = display.merge(
                        patients_df[["patient_id", "patient_name", "email"]], on="patient_id", how="left"
                    )
                show_cols = [c for c in ["appointment_id", "appointment_date", "appointment_time",
                                          "patient_name", "doctor_name", "specialty"] if c in display.columns]
                st.dataframe(display[show_cols], use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Lỗi tải dữ liệu: {e}")

    # ─── TAB 2: QUẢN LÝ BÁC SĨ ──────────────────────────────
    with tab2:
        st.markdown("### 👨‍⚕️ Quản lý Bác sĩ")
        try:
            doctors_df = load_doctors()
            st.info(f"📋 Tổng cộng **{len(doctors_df)}** bác sĩ trong hệ thống")

            edited_doctors = st.data_editor(
                doctors_df,
                use_container_width=True,
                num_rows="dynamic",
                key="doctors_editor",
                column_config={
                    "doctor_id":        st.column_config.TextColumn("Mã BS", disabled=True),
                    "doctor_name":      st.column_config.TextColumn("Tên bác sĩ", width="medium"),
                    "specialty":        st.column_config.TextColumn("Chuyên khoa", width="medium"),
                    "clinic_id":        st.column_config.TextColumn("Mã phòng khám"),
                    "experience_years": st.column_config.NumberColumn("Kinh nghiệm (năm)", min_value=0, max_value=50),
                },
            )

            col_save, col_reset = st.columns(2)
            with col_save:
                if st.button("💾 Lưu thay đổi bác sĩ", type="primary", use_container_width=True):
                    # Tự động tạo ID mới cho dòng thêm mới
                    if "doctor_id" in edited_doctors.columns:
                        missing_id = edited_doctors["doctor_id"].isna() | (edited_doctors["doctor_id"] == "")
                        if missing_id.any():
                            import uuid
                            edited_doctors.loc[missing_id, "doctor_id"] = [
                                f"D{str(uuid.uuid4())[:6].upper()}" for _ in range(missing_id.sum())
                            ]
                    edited_doctors.to_csv(
                        __import__("src.config", fromlist=["DOCTORS_CSV"]).DOCTORS_CSV,
                        index=False, encoding="utf-8-sig",
                    )
                    st.success("✅ Đã lưu danh sách bác sĩ!")
                    st.rerun()
            with col_reset:
                if st.button("↩️ Làm mới", use_container_width=True):
                    st.rerun()

        except Exception as e:
            st.error(f"Lỗi: {e}")

    # ─── TAB 3: QUẢN LÝ PHÒNG KHÁM ──────────────────────────
    with tab3:
        st.markdown("### 🏥 Quản lý Phòng khám")
        try:
            clinics_df = load_clinics()
            st.info(f"📋 Tổng cộng **{len(clinics_df)}** phòng khám")

            edited_clinics = st.data_editor(
                clinics_df,
                use_container_width=True,
                num_rows="dynamic",
                key="clinics_editor",
                column_config={
                    "clinic_id":        st.column_config.TextColumn("Mã PK", disabled=True),
                    "clinic_name":      st.column_config.TextColumn("Tên phòng khám", width="large"),
                    "distance_km":      st.column_config.NumberColumn("Khoảng cách (km)", min_value=0, format="%.1f"),
                    "consultation_fee": st.column_config.NumberColumn("Phí khám (VNĐ)", min_value=0, format="%d"),
                },
            )

            if st.button("💾 Lưu thay đổi phòng khám", type="primary", use_container_width=True):
                if "clinic_id" in edited_clinics.columns:
                    missing_id = edited_clinics["clinic_id"].isna() | (edited_clinics["clinic_id"] == "")
                    if missing_id.any():
                        import uuid
                        edited_clinics.loc[missing_id, "clinic_id"] = [
                            f"C{str(uuid.uuid4())[:6].upper()}" for _ in range(missing_id.sum())
                        ]
                edited_clinics.to_csv(
                    __import__("src.config", fromlist=["CLINICS_CSV"]).CLINICS_CSV,
                    index=False, encoding="utf-8-sig",
                )
                st.success("✅ Đã lưu danh sách phòng khám!")
                st.rerun()

        except Exception as e:
            st.error(f"Lỗi: {e}")

    # ─── TAB 4: QUẢN LÝ LỊCH HẸN ────────────────────────────
    with tab4:
        st.markdown("### 📅 Quản lý Lịch hẹn")
        try:
            appts_df    = load_appointments()
            doctors_df  = load_doctors()
            patients_df = load_patients()

            # Merge để hiển thị đầy đủ
            display_appts = appts_df.copy()
            if not doctors_df.empty:
                display_appts = display_appts.merge(
                    doctors_df[["doctor_id", "doctor_name", "specialty"]], on="doctor_id", how="left"
                )
            if not patients_df.empty:
                display_appts = display_appts.merge(
                    patients_df[["patient_id", "patient_name", "email"]], on="patient_id", how="left"
                )

            # Bộ lọc
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                filter_date = st.date_input("📅 Lọc theo ngày", value=None, key="admin_filter_date")
            with col_f2:
                spec_options = ["Tất cả"] + (doctors_df["specialty"].unique().tolist() if not doctors_df.empty else [])
                filter_spec = st.selectbox("🩺 Lọc theo chuyên khoa", spec_options, key="admin_filter_spec")
            with col_f3:
                filter_name = st.text_input("🔍 Tìm theo tên bệnh nhân", key="admin_filter_name")

            filtered = display_appts.copy()
            if filter_date:
                filtered = filtered[filtered["appointment_date"] == filter_date.strftime("%Y-%m-%d")]
            if filter_spec != "Tất cả" and "specialty" in filtered.columns:
                filtered = filtered[filtered["specialty"] == filter_spec]
            if filter_name and "patient_name" in filtered.columns:
                filtered = filtered[filtered["patient_name"].str.contains(filter_name, case=False, na=False)]

            st.markdown(f"**{len(filtered)}** lịch hẹn phù hợp")

            show_cols = [c for c in ["appointment_id", "appointment_date", "appointment_time",
                                      "patient_name", "email", "doctor_name", "specialty"] if c in filtered.columns]
            st.dataframe(filtered[show_cols].sort_values("appointment_date", ascending=False),
                         use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("#### ➕ Thêm lịch hẹn mới")
            with st.form("admin_add_appt_form", clear_on_submit=True):
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    new_pt_name = st.text_input("👤 Họ và tên bệnh nhân *")
                    new_pt_email = st.text_input("📧 Email bệnh nhân *")
                with col_a2:
                    doctor_options = {}
                    if not doctors_df.empty:
                        for _, row in doctors_df.iterrows():
                            doctor_options[row['doctor_id']] = f"{row['doctor_name']} - {row['specialty']}"
                    
                    new_doc_id = st.selectbox("👨‍⚕️ Bác sĩ *", options=list(doctor_options.keys()), format_func=lambda x: doctor_options.get(x, x))
                    
                    min_date = date.today()
                    new_date = st.date_input("📅 Ngày khám *", value=min_date, min_value=min_date)
                    
                    time_slots = []
                    current = datetime.strptime(WORKING_HOURS_START, "%H:%M")
                    end_t   = datetime.strptime(WORKING_HOURS_END, "%H:%M")
                    while current <= end_t:
                        time_slots.append(current.strftime("%H:%M"))
                        current += timedelta(minutes=TIME_SLOT_DURATION_MINUTES)
                    new_time = st.selectbox("⏰ Giờ khám *", time_slots)
                
                submit_add = st.form_submit_button("➕ Thêm lịch hẹn", type="primary", use_container_width=True)
                
            if submit_add:
                if not new_pt_name.strip() or not new_pt_email.strip():
                    st.error("❌ Vui lòng nhập đầy đủ tên và email bệnh nhân.")
                elif not new_doc_id:
                    st.error("❌ Vui lòng chọn bác sĩ.")
                else:
                    date_str = new_date.strftime("%Y-%m-%d")
                    is_conflict = check_appointment_conflict(new_doc_id, date_str, new_time)
                    if is_conflict:
                        st.error(f"❌ Bác sĩ đã có lịch hẹn vào lúc {new_time} ngày {date_str}. Vui lòng chọn giờ khác.")
                    else:
                        patient = get_or_create_patient(new_pt_name.strip(), new_pt_email.strip())
                        save_appointment(
                            patient_id=patient["patient_id"],
                            doctor_id=new_doc_id,
                            appointment_date=date_str,
                            appointment_time=new_time,
                        )
                        st.success("✅ Đã thêm lịch hẹn thành công!")
                        import time
                        time.sleep(1)
                        st.rerun()

            st.markdown("---")
            st.markdown("#### 🗑️ Hủy lịch hẹn")
            cancel_id = st.text_input("Nhập mã lịch hẹn cần hủy:", placeholder="VD: APT-001", key="cancel_appt_id")
            if st.button("❌ Hủy lịch hẹn này", type="primary", key="cancel_appt_btn"):
                if cancel_id.strip():
                    from src.config import APPOINTMENTS_CSV
                    original = load_appointments()
                    if cancel_id.strip() in original["appointment_id"].values:
                        updated = original[original["appointment_id"] != cancel_id.strip()]
                        updated.to_csv(APPOINTMENTS_CSV, index=False, encoding="utf-8-sig")
                        st.success(f"✅ Đã hủy lịch hẹn **{cancel_id}**!")
                        st.rerun()
                    else:
                        st.error(f"❌ Không tìm thấy mã lịch hẹn '{cancel_id}'")
                else:
                    st.warning("⚠️ Vui lòng nhập mã lịch hẹn.")

        except Exception as e:
            st.error(f"Lỗi: {e}")

    # ─── TAB 5: QUẢN LÝ BỆNH NHÂN ───────────────────────────
    with tab5:
        st.markdown("### 👥 Quản lý Bệnh nhân")
        try:
            patients_df = load_patients()
            st.info(f"📋 Tổng cộng **{len(patients_df)}** bệnh nhân đã đăng ký")

            search_pt = st.text_input("🔍 Tìm kiếm theo tên hoặc email:", key="admin_patient_search")
            filtered_pt = patients_df.copy()
            if search_pt:
                mask = (
                    filtered_pt["patient_name"].str.contains(search_pt, case=False, na=False)
                    | filtered_pt["email"].str.contains(search_pt, case=False, na=False)
                )
                filtered_pt = filtered_pt[mask]

            st.markdown(f"**{len(filtered_pt)}** bệnh nhân")
            st.dataframe(filtered_pt, use_container_width=True, hide_index=True,
                         column_config={
                             "patient_id":   st.column_config.TextColumn("Mã BN"),
                             "patient_name": st.column_config.TextColumn("Họ và tên", width="medium"),
                             "email":        st.column_config.TextColumn("Email", width="large"),
                         })

            # Lịch hẹn của bệnh nhân được chọn
            if not filtered_pt.empty and search_pt:
                appts_df = load_appointments()
                doctors_df = load_doctors()
                patient_ids = filtered_pt["patient_id"].tolist()
                pt_appts = appts_df[appts_df["patient_id"].isin(patient_ids)]
                if not pt_appts.empty and not doctors_df.empty:
                    pt_appts = pt_appts.merge(
                        doctors_df[["doctor_id", "doctor_name", "specialty"]], on="doctor_id", how="left"
                    )
                if not pt_appts.empty:
                    st.markdown(f"#### 📅 Lịch hẹn ({len(pt_appts)} lịch):")
                    show_c = [c for c in ["appointment_id", "appointment_date", "appointment_time",
                                           "doctor_name", "specialty"] if c in pt_appts.columns]
                    st.dataframe(pt_appts[show_c], use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Lỗi: {e}")

    # ─── TAB 6: GỬI NHẮC LỊCH ───────────────────────────────
    with tab6:
        st.markdown("### 🔔 Gửi Email Nhắc Lịch")

        st.markdown("""
        <div style="background:#eff6ff;border-radius:12px;padding:1.2rem 1.5rem;
                    border-left:4px solid #3b82f6;margin-bottom:1.5rem;">
            <p style="margin:0;color:#1e40af;font-size:0.95rem;">
                <strong>ℹ️ Chức năng này</strong> gửi email nhắc lịch đến tất cả bệnh nhân
                có lịch khám vào ngày mai. Trong thực tế, chạy script
                <code>python send_reminders.py</code> mỗi ngày qua Task Scheduler.
            </p>
        </div>
        """, unsafe_allow_html=True)

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow_display = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

        try:
            appts_df    = load_appointments()
            doctors_df  = load_doctors()
            clinics_df  = load_clinics()
            patients_df = load_patients()

            tomorrow_appts = appts_df[appts_df["appointment_date"] == tomorrow]
            st.markdown(f"#### 📅 Lịch hẹn ngày mai ({tomorrow_display}): **{len(tomorrow_appts)}** lịch")

            if tomorrow_appts.empty:
                st.info("✅ Không có lịch hẹn nào vào ngày mai.")
            else:
                merged = tomorrow_appts.merge(
                    doctors_df[["doctor_id", "doctor_name", "specialty"]], on="doctor_id", how="left"
                ).merge(
                    patients_df[["patient_id", "patient_name", "email"]], on="patient_id", how="left"
                )

                for _, row in merged.iterrows():
                    st.markdown(f"""
                    <div style="background:white;border-radius:10px;padding:1rem 1.2rem;
                                margin-bottom:8px;border:1px solid #e5e7eb;">
                        <strong>{row.get('patient_name','N/A')}</strong>
                        ({row.get('email','N/A')}) &nbsp;·&nbsp;
                        ⏰ {row.get('appointment_time','')} &nbsp;·&nbsp;
                        👨‍⚕️ {row.get('doctor_name','N/A')} &nbsp;·&nbsp;
                        🩺 {row.get('specialty','N/A')}
                    </div>
                    """, unsafe_allow_html=True)

                if st.button(f"📧 Gửi {len(tomorrow_appts)} email nhắc lịch ngay",
                             type="primary", use_container_width=True, key="admin_send_reminders"):
                    from src.email_service import send_reminders_for_tomorrow
                    with st.spinner("Đang gửi email..."):
                        results = send_reminders_for_tomorrow(appts_df, doctors_df, clinics_df, patients_df)
                    success_count = sum(1 for r in results if r["success"])
                    fail_count    = len(results) - success_count
                    if success_count > 0:
                        st.success(f"✅ Gửi thành công {success_count}/{len(results)} email!")
                    if fail_count > 0:
                        st.error(f"❌ Gửi thất bại {fail_count} email. Kiểm tra lại cấu hình SMTP.")

        except Exception as e:
            st.error(f"Lỗi: {e}")


# ============================================================
# ROUTER CHÍNH
# ============================================================
page = st.session_state.get("page", "home")

if page == "home":
    page_home()
elif page == "booking":
    page_booking()
elif page == "my_appointments":
    page_my_appointments()
elif page == "guide":
    page_guide()
elif page == "chat":
    page_chat()
elif page == "admin_login":
    page_admin_login()
elif page == "admin":
    page_admin()
else:
    page_home()

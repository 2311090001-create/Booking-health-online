"""
Module xử lý dữ liệu CSV
Đọc, ghi, và truy vấn dữ liệu từ các file CSV
"""

import pandas as pd
import os
import uuid
from datetime import datetime

from src.config import (
    PATIENTS_CSV, CLINICS_CSV, DOCTORS_CSV,
    SYMPTOMS_CSV, APPOINTMENTS_CSV
)


# ============================================================
# HÀM ĐỌC DỮ LIỆU
# ============================================================

def load_patients() -> pd.DataFrame:
    """Đọc danh sách bệnh nhân"""
    return pd.read_csv(PATIENTS_CSV, dtype=str).fillna("")


def load_clinics() -> pd.DataFrame:
    """Đọc danh sách phòng khám"""
    df = pd.read_csv(CLINICS_CSV, dtype=str).fillna("")
    df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce")
    df["consultation_fee"] = pd.to_numeric(df["consultation_fee"], errors="coerce")
    return df


def load_doctors() -> pd.DataFrame:
    """Đọc danh sách bác sĩ"""
    df = pd.read_csv(DOCTORS_CSV, dtype=str).fillna("")
    df["experience_years"] = pd.to_numeric(df["experience_years"], errors="coerce")
    return df


def load_symptoms() -> pd.DataFrame:
    """Đọc bảng triệu chứng - chuyên khoa"""
    return pd.read_csv(SYMPTOMS_CSV, dtype=str).fillna("")


def load_appointments() -> pd.DataFrame:
    """Đọc danh sách lịch hẹn"""
    return pd.read_csv(APPOINTMENTS_CSV, dtype=str).fillna("")


# ============================================================
# TRA CỨU DỮ LIỆU
# ============================================================

def find_specialty_by_symptom(symptom_input: str) -> list[str]:
    """
    Tìm chuyên khoa phù hợp dựa trên triệu chứng người dùng nhập.
    Hỗ trợ tìm kiếm mờ (partial match).
    
    Returns:
        Danh sách chuyên khoa tìm được (có thể có nhiều)
    """
    df = load_symptoms()
    symptom_lower = symptom_input.strip().lower()
    
    # Tìm kiếm theo từ khóa (tìm mờ)
    mask = df["symptom"].str.lower().str.contains(symptom_lower, na=False, regex=False)
    matched = df[mask]
    
    if matched.empty:
        return []
    
    return matched["specialty"].unique().tolist()


def get_all_specialties() -> list[str]:
    """Lấy toàn bộ danh sách chuyên khoa"""
    df = load_symptoms()
    return sorted(df["specialty"].unique().tolist())


def get_doctors_by_specialty(specialty: str) -> pd.DataFrame:
    """Lấy danh sách bác sĩ theo chuyên khoa"""
    df = load_doctors()
    return df[df["specialty"] == specialty].copy()


def get_clinic_info(clinic_id: str) -> dict:
    """Lấy thông tin phòng khám theo ID"""
    df = load_clinics()
    row = df[df["clinic_id"] == clinic_id]
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


def get_doctors_with_clinic_info(specialty: str) -> pd.DataFrame:
    """
    Lấy danh sách bác sĩ kèm thông tin phòng khám,
    sắp xếp theo khoảng cách phòng khám tăng dần.
    """
    doctors = get_doctors_by_specialty(specialty)
    if doctors.empty:
        return pd.DataFrame()
    
    clinics = load_clinics()
    
    # Gộp thông tin bác sĩ và phòng khám
    merged = doctors.merge(clinics, on="clinic_id", how="left")
    
    # Sắp xếp theo khoảng cách tăng dần
    merged = merged.sort_values("distance_km", ascending=True)
    merged = merged.reset_index(drop=True)
    
    return merged


def get_patient_by_email(email: str) -> dict:
    """Tìm bệnh nhân theo email"""
    df = load_patients()
    row = df[df["email"].str.lower() == email.strip().lower()]
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


def get_or_create_patient(patient_name: str, email: str) -> dict:
    """
    Lấy thông tin bệnh nhân nếu đã tồn tại,
    hoặc tạo mới nếu chưa có trong hệ thống.
    """
    patient = get_patient_by_email(email)
    if patient:
        return patient
    
    # Tạo bệnh nhân mới
    df = load_patients()
    new_id = f"P{str(len(df) + 1).zfill(3)}"
    new_patient = {
        "patient_id": new_id,
        "patient_name": patient_name,
        "email": email.strip().lower(),
    }
    new_row = pd.DataFrame([new_patient])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(PATIENTS_CSV, index=False)
    return new_patient


# ============================================================
# KIỂM TRA VÀ ĐẶT LỊCH HẸN
# ============================================================

def check_appointment_conflict(doctor_id: str, appointment_date: str, appointment_time: str) -> bool:
    """
    Kiểm tra xem bác sĩ đã có lịch vào ngày giờ này chưa.
    
    Returns:
        True nếu BỊ TRÙNG, False nếu còn trống.
    """
    df = load_appointments()
    if df.empty:
        return False
    
    conflict = df[
        (df["doctor_id"] == doctor_id) &
        (df["appointment_date"] == appointment_date) &
        (df["appointment_time"] == appointment_time)
    ]
    return not conflict.empty


def suggest_alternative_slots(
    doctor_id: str,
    appointment_date: str,
    appointment_time: str,
    count: int = 3
) -> list[dict]:
    """
    Gợi ý các khung giờ thay thế (cách nhau 30 phút) nếu lịch bị trùng.
    
    Returns:
        Danh sách dict {'date': ..., 'time': ...} cho các khung giờ trống.
    """
    from datetime import timedelta
    from src.config import WORKING_HOURS_START, WORKING_HOURS_END, TIME_SLOT_DURATION_MINUTES

    base_dt = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
    work_end = datetime.strptime(f"{appointment_date} {WORKING_HOURS_END}", "%Y-%m-%d %H:%M")
    
    suggestions = []
    candidate = base_dt + timedelta(minutes=TIME_SLOT_DURATION_MINUTES)
    
    while len(suggestions) < count:
        # Nếu vượt quá giờ làm việc trong ngày, sang ngày hôm sau
        if candidate > work_end:
            next_date = candidate.date() + timedelta(days=1)
            candidate = datetime.strptime(
                f"{next_date} {WORKING_HOURS_START}", "%Y-%m-%d %H:%M"
            )
            work_end = datetime.strptime(
                f"{next_date} {WORKING_HOURS_END}", "%Y-%m-%d %H:%M"
            )
        
        slot_date = candidate.strftime("%Y-%m-%d")
        slot_time = candidate.strftime("%H:%M")
        
        if not check_appointment_conflict(doctor_id, slot_date, slot_time):
            suggestions.append({"date": slot_date, "time": slot_time})
        
        candidate += timedelta(minutes=TIME_SLOT_DURATION_MINUTES)
    
    return suggestions


def save_appointment(
    patient_id: str,
    doctor_id: str,
    appointment_date: str,
    appointment_time: str
) -> dict:
    """
    Lưu lịch hẹn mới vào file appointments.csv.
    
    Returns:
        Dict thông tin lịch hẹn vừa tạo.
    """
    df = load_appointments()
    
    # Tạo appointment_id mới
    new_id = f"A{str(len(df) + 1).zfill(3)}"
    
    new_appt = {
        "appointment_id": new_id,
        "patient_id":     patient_id,
        "doctor_id":      doctor_id,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
    }
    
    new_row = pd.DataFrame([new_appt])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(APPOINTMENTS_CSV, index=False)
    
    return new_appt


def get_appointments_by_patient(patient_id: str) -> pd.DataFrame:
    """Lấy toàn bộ lịch hẹn của một bệnh nhân"""
    df = load_appointments()
    doctors = load_doctors()
    clinics = load_clinics()
    
    patient_appts = df[df["patient_id"] == patient_id].copy()
    if patient_appts.empty:
        return pd.DataFrame()
    
    # Gộp thêm thông tin bác sĩ và phòng khám
    merged = patient_appts.merge(doctors[["doctor_id", "doctor_name", "specialty", "clinic_id"]], 
                                  on="doctor_id", how="left")
    merged = merged.merge(clinics[["clinic_id", "clinic_name"]], on="clinic_id", how="left")
    return merged


def get_doctor_info(doctor_id: str) -> dict:
    """Lấy thông tin bác sĩ theo ID"""
    df = load_doctors()
    row = df[df["doctor_id"] == doctor_id]
    if row.empty:
        return {}
    return row.iloc[0].to_dict()

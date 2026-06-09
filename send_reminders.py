"""
Script gửi email nhắc lịch tự động
Chạy script này mỗi ngày (qua Task Scheduler hoặc cron job)
để tự động gửi email nhắc lịch cho bệnh nhân có lịch khám vào ngày hôm sau.

Cách chạy:
    python send_reminders.py

Thiết lập tự động (Windows Task Scheduler):
    - Action: python C:\\đường\\dẫn\\send_reminders.py
    - Trigger: Hàng ngày lúc 08:00 sáng

Thiết lập tự động (Linux/Mac Cron):
    0 8 * * * /usr/bin/python3 /đường/dẫn/send_reminders.py
"""

import sys
import os
import logging
from datetime import datetime

# Thêm thư mục gốc vào Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_manager import (
    load_appointments,
    load_doctors,
    load_clinics,
    load_patients,
)
from src.email_service import send_reminders_for_tomorrow

# Cấu hình logging để ghi lại kết quả
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("reminder_log.txt", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info(f"Bắt đầu gửi email nhắc lịch - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        appointments_df = load_appointments()
        doctors_df      = load_doctors()
        clinics_df      = load_clinics()
        patients_df     = load_patients()
        
        results = send_reminders_for_tomorrow(
            appointments_df, doctors_df, clinics_df, patients_df
        )
        
        if not results:
            logger.info("✅ Không có lịch hẹn nào vào ngày mai. Không cần gửi email.")
        else:
            success = sum(1 for r in results if r["success"])
            failed  = len(results) - success
            
            logger.info(f"📧 Tổng số email cần gửi: {len(results)}")
            logger.info(f"✅ Gửi thành công: {success}")
            logger.info(f"❌ Gửi thất bại:  {failed}")
            
            for r in results:
                if r["success"]:
                    logger.info(f"  ✅ Gửi OK: {r['patient_email']} (#{r['appointment_id']})")
                else:
                    logger.error(f"  ❌ Lỗi: {r['patient_email']} - {r['error']}")
        
        logger.info("=" * 60)
        logger.info("Hoàn thành gửi email nhắc lịch")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"❌ Lỗi nghiêm trọng: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

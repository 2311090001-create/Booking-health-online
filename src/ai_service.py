"""
Dịch vụ AI Chat sử dụng Google Gemini (google-genai package mới)
Hỗ trợ tư vấn sức khỏe và hỗ trợ đặt lịch khám
"""

import streamlit as st


def get_api_key() -> str:
    """
    Lấy Gemini API key theo thứ tự ưu tiên:
    1. st.secrets (Streamlit Cloud)
    2. config.py (local dev)
    """
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        from src.config import GEMINI_API_KEY
        return GEMINI_API_KEY


def build_system_prompt(doctors_df=None, clinics_df=None, specialties=None) -> str:
    """Tạo system prompt với context dữ liệu thực của hệ thống"""

    specialty_list = ", ".join(specialties) if specialties else (
        "Nội khoa, Tim mạch, Nhi khoa, Da liễu, Mắt, Răng hàm mặt, "
        "Thần kinh, Cơ xương khớp, Ngoại khoa, Sản phụ khoa"
    )

    doctor_summary = f"Hiện có {len(doctors_df)} bác sĩ trong hệ thống." if (
        doctors_df is not None and not doctors_df.empty
    ) else ""

    clinic_summary = f"Có {len(clinics_df)} phòng khám." if (
        clinics_df is not None and not clinics_df.empty
    ) else ""

    return f"""Bạn là trợ lý AI thông minh của **Hệ thống Đặt Lịch Khám Sức Khỏe Online**.

## Nhiệm vụ của bạn:
- Tư vấn người dùng về triệu chứng và gợi ý chuyên khoa phù hợp
- Hướng dẫn cách sử dụng hệ thống để đặt lịch khám
- Trả lời câu hỏi về sức khỏe thông thường
- Thân thiện, ngắn gọn, dễ hiểu

## Thông tin hệ thống:
- {doctor_summary}
- {clinic_summary}
- Các chuyên khoa: {specialty_list}
- Giờ làm việc: 07:00 – 17:00
- Có thể đặt lịch trước tối đa 90 ngày

## Quy tắc trả lời:
1. **Luôn trả lời bằng tiếng Việt**
2. Khi người dùng mô tả triệu chứng → gợi ý chuyên khoa và khuyến nghị đặt lịch
3. Không đưa ra chẩn đoán y tế cụ thể — luôn khuyến khích đến khám trực tiếp
4. Câu trả lời ngắn gọn (3-5 câu), dùng emoji phù hợp để thân thiện hơn

## Hướng dẫn đặt lịch:
1. Nhập triệu chứng → 2. Chọn chuyên khoa → 3. Chọn bác sĩ → 4. Xác nhận & nhận email
"""


def get_gemini_response(messages: list[dict], system_prompt: str) -> str:
    """
    Gọi Gemini API (google-genai package mới) và trả về response.
    messages: list of {"role": "user"/"model", "content": "..."}
    """
    try:
        from google import genai
        from google.genai import types

        api_key = get_api_key()
        client = genai.Client(api_key=api_key)

        # Chuyển messages thành format của google-genai
        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append(
                types.Content(role=role, parts=[types.Part(text=msg["content"])])
            )

        last_message = messages[-1]["content"]

        # Thử các model theo thứ tự (ưu tiên model còn quota)
        model_candidates = [
            "gemini-2.5-flash",       # ưu tiên - đang hoạt động
            "gemini-2.0-flash",       # fallback
            "gemini-2.0-flash-lite",  # fallback nhẹ
        ]

        last_err = None
        for model_name in model_candidates:
            try:
                chat = client.chats.create(
                    model=model_name,
                    history=history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.7,
                        max_output_tokens=512,
                    ),
                )
                response = chat.send_message(last_message)
                return response.text
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                # Fallback nếu model không khả dụng hoặc quá tải
                if any(k in err_str for k in ["404", "not found", "not support", "503", "unavailable", "overload"]):
                    continue
                raise  # lỗi khác (auth, quota...) thì raise luôn

        raise last_err

    except ImportError:
        return (
            "⚠️ Chưa cài thư viện `google-genai`. "
            "Chạy: `pip install google-genai`"
        )
    except Exception as e:
        err = str(e).lower()
        # Fallback sang chế độ tự động nếu lỗi quota, invalid key, hoặc lỗi mạng
        if "quota" in err or "429" in err or "api_key" in err or "invalid" in err or "401" in err or "400" in err:
            msg = messages[-1]["content"].lower()
            if "đau ngực" in msg or "tim" in msg or "khó thở" in msg:
                return "🤖 (Chế độ Offline): Triệu chứng của bạn có thể liên quan đến **Tim mạch**. Bạn hãy sang phần Đặt lịch và chọn chuyên khoa Tim mạch nhé."
            elif "đau răng" in msg or "sâu răng" in msg:
                return "🤖 (Chế độ Offline): Bạn nên đặt lịch khám ở chuyên khoa **Răng hàm mặt**."
            elif "mờ mắt" in msg or "đau mắt" in msg:
                return "🤖 (Chế độ Offline): Bạn nên đặt lịch khám ở chuyên khoa **Mắt**."
            elif "ho" in msg or "sốt" in msg or "đau đầu" in msg:
                return "🤖 (Chế độ Offline): Các triệu chứng này thường thuộc chuyên khoa **Nội khoa**. Nếu là trẻ em thì chọn **Nhi khoa** nhé."
            elif "nổi mụn" in msg or "ngứa da" in msg or "phát ban" in msg:
                return "🤖 (Chế độ Offline): Các triệu chứng này thường thuộc chuyên khoa **da liễu**"
            elif "đặt lịch" in msg or "hướng dẫn" in msg:
                return "🤖 (Chế độ Offline): Để đặt lịch, bạn nhấn vào trang chủ ở slide bar **Đặt lịch khám**, nhập triệu chứng hoặc chọn trực tiếp chuyên khoa và bác sĩ nhé."
            else:
                return "🤖 (Chế độ Offline): Hiện tại AI đang hết lượt sử dụng miễn phí từ Google nên tôi trả lời tự động. Hãy chuyển sang phần **Đặt lịch khám**, nhập triệu chứng để hệ thống gợi ý chuyên khoa tự động nhé!"
            
        return f"⚠️ Lỗi kết nối AI: {e}"


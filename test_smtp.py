import sys, smtplib
sys.path.insert(0, ".")
from src.config import EMAIL_CONFIG

cfg = EMAIL_CONFIG
email = cfg["sender_email"]
password = cfg["sender_password"]
server_addr = cfg["smtp_server"]
port = cfg["smtp_port"]

print("=" * 45)
print("KIEM TRA CAU HINH GMAIL SMTP")
print("=" * 45)
print("Email   :", email)
print("Password:", password[:4] + "****" + password[-4:] if len(password) >= 8 else "****")
print("Server  :", server_addr, "port", port)
print()

if email == "your_email@gmail.com":
    print("CHUA CAU HINH: Vui long dien email vao src/config.py")
    sys.exit(1)

print("Dang ket noi SMTP...")
try:
    with smtplib.SMTP(server_addr, port, timeout=10) as s:
        s.ehlo()
        s.starttls()
        s.login(email, password)
        print()
        print("=== KET NOI THANH CONG! ===")
        print("Gmail SMTP hoat dong binh thuong.")
        print("Ung dung co the gui email xac nhan.")
except smtplib.SMTPAuthenticationError as e:
    print()
    print("=== LOI XAC THUC ===")
    print("Sai email hoac App Password.")
    print("Hay kiem tra lai tai: myaccount.google.com/apppasswords")
    print("Chi tiet:", str(e)[:120])
except smtplib.SMTPConnectError as e:
    print()
    print("=== LOI KET NOI ===")
    print("Khong the ket noi den Gmail SMTP.")
    print("Kiem tra ket noi internet hoac firewall.")
    print("Chi tiet:", str(e)[:120])
except Exception as e:
    print()
    print("=== LOI KHAC ===")
    print(type(e).__name__, ":", str(e)[:200])

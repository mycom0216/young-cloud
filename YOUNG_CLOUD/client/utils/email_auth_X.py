# utils/email_auth.py
import yagmail
import random

def send_verification_email(receiver_email):
    """
    지정된 Gmail 계정을 통해 인증코드를 생성하고 이메일로 발송하는 함수
    반환값: (성공 여부(bool), 생성된 인증코드 또는 에러메시지)
    """
    sender_email = "hyun20260714@gmail.com"
    app_password = "wucv dejb gbmx ihvd"
    
    try:
        # 6자리 랜덤 인증코드 생성
        auth_code = str(random.randint(100000, 999999))
        
        # yagmail 객체 생성 및 로그인
        yag = yagmail.SMTP(user=sender_email, password=app_password)
        
        # 메일 제목과 본문 설정
        subject = "[YOUNG CLOUD] 회원가입 이메일 인증코드"
        contents = [
            f"안녕하세요, YOUNG CLOUD입니다.",
            f"요청하신 회원가입 인증코드는 [{auth_code}] 입니다.",
            "화면에 해당 코드를 입력하여 인증을 완료해주세요."
        ]
        
        # 메일 발송
        yag.send(to=receiver_email, subject=subject, contents=contents)
        
        print(f"[이메일 전송 성공] {receiver_email} 앞으로 인증코드 발송 완료")
        return True, auth_code
        
    except Exception as e:
        print(f"[이메일 전송 실패 오류] {e}")
        return False, str(e)
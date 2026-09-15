# server/client_hendler.py
import threading
import json
import pymysql
import random
import yagmail

class ClientHandler(threading.Thread):
    def __init__(self, client_sock, client_addr, db_lock):
        super().__init__()
        self.client_sock = client_sock
        self.client_addr = client_addr
        self.db_lock = db_lock

    def run(self):
        try:
            while True:
                data = self.client_sock.recv(4096)
                if not data:
                    break
                
                request = json.loads(data.decode('utf-8'))
                response = self.route_request(request)
                self.client_sock.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            print(f"[에러 발생] 클라이언트 통신 오류: {e}")
        finally:
            self.client_sock.close()

    def route_request(self, request):
        action = request.get("action")
        data = request.get("data", {})

        print(f"[요청 수신] 작업 종류(Action): {action}")

        with self.db_lock:
            try:
                # MariaDB 원격 연결 설정
                conn = pymysql.connect(
                    host='10.10.10.113',
                    port=3306,
                    user='young_user',
                    password='1234',
                    database='YOUNG_CLOUD',  
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )
                cursor = conn.cursor()
                
                response = {"status": "fail", "message": "알 수 없는 요청입니다."}

                # 1. 로그인 요청 처리
                if action == "login":
                    user_id = data.get("user_id")
                    password = data.get("password")
                    
                    cursor.execute("SELECT * FROM USER WHERE EMAIL = %s AND PASSWORD_HASH = %s", (user_id, password))
                    user = cursor.fetchone()
                    
                    if user:
                        response = {
                            "status": "success", 
                            "message": "로그인 성공", 
                            "is_admin": bool(user.get('IS_ADMIN', 0)),
                            "name": user.get('NAME', '사용자')
                        }
                    else:
                        response = {"status": "fail", "message": "아이디 또는 비밀번호가 틀렸습니다."}

                # 2. 이메일 인증코드 발송 요청 처리 (서버 내부에서 직접 yagmail 처리)
                elif action == "send_email":
                    email = data.get("email")
                    if not email:
                        return {"status": "fail", "message": "이메일 주소가 입력되지 않았습니다."}
                    
                    # 6자리 랜덤 인증코드 생성
                    auth_code = str(random.randint(100000, 999999))
                    
                    sender_email = "hyun20260714@gmail.com"
                    app_password = "wucv dejb gbmx ihvd"
                    
                    try:
                        yag = yagmail.SMTP(user=sender_email, password=app_password)
                        subject = "[YOUNG CLOUD] 회원가입 이메일 인증 코드"
                        
                        # 💡 yagmail이 본문 내용을 여러 줄로 확실히 인식하도록 리스트 내 각 줄을 분리하고 
                        # 인증코드를 별도의 강조 문구로 명확하게 작성합니다.
                        contents = [
                            f"안녕하세요, YOUNG CLOUD입니다.회원가입 인증 코드는 [{auth_code}] 입니다."
                        ]
                        
                        yag.send(to=email, subject=subject, contents=contents)
                        
                        response = {
                            "status": "success", 
                            "message": "인증코드가 발송되었습니다.",
                            "auth_code": auth_code  
                        }
                    except Exception as mail_err:
                        print(f"[이메일 전송 실패] {mail_err}")
                        response = {"status": "fail", "message": "이메일 전송에 실패했습니다. 이메일 주소를 확인해주세요."}

                # 3. 회원가입 정보 등록 요청 처리 (데이터 정의서 스키마 반영)
                elif action == "signup":
                    email = data.get("email")
                    password = data.get("password")
                    name = data.get("name")
                    company = data.get("company")
                    grade_name = data.get("grade", "일반")
                    
                    # 중복 가입 체크
                    cursor.execute("SELECT * FROM USER WHERE EMAIL = %s", (email,))
                    existing_user = cursor.fetchone()
                    
                    if existing_user:
                        response = {"status": "fail", "message": "이미 가입된 이메일 계정입니다."}
                    else:
                        # 등급 이름에 따른 SERVICE_ID 조회 (없으면 기본값 1)
                        cursor.execute("SELECT `SERVICE_ID` FROM SERVICE WHERE `GRADE_NAME` = %s", (grade_name,))
                        service_row = cursor.fetchone()
                        service_id = service_row['SERVICE_ID'] if service_row else 1
                        
                        sql = """
                            INSERT INTO USER (EMAIL, PASSWORD_HASH, NAME, COMP, `SERVICE_ID`) 
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql, (email, password, name, company, service_id))
                        conn.commit()
                        
                        response = {"status": "success", "message": "회원가입이 완료되었습니다!"}
                
            except Exception as e:
                response = {"status": "error", "message": f"데이터베이스 오류: {str(e)}"}
            finally:
                if 'conn' in locals() and conn.open:
                    conn.close()

        return response
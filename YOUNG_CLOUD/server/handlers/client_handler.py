# server/client_hendler.py
import threading
import json
import pymysql
import random
import yagmail
import hashlib

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
                # ===========================================
                # 로그인 요청 처리
                # ===========================================
                if action == "login":
                    user_id = data.get("user_id")
                    password = data.get("password")
                    # 입력받은 평문 비밀번호를 SHA-256 해시 문자열로 변환
                    hashed_pw = hashlib.sha256(password.encode("utf-8")).hexdigest()
                    
                    cursor.execute(
                        "SELECT * FROM USER WHERE EMAIL = %s AND LOWER(PASSWORD_HASH) = LOWER(%s)",
                        (user_id, hashed_pw),
                    )
                    user = cursor.fetchone()
                    
                    if user:
                        # 💡 [추가된 검증 로직] 아이디/비밀번호가 맞더라도 차단(IS_BANNED)된 유저인지 확인합니다.
                        # 데이터 정의서 기준 IS_BANNED는 BOOLEAN(0 또는 1)입니다.
                        is_banned = bool(user.get('IS_BANNED', 0))
                        
                        if is_banned:
                            # 차단된 유저라면 로그인을 거부하고 메시지를 반환합니다.
                            response = {
                                "status": "fail", 
                                "message": "차단된 계정입니다. 관리자에게 문의하세요."
                            }
                        else:
                            # 정상 유저인 경우에만 로그인 성공 처리
                            response = {
                                "status": "success", 
                                "message": "로그인 성공", 
                                "email": user.get('EMAIL'),
                                "service_id": user.get('SERVICE_ID'),
                                "is_admin": bool(user.get('IS_ADMIN', 0)),
                                "is_banned": is_banned,
                                "name": user.get('NAME', '사용자')
                            }
                    else:
                        response = {"status": "fail", "message": "아이디 또는 비밀번호가 틀렸습니다."}
                # ===========================================
                # 이메일 인증코드 발송 요청 처리 (서버 내부에서 직접 yagmail 처리)
                # ===========================================
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
                # ===========================================
                # 회원가입 정보 등록 요청 처리 (데이터 정의서 스키마 반영)
                # ===========================================
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
                        # 💡 [핵심 수정] 로그인할 때와 똑같이 비밀번호를 SHA-256 해시로 암호화하여 저장합니다.
                        hashed_pw = hashlib.sha256(password.encode("utf-8")).hexdigest()
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
                # ===========================================
                # 받은 메시지 목록 조회 요청 처리
                # ==========================================
                elif action == "message_received":
                    email = data.get("email")
                    
                    # 1) 이메일로 현재 사용자의 USER_ID 조회
                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (email,))
                    user_row = cursor.fetchone()
                    if not user_row:
                        return {"status": "fail", "message": "사용자 정보를 찾을 수 없습니다."}
                    user_id = user_row['USER_ID']
                    
                    # 2) MESSAGE 테이블에서 내가 받은 메시지 조회 (보낸 사람의 이메일도 함께 가져오기 위해 JOIN 사용)
                    sql = """
                        SELECT m.MESSAGE_ID, u.EMAIL as SENDER_EMAIL, m.CONTENT, m.IS_READ, m.CREATED_AT
                        FROM MESSAGE m
                        JOIN USER u ON m.SENDER_ID = u.USER_ID
                        WHERE m.RECEIVER_ID = %s
                        ORDER BY m.CREATED_AT DESC
                    """
                    cursor.execute(sql, (user_id,))
                    messages = cursor.fetchall()
                    
                    # 날짜 형식 문자열 변환 (JSON 직렬화를 위함)
                    for msg in messages:
                        if msg.get('CREATED_AT'):
                            msg['CREATED_AT'] = str(msg['CREATED_AT'])
                            
                    response = {"status": "success", "messages": messages}
                    
                # ==========================================
                # 메시지 읽음 상태 변경 요청 처리
                # ==========================================
                elif action == "mark_message_read":
                    message_id = data.get("message_id")
                    if not message_id:
                        response = {"status": "fail", "message": "메시지 ID가 전달되지 않았습니다."}
                    else:
                        sql = "UPDATE MESSAGE SET IS_READ = 1 WHERE MESSAGE_ID = %s"
                        cursor.execute(sql, (message_id,))
                        conn.commit()
                        response = {"status": "success", "message": "메시지가 읽음 처리되었습니다."}    

                # ==========================================
                # 메시지 전송(답장 포함) 요청 처리
                # ==========================================
                elif action == "message_send":
                    sender_email = data.get("sender")
                    receiver_email = data.get("receiver")
                    content = data.get("content")
                    print(f"[DEBUG] 받는 사람: {receiver_email} / 보내는 사람: {sender_email}")
                    
                    # 송신자 정보 및 관리자 여부 조회
                    cursor.execute("SELECT USER_ID, IS_ADMIN FROM USER WHERE EMAIL = %s", (sender_email,))
                    sender_row = cursor.fetchone()
                    
                    if not sender_row:
                        response = {"status": "fail", "message": "송신자 정보를 찾을 수 없습니다."}
                    else:
                        sender_id = sender_row['USER_ID']
                        is_admin = bool(sender_row['IS_ADMIN'])
                        
                        # 관리자이고 전체 전송을 요청한 경우 (수신자가 "ALL" 또는 "전체 이용자")
                        if is_admin and receiver_email in ("ALL", "전체 이용자"):
                            cursor.execute("SELECT USER_ID FROM USER")
                            all_users = cursor.fetchall()
                            
                            sql = """
                                INSERT INTO MESSAGE (SENDER_ID, RECEIVER_ID, CONTENT, IS_READ)
                                VALUES (%s, %s, %s, FALSE)
                            """
                            for user in all_users:
                                cursor.execute(sql, (sender_id, user['USER_ID'], content))
                            conn.commit()
                            response = {"status": "success", "message": "전체 이용자에게 메시지가 성공적으로 전송되었습니다."}
                            
                        else:
                            # 일반 사용자 또는 개별 전송
                            cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (receiver_email,))
                            receiver_row = cursor.fetchone()
                            
                            if not receiver_row:
                                response = {"status": "fail", "message": "수신자 정보를 찾을 수 없습니다."}
                            else:
                                sql = """
                                    INSERT INTO MESSAGE (SENDER_ID, RECEIVER_ID, CONTENT, IS_READ)
                                    VALUES (%s, %s, %s, FALSE)
                                """
                                cursor.execute(sql, (sender_id, receiver_row['USER_ID'], content))
                                conn.commit()
                                response = {"status": "success", "message": "메시지가 성공적으로 저장 및 전송되었습니다."}

                # ==========================================
                #  메시지 삭제 요청 처리
                # ==========================================
                elif action == "message_delete":
                    message_ids = data.get("message_ids", [])
                    if not message_ids:
                        response = {"status": "fail", "message": "삭제할 메시지가 선택되지 않았습니다."}
                    else:
                        # 전달받은 ID 리스트에 해당하는 메시지 삭제
                        format_strings = ','.join(['%s'] * len(message_ids))
                        sql = f"DELETE FROM MESSAGE WHERE MESSAGE_ID IN ({format_strings})"
                        cursor.execute(sql, tuple(message_ids))
                        conn.commit()
                        response = {"status": "success", "message": "선택한 메시지가 삭제되었습니다."}

                # ==========================================
                # 보낸 메시지 목록 조회 요청 처리
                # ==========================================
                elif action == "message_sent":
                    email = data.get("email")
                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (email,))
                    user_row = cursor.fetchone()
                    if not user_row:
                        return {"status": "fail", "message": "사용자 정보를 찾을 수 없습니다."}
                    user_id = user_row['USER_ID']
                    
                    sql = """
                        SELECT m.MESSAGE_ID, u.EMAIL as RECEIVER_EMAIL, m.CONTENT, m.CREATED_AT
                        FROM MESSAGE m
                        JOIN USER u ON m.RECEIVER_ID = u.USER_ID
                        WHERE m.SENDER_ID = %s
                        ORDER BY m.CREATED_AT DESC
                    """
                    cursor.execute(sql, (user_id,))
                    messages = cursor.fetchall()
                    
                    for msg in messages:
                        if msg.get('CREATED_AT'):
                            msg['CREATED_AT'] = str(msg['CREATED_AT'])
                            
                    response = {"status": "success", "messages": messages}

                # ==========================================
                #  서비스 등급 조회 요청 처리 (NEW)
                # ==========================================
                elif action == "get_user_service":
                    email = data.get("email")
                    sql = """
                        SELECT u.EMAIL, u.SERVICE_ID, s.GRADE_NAME, s.MAX_STORAGE
                        FROM USER u
                        JOIN SERVICE s ON u.SERVICE_ID = s.SERVICE_ID
                        WHERE u.EMAIL = %s
                    """
                    cursor.execute(sql, (email,))
                    user_service = cursor.fetchone()
                    
                    if user_service:
                        response = {
                            "status": "success",
                            "service_id": user_service['SERVICE_ID'],
                            "grade_name": user_service['GRADE_NAME'],
                            "max_storage": user_service['MAX_STORAGE']
                        }
                    else:
                        response = {"status": "fail", "message": "사용자 등급 정보를 가져오지 못했습니다."}

                # ==========================================
                # 서비스 등급 변경 요청 처리 (NEW)
                # ==========================================
                elif action == "settings_tier_update":
                    email = data.get("email")
                    grade_name = data.get("grade_name")
                    service_id = data.get("service_id")

                    # 등급 이름만 넘어왔을 경우 SERVICE 테이블에서 SERVICE_ID 조회
                    if not service_id and grade_name:
                        cursor.execute("SELECT SERVICE_ID FROM SERVICE WHERE GRADE_NAME = %s", (grade_name,))
                        s_row = cursor.fetchone()
                        if s_row:
                            service_id = s_row['SERVICE_ID']

                    if not service_id:
                        response = {"status": "fail", "message": "유효하지 않은 서비스 등급 정보입니다."}
                    else:
                        cursor.execute("UPDATE USER SET SERVICE_ID = %s WHERE EMAIL = %s", (service_id, email))
                        conn.commit()
                        response = {
                            "status": "success", 
                            "message": "서비스 등급 변경 성공",
                            "service_id": service_id
                        }
                        
                # ==========================================
                #  사용자 이름 변경 요청 처리
                # ==========================================
                elif action == "update_user_name":
                    email = data.get("email")
                    name = data.get("name")
                    if not email or not name:
                        response = {"status": "fail", "message": "이름 정보가 올바르지 않습니다."}
                    else:
                        cursor.execute("UPDATE USER SET NAME = %s WHERE EMAIL = %s", (name, email))
                        conn.commit()
                        response = {"status": "success", "message": "이름이 성공적으로 변경되었습니다."}

                # ==========================================
                # 사용자 비밀번호 변경 요청 처리
                # ==========================================
                elif action == "update_user_password":
                    email = data.get("email")
                    password = data.get("password")
                    if not email or not password:
                        response = {"status": "fail", "message": "비밀번호 정보가 올바르지 않습니다."}
                    else:
                        hashed_pw = hashlib.sha256(password.encode("utf-8")).hexdigest()
                        cursor.execute("UPDATE USER SET PASSWORD_HASH = %s WHERE EMAIL = %s", (hashed_pw, email))
                        conn.commit()
                        response = {"status": "success", "message": "비밀번호가 성공적으로 변경되었습니다."}                                     
                
                
            
            
            
            
            
            
            
            
            
            
            
            
            # ==========================================
                # 💡 [추가] 사용자의 클라우드 용량 및 등급 정보 조회 요청 처리
                # ==========================================
                elif action == "get_user_storage_info":
                    email = data.get("email")
                    
                    # 1. 사용자 정보 및 서비스 등급 조회
                    cursor.execute("""
                        SELECT u.USER_ID, s.GRADE_NAME, s.MAX_STORAGE
                        FROM USER u
                        JOIN SERVICE s ON u.SERVICE_ID = s.SERVICE_ID
                        WHERE u.EMAIL = %s
                    """, (email,))
                    user_row = cursor.fetchone()
                    
                    if not user_row:
                        response = {"status": "fail", "message": "사용자 정보를 찾을 수 없습니다."}
                    else:
                        user_id = user_row['USER_ID']
                        grade_name = user_row['GRADE_NAME']
                        max_storage = user_row['MAX_STORAGE'] # 바이트(Bytes) 단위 등급별 최대 용량
                        
                        # 2. FILE 테이블에서 해당 사용자가 업로드한 파일들의 총 용량 계산 (STATUS가 COMPLETED이거나 전체)
                        cursor.execute("""
                            SELECT SUM(FILE_SIZE) as TOTAL_USED 
                            FROM FILE 
                            WHERE USER_ID = %s
                        """, (user_id,))
                        storage_row = cursor.fetchone()
                        
                        total_used = storage_row['TOTAL_USED'] if storage_row and storage_row['TOTAL_USED'] else 0
                        
                        response = {
                            "status": "success",
                            "grade_name": grade_name,
                            "max_storage": max_storage,
                            "total_used": total_used
                        }
            
            
            
            
            
            
            
            
                # ==========================================
                # 💡 [관리자] 전체 이용자 목록 조회 요청 처리
                # ==========================================
                elif action == "admin_get_users":
                    # USER 테이블과 SERVICE 테이블을 조인하여 이용자 이메일, 이름, 등급명, 차단상태(IS_BANNED)를 조회합니다.
                    sql = """
                        SELECT u.EMAIL, u.NAME, s.GRADE_NAME, u.IS_BANNED
                        FROM USER u
                        JOIN SERVICE s ON u.SERVICE_ID = s.SERVICE_ID
                        ORDER BY u.CREATED_AT DESC
                    """
                    cursor.execute(sql)
                    users = cursor.fetchall()
                    
                    response = {"status": "success", "users": users}

                # ==========================================
                # 💡 [관리자] 사용자 차단 상태 변경(정지/해제) 요청 처리
                # ==========================================
                elif action == "admin_update_ban":
                    email = data.get("email")
                    is_banned = data.get("is_banned") # True(차단) 또는 False(정상)
                    
                    if not email:
                        response = {"status": "fail", "message": "사용자 이메일 정보가 전달되지 않았습니다."}
                    else:
                        # 데이터 정의서에 따라 IS_BANNED 컬럼 값을 1(True) 또는 0(False)으로 업데이트합니다[cite: 6].
                        banned_val = 1 if is_banned else 0
                        sql = "UPDATE USER SET IS_BANNED = %s WHERE EMAIL = %s"
                        cursor.execute(sql, (banned_val, email))
                        conn.commit()
                        
                        status_text = "차단" if is_banned else "차단 해제"
                        response = {"status": "success", "message": f"해당 사용자가 성공적으로 {status_text}되었습니다."}
            
            
            
                
                
                
            except Exception as e:
                response = {"status": "error", "message": f"데이터베이스 오류: {str(e)}"}
            finally:
                if 'conn' in locals() and conn.open:
                    conn.close()

        return response
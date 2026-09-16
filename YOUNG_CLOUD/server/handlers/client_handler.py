import threading
import json
import pymysql
import random
import yagmail
import hashlib
import os
import base64

# 서버 측 클라우드 저장소 기본 디렉토리 설정 (cloud_storage)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUD_STORAGE_DIR = os.path.join(BASE_DIR, "cloud_storage")
os.makedirs(CLOUD_STORAGE_DIR, exist_ok=True)

class ClientHandler(threading.Thread):
    def __init__(self, client_sock, client_addr, db_lock):
        super().__init__()
        self.client_sock = client_sock
        self.client_addr = client_addr
        self.db_lock = db_lock

    def run(self):
        try:
            while True:
                # 대용량 파라미터/파일 데이터 수신을 위한 소켓 처리
                buffer = ""
                while True:
                    chunk = self.client_sock.recv(4096).decode('utf-8')
                    if not chunk:
                        break
                    buffer += chunk
                    try:
                        request = json.loads(buffer)
                        break
                    except json.JSONDecodeError:
                        continue  # 데이터가 완벽히 들어올 때까지 수신 반복

                if not buffer:
                    break

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
                # 1. 로그인 요청 처리
                # ===========================================
                if action == "login":
                    user_id = data.get("user_id")
                    password = data.get("password")
                    hashed_pw = hashlib.sha256(password.encode("utf-8")).hexdigest()
                    
                    cursor.execute(
                        "SELECT * FROM USER WHERE EMAIL = %s AND LOWER(PASSWORD_HASH) = LOWER(%s)",
                        (user_id, hashed_pw),
                    )
                    user = cursor.fetchone()
                    
                    if user:
                        response = {
                            "status": "success", 
                            "message": "로그인 성공", 
                            "email": user.get('EMAIL'),
                            "service_id": user.get('SERVICE_ID'),
                            "is_admin": bool(user.get('IS_ADMIN', 0)),
                            "is_banned": bool(user.get('IS_BANNED', 0)),
                            "name": user.get('NAME', '사용자')
                        }
                    else:
                        response = {"status": "fail", "message": "아이디 또는 비밀번호가 틀렸습니다."}

                # ===========================================
                # 2. 이메일 인증코드 발송 요청 처리
                # ===========================================
                elif action == "send_email":
                    email = data.get("email")
                    if not email:
                        return {"status": "fail", "message": "이메일 주소가 입력되지 않았습니다."}
                    
                    auth_code = str(random.randint(100000, 999999))
                    sender_email = "hyun20260714@gmail.com"
                    app_password = "wucv dejb gbmx ihvd"
                    
                    try:
                        yag = yagmail.SMTP(user=sender_email, password=app_password)
                        subject = "[YOUNG CLOUD] 회원가입 이메일 인증 코드"
                        contents = [f"안녕하세요, YOUNG CLOUD입니다. 회원가입 인증 코드는 [{auth_code}] 입니다."]
                        yag.send(to=email, subject=subject, contents=contents)
                        
                        response = {
                            "status": "success", 
                            "message": "인증코드가 발송되었습니다.",
                            "auth_code": auth_code  
                        }
                    except Exception as mail_err:
                        print(f"[이메일 전송 실패] {mail_err}")
                        response = {"status": "fail", "message": "이메일 전송에 실패했습니다."}

                # ===========================================
                # 3. 회원가입 요청 처리
                # ===========================================
                elif action == "signup":
                    email = data.get("email")
                    password = data.get("password")
                    name = data.get("name")
                    company = data.get("company")
                    grade_name = data.get("grade", "일반")
                    
                    cursor.execute("SELECT * FROM USER WHERE EMAIL = %s", (email,))
                    if cursor.fetchone():
                        response = {"status": "fail", "message": "이미 가입된 이메일 계정입니다."}
                    else:
                        cursor.execute("SELECT `SERVICE_ID` FROM SERVICE WHERE `GRADE_NAME` = %s", (grade_name,))
                        service_row = cursor.fetchone()
                        service_id = service_row['SERVICE_ID'] if service_row else 1
                        
                        sql = "INSERT INTO USER (EMAIL, PASSWORD_HASH, NAME, COMP, `SERVICE_ID`) VALUES (%s, %s, %s, %s, %s)"
                        cursor.execute(sql, (email, password, name, company, service_id))
                        conn.commit()
                        response = {"status": "success", "message": "회원가입이 완료되었습니다!"}

                # ===========================================
                # 4. 받은 메시지 목록 조회 요청 처리
                # ===========================================
                elif action == "message_received":
                    email = data.get("email")
                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (email,))
                    user_row = cursor.fetchone()
                    if not user_row:
                        return {"status": "fail", "message": "사용자 정보를 찾을 수 없습니다."}
                    
                    sql = """
                        SELECT m.MESSAGE_ID, u.EMAIL as SENDER_EMAIL, m.CONTENT, m.IS_READ, m.CREATED_AT
                        FROM MESSAGE m
                        JOIN USER u ON m.SENDER_ID = u.USER_ID
                        WHERE m.RECEIVER_ID = %s
                        ORDER BY m.CREATED_AT DESC
                    """
                    cursor.execute(sql, (user_row['USER_ID'],))
                    messages = cursor.fetchall()
                    for msg in messages:
                        if msg.get('CREATED_AT'):
                            msg['CREATED_AT'] = str(msg['CREATED_AT'])
                    response = {"status": "success", "messages": messages}

                # ==========================================
                # 5. 메시지 전송 요청 처리
                # ==========================================
                elif action == "message_send":
                    sender_email = data.get("sender")
                    receiver_email = data.get("receiver")
                    content = data.get("content")
                    
                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (sender_email,))
                    sender_row = cursor.fetchone()
                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (receiver_email,))
                    receiver_row = cursor.fetchone()
                    
                    if not sender_row or not receiver_row:
                        response = {"status": "fail", "message": "수신자 또는 송신자 정보를 찾을 수 없습니다."}
                    else:
                        sql = "INSERT INTO MESSAGE (SENDER_ID, RECEIVER_ID, CONTENT, IS_READ) VALUES (%s, %s, %s, FALSE)"
                        cursor.execute(sql, (sender_row['USER_ID'], receiver_row['USER_ID'], content))
                        conn.commit()
                        response = {"status": "success", "message": "메시지가 성공적으로 저장 및 전송되었습니다."}

                # ==========================================
                # 6. 메시지 삭제 요청 처리
                # ==========================================
                elif action == "message_delete":
                    message_ids = data.get("message_ids", [])
                    if not message_ids:
                        response = {"status": "fail", "message": "삭제할 메시지가 선택되지 않았습니다."}
                    else:
                        format_strings = ','.join(['%s'] * len(message_ids))
                        sql = f"DELETE FROM MESSAGE WHERE MESSAGE_ID IN ({format_strings})"
                        cursor.execute(sql, tuple(message_ids))
                        conn.commit()
                        response = {"status": "success", "message": "선택한 메시지가 삭제되었습니다."}

                # ==========================================
                # 7. 메시지 읽음 상태 변경 요청 처리
                # ==========================================
                elif action == "mark_message_read":
                    message_id = data.get("message_id")
                    if not message_id:
                        response = {"status": "fail", "message": "메시지 ID가 전달되지 않았습니다."}
                    else:
                        cursor.execute("UPDATE MESSAGE SET IS_READ = 1 WHERE MESSAGE_ID = %s", (message_id,))
                        conn.commit()
                        response = {"status": "success", "message": "메시지가 읽음 처리되었습니다."}

                # ==========================================
                # 8. 보낸 메시지 목록 조회 요청 처리
                # ==========================================
                elif action == "message_sent":
                    email = data.get("email")
                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (email,))
                    user_row = cursor.fetchone()
                    if not user_row:
                        return {"status": "fail", "message": "사용자 정보를 찾을 수 없습니다."}
                    
                    sql = """
                        SELECT m.MESSAGE_ID, u.EMAIL as RECEIVER_EMAIL, m.CONTENT, m.CREATED_AT
                        FROM MESSAGE m
                        JOIN USER u ON m.RECEIVER_ID = u.USER_ID
                        WHERE m.SENDER_ID = %s
                        ORDER BY m.CREATED_AT DESC
                    """
                    cursor.execute(sql, (user_row['USER_ID'],))
                    messages = cursor.fetchall()
                    for msg in messages:
                        if msg.get('CREATED_AT'):
                            msg['CREATED_AT'] = str(msg['CREATED_AT'])
                    response = {"status": "success", "messages": messages}

                # ==========================================
                # 9. 클라우드 파일 목록 조회 (바탕화면 표시용)
                # ==========================================
                elif action == "cloud_list_files":
                    email = data.get("email")
                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (email,))
                    user_row = cursor.fetchone()

                    if user_row:
                        sql = """
                            SELECT FILE_ID, FILE_NAME, FILE_SIZE, CREATED_AT 
                            FROM FILE 
                            WHERE USER_ID = %s AND IS_TRASH = 0 
                            ORDER BY CREATED_AT DESC
                        """
                        cursor.execute(sql, (user_row['USER_ID'],))
                        files = cursor.fetchall()
                        for f in files:
                            if f.get('CREATED_AT'):
                                f['CREATED_AT'] = str(f['CREATED_AT'])
                        response = {"status": "success", "file_list": files}
                    else:
                        response = {"status": "fail", "message": "사용자 정보를 찾을 수 없습니다."}

                # ==========================================
                # 10. 클라우드 파일 업로드 (디스크 저장 + DB 기록)
                # ==========================================
                elif action == "cloud_upload":
                    email = data.get("email")
                    file_name = data.get("file_name")
                    file_size = data.get("file_size")
                    file_data_b64 = data.get("file_data")

                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (email,))
                    user_row = cursor.fetchone()

                    if user_row:
                        user_id = user_row["USER_ID"]
                        # 디스크에 바이너리 파일 저장
                        user_dir = os.path.join(UPLOAD_DIR, str(user_id))
                        os.makedirs(user_dir, exist_ok=True)
                        save_path = os.path.join(user_dir, file_name)

                        file_bytes = base64.b64decode(file_data_b64)
                        with open(save_path, "wb") as f:
                            f.write(file_bytes)

                        # DB 저장
                        sql = """
                            INSERT INTO FILE (USER_ID, FILE_NAME, FILE_SIZE, FILE_PATH, IS_TRASH, CREATED_AT)
                            VALUES (%s, %s, %s, %s, 0, NOW())
                        """
                        cursor.execute(sql, (user_id, file_name, file_size, save_path))
                        conn.commit()

                        response = {"status": "success", "message": f"{file_name} 업로드 완료"}
                    else:
                        response = {"status": "fail", "message": "사용자 정보가 존재하지 않습니다."}

                # ==========================================
                # 11. 클라우드 파일 다운로드 (디스크 파일 읽기 -> Base64 전달)
                # ==========================================
                elif action == "cloud_download":
                    file_id = data.get("file_id")
                    cursor.execute("SELECT * FROM FILE WHERE FILE_ID = %s", (file_id,))
                    file_info = cursor.fetchone()

                    if file_info and os.path.exists(file_info["FILE_PATH"]):
                        with open(file_info["FILE_PATH"], "rb") as f:
                            encoded_bytes = base64.b64encode(f.read()).decode('utf-8')
                        
                        response = {
                            "status": "success",
                            "file_data": {
                                "file_id": file_info["FILE_ID"],
                                "file_name": file_info["FILE_NAME"],
                                "file_bytes_base64": encoded_bytes
                            }
                        }
                    else:
                        response = {"status": "fail", "message": "파일이 서버 존재하지 않거나 DB 정보를 찾을 수 없습니다."}

                # ==========================================
                # 12. 파일 휴지통 이동
                # ==========================================
                elif action == "cloud_move_to_trash":
                    file_id = data.get("file_id")
                    cursor.execute("UPDATE FILE SET IS_TRASH = 1 WHERE FILE_ID = %s", (file_id,))
                    conn.commit()
                    response = {"status": "success", "message": "휴지통으로 이동했습니다."}

                # ==========================================
                # 13. 파일 영구 삭제 (실제 파일 삭제 + DB 삭제)
                # ==========================================
                elif action == "cloud_delete_permanently":
                    file_id = data.get("file_id")
                    cursor.execute("SELECT FILE_PATH FROM FILE WHERE FILE_ID = %s", (file_id,))
                    file_row = cursor.fetchone()
                    if file_row and os.path.exists(file_row["FILE_PATH"]):
                        os.remove(file_row["FILE_PATH"])

                    cursor.execute("DELETE FROM FILE WHERE FILE_ID = %s", (file_id,))
                    conn.commit()
                    response = {"status": "success", "message": "파일이 영구 삭제되었습니다."}

            except Exception as e:
                response = {"status": "error", "message": f"데이터베이스 오류: {str(e)}"}
            finally:
                if 'conn' in locals() and conn.open:
                    conn.close()

        return response
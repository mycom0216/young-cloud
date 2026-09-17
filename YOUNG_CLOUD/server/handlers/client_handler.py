import threading
import json
import pymysql
import random
import yagmail
import hashlib
import os
import base64
from datetime import datetime, date

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
                # 바이트 버퍼로 수신하여 한글/대용량 데이터 분할 수신 안전성 확보
                raw_buffer = b""
                while True:
                    chunk = self.client_sock.recv(4096)
                    if not chunk:
                        break
                    raw_buffer += chunk
                    try:
                        # 완벽한 JSON 형태가 수신될 때까지 디코딩 및 파싱 시도
                        request = json.loads(raw_buffer.decode('utf-8'))
                        break
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue  

                if not raw_buffer:
                    break

                response = self.route_request(request)
                self.client_sock.sendall(json.dumps(response, default=str).encode('utf-8'))
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
                    email = data.get("email") or data.get("user_id")
                    password = data.get("password")
                    if not email or not password:
                        response = {"status": "fail", "message": "이메일과 비밀번호를 입력해주세요."}
                    else:
                        # DB 트리거가 INSERT/UPDATE 시 SHA2(password, 256)을 수행하므로
                        # 로그인 조회 시에도 SHA2() 함수를 이용해 비교합니다.
                        sql = "SELECT * FROM USER WHERE EMAIL = %s AND PASSWORD_HASH = SHA2(%s, 256)"
                        cursor.execute(sql, (email, password))
                        user = cursor.fetchone()
                        # 3. 조회 결과(user) 존재 여부 검증
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
                # 3. 회원가입 정보 등록 요청 처리
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
                        hashed_pw = hashlib.sha256(password.encode("utf-8")).hexdigest()
                        # 등급 이름에 따른 SERVICE_ID 조회 (없으면 기본값 1)
                        cursor.execute("SELECT `SERVICE_ID` FROM SERVICE WHERE `GRADE_NAME` = %s", (grade_name,))
                        service_row = cursor.fetchone()
                        service_id = service_row['SERVICE_ID'] if service_row else 1
                        
                        sql = "INSERT INTO USER (EMAIL, PASSWORD_HASH, NAME, COMP, `SERVICE_ID`) VALUES (%s, %s, %s, %s, %s)"
                        cursor.execute(sql, (email, password, name, company, service_id)) # 평문 전달 -> 트리거가 해싱
                        conn.commit()
                        response = {"status": "success", "message": "회원가입이 완료되었습니다!"}

                # ===========================================
                # 4. 메시지 기능 처리
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

                elif action == "message_send":
                    sender_email = data.get("sender")
                    receiver_email = data.get("receiver")
                    content = data.get("content")
                    
                    cursor.execute("SELECT USER_ID, IS_ADMIN FROM USER WHERE EMAIL = %s", (sender_email,))
                    sender_row = cursor.fetchone()
                    
                    if not sender_row:
                        response = {"status": "fail", "message": "송신자 정보를 찾을 수 없습니다."}
                    else:
                        sender_id = sender_row['USER_ID']
                        is_admin = bool(sender_row['IS_ADMIN'])
                        
                        if is_admin and receiver_email in ("ALL", "전체 이용자"):
                            cursor.execute("SELECT USER_ID FROM USER")
                            all_users = cursor.fetchall()
                            sql = "INSERT INTO MESSAGE (SENDER_ID, RECEIVER_ID, CONTENT, IS_READ) VALUES (%s, %s, %s, FALSE)"
                            for user in all_users:
                                cursor.execute(sql, (sender_id, user['USER_ID'], content))
                            conn.commit()
                            response = {"status": "success", "message": "전체 이용자에게 메시지가 전송되었습니다."}
                        else:
                            cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (receiver_email,))
                            receiver_row = cursor.fetchone()
                            if not receiver_row:
                                response = {"status": "fail", "message": "수신자 정보를 찾을 수 없습니다."}
                            else:
                                sql = "INSERT INTO MESSAGE (SENDER_ID, RECEIVER_ID, CONTENT, IS_READ) VALUES (%s, %s, %s, FALSE)"
                                cursor.execute(sql, (sender_id, receiver_row['USER_ID'], content))
                                conn.commit()
                                response = {"status": "success", "message": "메시지가 전송되었습니다."}

                elif action == "mark_message_read":
                    message_id = data.get("message_id")
                    if not message_id:
                        response = {"status": "fail", "message": "메시지 ID가 전달되지 않았습니다."}
                    else:
                        cursor.execute("UPDATE MESSAGE SET IS_READ = 1 WHERE MESSAGE_ID = %s", (message_id,))
                        conn.commit()
                        response = {"status": "success", "message": "메시지가 읽음 처리되었습니다."}

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

                # ===========================================
                # 5. 개인정보 및 설정 변경 처리
                # ===========================================
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

                elif action == "settings_tier_update":
                    email = data.get("email")
                    grade_name = data.get("grade_name")
                    service_id = data.get("service_id")

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
                        response = {"status": "success", "message": "서비스 등급 변경 성공", "service_id": service_id}

                elif action == "update_user_name":
                    email = data.get("email")
                    name = data.get("name")
                    cursor.execute("UPDATE USER SET NAME = %s WHERE EMAIL = %s", (name, email))
                    conn.commit()
                    response = {"status": "success", "message": "이름이 성공적으로 변경되었습니다."}

                elif action == "update_user_password":
                    email = data.get("email")
                    password = data.get("password") or data.get("new_password")
                    if not email or not password:
                        response = {"status": "fail", "message": "비밀번호 정보가 올바르지 않습니다."}
                    else:
                    # hashlib 해싱을 제거하고 평문 전달 -> UPDATE 트리거가 해싱 처리
                        cursor.execute("UPDATE USER SET PASSWORD_HASH = %s WHERE EMAIL = %s", (password, email))
                        conn.commit()
                        response = {"status": "success", "message": "비밀번호가 성공적으로 변경되었습니다."}

                # ===========================================
                # 6. 클라우드 파일 업로드/다운로드/목록/휴지통 처리
                # ===========================================
                elif action in ("cloud_upload_file", "upload_file"):
                    user_id_input = data.get("user_id") or data.get("email")
                    file_name = data.get("file_name")
                    file_b64 = data.get("file_data")
                    folder_path = data.get("folder_path", "/")

                    if not user_id_input or not file_name or not file_b64:
                        response = {"status": "fail", "message": "파일 업로드 필수 정보가 누락되었습니다."}
                    else:
                        cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s OR USER_ID = %s", (user_id_input, user_id_input))
                        u_row = cursor.fetchone()
                        if not u_row:
                            response = {"status": "fail", "message": "사용자 정보를 찾을 수 없습니다."}
                        else:
                            user_id = u_row['USER_ID']
                            user_dir = os.path.join(CLOUD_STORAGE_DIR, str(user_id))
                            
                            # 하위 폴더 경로까지 포함하여 디렉토리 자동 생성
                            clean_folder_path = folder_path.strip("/\\")
                            target_dir = os.path.join(user_dir, clean_folder_path) if clean_folder_path else user_dir
                            os.makedirs(target_dir, exist_ok=True)
                            
                            save_path = os.path.join(target_dir, file_name)
                            file_bytes = base64.b64decode(file_b64)
                            file_size = len(file_bytes)
                            
                            with open(save_path, "wb") as f:
                                f.write(file_bytes)
                            
                            # DB 기록 (중복 파일은 업데이트)
                            cursor.execute("""
                                SELECT FILE_ID FROM FILE 
                                WHERE USER_ID = %s AND FILE_NAME = %s AND FOLDER_PATH = %s
                            """, (user_id, file_name, folder_path))
                            exist_file = cursor.fetchone()

                            if exist_file:
                                cursor.execute("""
                                    UPDATE FILE 
                                    SET FILE_SIZE = %s, FILE_PATH = %s, IS_TRASH = 0, UPDATED_AT = NOW() 
                                    WHERE FILE_ID = %s
                                """, (file_size, save_path, exist_file['FILE_ID']))
                            else:
                                cursor.execute("""
                                    INSERT INTO FILE (USER_ID, FILE_NAME, FILE_SIZE, FILE_PATH, FOLDER_PATH, IS_TRASH)
                                    VALUES (%s, %s, %s, %s, %s, 0)
                                """, (user_id, file_name, file_size, save_path, folder_path))

                            conn.commit()
                            response = {"status": "success", "message": "파일 업로드가 완료되었습니다."}

                elif action in ("cloud_download_file", "download_file"):
                    file_id = data.get("file_id")
                    cursor.execute("SELECT FILE_NAME, FILE_PATH FROM FILE WHERE FILE_ID = %s", (file_id,))
                    f_row = cursor.fetchone()
                    if f_row and os.path.exists(f_row['FILE_PATH']):
                        with open(f_row['FILE_PATH'], "rb") as f:
                            file_b64 = base64.b64encode(f.read()).decode('utf-8')
                        response = {
                            "status": "success",
                            "file_name": f_row['FILE_NAME'],
                            "file_data": file_b64
                        }
                    else:
                        response = {"status": "fail", "message": "파일을 찾을 수 없거나 파일이 존재하지 않습니다."}

                elif action == "cloud_list_files":
                    user_id_input = data.get("user_id") or data.get("email")
                    folder_path = data.get("folder_path", "/")
                    
                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s OR USER_ID = %s", (user_id_input, user_id_input))
                    u_row = cursor.fetchone()
                    if not u_row:
                        response = {"status": "fail", "message": "사용자 정보가 존재하지 않습니다."}
                    else:
                        sql = """
                            SELECT FILE_ID, FILE_NAME, FILE_SIZE, UPDATED_AT, IS_TRASH
                            FROM FILE
                            WHERE USER_ID = %s AND IS_TRASH = 0 AND FOLDER_PATH = %s
                            ORDER BY UPDATED_AT DESC
                        """
                        cursor.execute(sql, (u_row['USER_ID'], folder_path))
                        files = cursor.fetchall()
                        response = {"status": "success", "files": files}

                elif action == "cloud_trash_list":
                    user_id_input = data.get("user_id") or data.get("email")
                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s OR USER_ID = %s", (user_id_input, user_id_input))
                    u_row = cursor.fetchone()
                    if not u_row:
                        response = {"status": "fail", "message": "사용자 정보가 존재하지 않습니다."}
                    else:
                        sql = """
                            SELECT FILE_ID, FILE_NAME, FILE_SIZE, UPDATED_AT
                            FROM FILE
                            WHERE USER_ID = %s AND IS_TRASH = 1
                            ORDER BY UPDATED_AT DESC
                        """
                        cursor.execute(sql, (u_row['USER_ID'],))
                        files = cursor.fetchall()
                        response = {"status": "success", "files": files}

                elif action == "cloud_delete_file":
                    file_id = data.get("file_id")
                    cursor.execute("UPDATE FILE SET IS_TRASH = 1 WHERE FILE_ID = %s", (file_id,))
                    conn.commit()
                    response = {"status": "success", "message": "휴지통으로 이동되었습니다."}

                elif action == "cloud_restore_file":
                    file_id = data.get("file_id")
                    cursor.execute("UPDATE FILE SET IS_TRASH = 0 WHERE FILE_ID = %s", (file_id,))
                    conn.commit()
                    response = {"status": "success", "message": "복구되었습니다."}

                elif action == "cloud_permanent_delete":
                    file_id = data.get("file_id")
                    cursor.execute("SELECT FILE_PATH FROM FILE WHERE FILE_ID = %s", (file_id,))
                    f_row = cursor.fetchone()
                    if f_row and os.path.exists(f_row['FILE_PATH']):
                        try:
                            os.remove(f_row['FILE_PATH'])
                        except Exception:
                            pass
                    cursor.execute("DELETE FROM FILE WHERE FILE_ID = %s", (file_id,))
                    conn.commit()
                    response = {"status": "success", "message": "영구 삭제되었습니다."}

                elif action == "cloud_storage_info":
                    user_id_input = data.get("user_id") or data.get("email")
                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s OR USER_ID = %s", (user_id_input, user_id_input))
                    u_row = cursor.fetchone()
                    if u_row:
                        cursor.execute("SELECT IFNULL(SUM(FILE_SIZE), 0) AS USED FROM FILE WHERE USER_ID = %s AND IS_TRASH = 0", (u_row['USER_ID'],))
                        used = cursor.fetchone()['USED']
                        response = {"status": "success", "used_bytes": used}
                    else:
                        response = {"status": "fail", "message": "사용자 조회 실패"}

                # ===========================================
                # 7. [관리자] 사용자 정지/해제 관리
                # ===========================================
                elif action == "admin_get_users":
                    sql = """
                        SELECT u.EMAIL, u.NAME, s.GRADE_NAME, u.IS_BANNED
                        FROM USER u
                        JOIN SERVICE s ON u.SERVICE_ID = s.SERVICE_ID
                        ORDER BY u.CREATED_AT DESC
                    """
                    cursor.execute(sql)
                    users = cursor.fetchall()
                    response = {"status": "success", "users": users}

                elif action == "admin_update_ban":
                    email = data.get("email")
                    is_banned = data.get("is_banned")
                    if not email:
                        response = {"status": "fail", "message": "사용자 이메일 정보가 전달되지 않았습니다."}
                    else:
                        banned_val = 1 if is_banned else 0
                        cursor.execute("UPDATE USER SET IS_BANNED = %s WHERE EMAIL = %s", (banned_val, email))
                        conn.commit()
                        status_text = "차단" if is_banned else "차단 해제"
                        response = {"status": "success", "message": f"해당 사용자가 성공적으로 {status_text}되었습니다."}

            except Exception as e:
                response = {"status": "error", "message": f"데이터베이스 오류: {str(e)}"}
            finally:
                if 'conn' in locals() and conn.open:
                    conn.close()

        return response
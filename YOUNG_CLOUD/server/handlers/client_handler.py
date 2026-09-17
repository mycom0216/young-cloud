import threading
import json
import pymysql
import random
import yagmail
import hashlib
import os
import base64
import struct  # 💡 4바이트 길이 헤더 처리를 위해 추가
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
        
    def _recv_all(self, n):
        """지정한 n 바이트를 모두 수신할 때까지 반복 수신하는 Helper 함수"""
        data = bytearray()
        while len(data) < n:
            packet = self.client_sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    def run(self):
        try:
            while True:
                # 1. 클라이언트 요청의 4바이트 길이 헤더 수신
                raw_length = self._recv_all(4)
                if not raw_length:
                    break

                data_length = struct.unpack('>I', raw_length)[0]

                # 2. 지정된 데이터 길이만큼 요청 바디 완벽 수신
                body_bytes = self._recv_all(data_length)
                if not body_bytes:
                    break

                request = json.loads(body_bytes.decode('utf-8'))

                # 3. 비즈니스 로직 처리
                response = self.route_request(request)

                # 4. 클라이언트로 응답 전송 (4바이트 길이 헤더 + JSON 응답 바디)
                response_bytes = json.dumps(response, default=str).encode('utf-8')
                header = struct.pack('>I', len(response_bytes))
                self.client_sock.sendall(header + response_bytes)

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
                # 6. 클라우드: 파일/폴더 목록 조회
                # ===========================================
                elif action == "cloud_list_files":
                    email = data.get("email")
                    parent_folder_id = data.get("parent_folder_id")  # None이면 루트 폴더

                    cursor.execute("SELECT USER_ID, NAME, EMAIL, COMP FROM USER WHERE EMAIL = %s", (email,))
                    user = cursor.fetchone()
                    if not user:
                        response = {"status": "fail", "message": "사용자 정보를 찾을 수 없습니다."}
                    else:
                        user_id = user['USER_ID']
                        user_name = user['NAME']
                        comp_name = user['COMP'] or "DEFAULT_COMP"

                        # DB에서 PARENT_FOLDER_ID 기준으로 하위 폴더 조회
                        if parent_folder_id:
                            cursor.execute("""
                                SELECT FOLDER_ID, FOLDER_NAME, RELATIVE_PATH, CREATED_AT
                                FROM FOLDER
                                WHERE USER_ID = %s AND PARENT_FOLDER_ID = %s
                            """, (user_id, parent_folder_id))
                        else:
                            cursor.execute("""
                                SELECT FOLDER_ID, FOLDER_NAME, RELATIVE_PATH, CREATED_AT
                                FROM FOLDER
                                WHERE USER_ID = %s AND PARENT_FOLDER_ID IS NULL
                            """, (user_id,))
                        folders = cursor.fetchall()

                        # DB에서 FOLDER_ID 기준으로 파일 목록 조회
                        if parent_folder_id:
                            cursor.execute("""
                                SELECT FILE_ID, FOLDER_ID, FILE_NAME, ORIGINAL_NAME, FILE_SIZE, STATUS, UPLOADED_AT
                                FROM FILE
                                WHERE USER_ID = %s AND FOLDER_ID = %s AND STATUS != 'TRASH'
                            """, (user_id, parent_folder_id))
                        else:
                            cursor.execute("""
                                SELECT FILE_ID, FOLDER_ID, FILE_NAME, ORIGINAL_NAME, FILE_SIZE, STATUS, UPLOADED_AT
                                FROM FILE
                                WHERE USER_ID = %s AND FOLDER_ID IS NULL AND STATUS != 'TRASH'
                            """, (user_id,))
                        files = cursor.fetchall()

                        response = {
                            "status": "success",
                            "user_name": user_name,
                            "comp_name": comp_name,
                            "folders": folders,
                            "files": files
                        }

                # ===========================================
                # 6-1. 클라우드: 새 폴더 생성 (FOLDER_TYPE을 'USER'로 수정)
                # ===========================================
                elif action == "cloud_create_folder":
                    email = data.get("email")
                    folder_name = data.get("folder_name")
                    parent_folder_id = data.get("parent_folder_id")

                    cursor.execute("SELECT USER_ID, COMP, EMAIL FROM USER WHERE EMAIL = %s", (email,))
                    user = cursor.fetchone()
                    if not user:
                        response = {"status": "fail", "message": "사용자 정보가 존재하지 않습니다."}
                    else:
                        user_id = user['USER_ID']
                        comp = user['COMP'] or "DEFAULT_COMP"
                        user_email = user['EMAIL']

                        parent_rel_path = ""
                        if parent_folder_id:
                            cursor.execute("SELECT RELATIVE_PATH FROM FOLDER WHERE FOLDER_ID = %s", (parent_folder_id,))
                            p_row = cursor.fetchone()
                            if p_row and p_row.get('RELATIVE_PATH'):
                                parent_rel_path = p_row['RELATIVE_PATH']

                        rel_path = os.path.join(parent_rel_path, folder_name).replace("\\", "/")
                        physical_dir = os.path.join(CLOUD_STORAGE_DIR, comp, user_email, rel_path)
                        os.makedirs(physical_dir, exist_ok=True)

                        # FOLDER_TYPE을 DB enum에 정의된 'USER'로 지정
                        sql = """
                            INSERT INTO FOLDER (COMP, USER_ID, FOLDER_NAME, FOLDER_TYPE, PARENT_FOLDER_ID, RELATIVE_PATH)
                            VALUES (%s, %s, %s, 'USER', %s, %s)
                        """
                        cursor.execute(sql, (comp, user_id, folder_name, parent_folder_id, rel_path))
                        conn.commit()

                        response = {"status": "success", "message": "폴더가 생겼습니다."}

                # ===========================================
                # 6-2. 클라우드: 파일 업로드 (FOLDER_ID NULL 허용 반영)
                # ===========================================
                elif action == "cloud_upload":
                    email = data.get("email")
                    file_name = data.get("file_name")
                    file_size = data.get("file_size")
                    file_b64 = data.get("file_data")
                    folder_id = data.get("folder_id")

                    cursor.execute("SELECT USER_ID, COMP, EMAIL FROM USER WHERE EMAIL = %s", (email,))
                    user = cursor.fetchone()
                    if not user:
                        response = {"status": "fail", "message": "사용자 정보를 찾을 수 없습니다."}
                    else:
                        user_id = user['USER_ID']
                        comp = user['COMP'] or "DEFAULT_COMP"
                        user_email = user['EMAIL']

                        rel_path = ""
                        if folder_id:
                            cursor.execute("SELECT RELATIVE_PATH FROM FOLDER WHERE FOLDER_ID = %s", (folder_id,))
                            f_row = cursor.fetchone()
                            if f_row and f_row.get('RELATIVE_PATH'):
                                rel_path = f_row['RELATIVE_PATH']

                        physical_dir = os.path.join(CLOUD_STORAGE_DIR, comp, user_email, rel_path)
                        os.makedirs(physical_dir, exist_ok=True)

                        physical_file_path = os.path.join(physical_dir, file_name)
                        file_bytes = base64.b64decode(file_b64)

                        with open(physical_file_path, "wb") as f:
                            f.write(file_bytes)

                        # folder_id가 미지정/None인 경우 DB에 NULL로 안심 저장
                        sql = """
                            INSERT INTO FILE (FOLDER_ID, USER_ID, FILE_NAME, ORIGINAL_NAME, FILE_PATH, FILE_SIZE, STATUS)
                            VALUES (%s, %s, %s, %s, %s, %s, 'COMPLETED')
                        """
                        cursor.execute(sql, (folder_id if folder_id else None, user_id, file_name, file_name, physical_file_path, file_size))
                        conn.commit()

                        response = {"status": "success", "message": "파일 업로드가 완료되었습니다."}
                        
                # ===========================================
                # 6-3. 클라우드: 파일 다운로드
                # ===========================================
                elif action == "cloud_download":
                    file_id = data.get("file_id")
                    if not file_id:
                        response = {"status": "fail", "message": "파일 ID가 제공되지 않았습니다."}
                    else:
                        cursor.execute("SELECT FILE_NAME, FILE_PATH FROM FILE WHERE FILE_ID = %s", (file_id,))
                        file_row = cursor.fetchone()

                        if not file_row:
                            response = {"status": "fail", "message": "해당 파일 정보를 찾을 수 없습니다."}
                        else:
                            physical_path = file_row['FILE_PATH']
                            file_name = file_row['FILE_NAME']

                            if not os.path.exists(physical_path):
                                response = {"status": "fail", "message": "서버에 해당 파일이 존재하지 않습니다."}
                            else:
                                with open(physical_path, "rb") as f:
                                    file_bytes = f.read()
                                    file_b64 = base64.b64encode(file_bytes).decode('utf-8')

                                response = {
                                    "status": "success",
                                    "file_data": {
                                        "file_name": file_name,
                                        "file_bytes_base64": file_b64
                                    }
                                }

                # ===========================================
                # 6-4. 클라우드: 휴지통으로 이동
                # ===========================================
                elif action == "cloud_move_to_trash":
                    file_id = data.get("file_id")
                    if not file_id:
                        response = {"status": "fail", "message": "파일 ID가 제공되지 않았습니다."}
                    else:
                        cursor.execute("UPDATE FILE SET STATUS = 'TRASH' WHERE FILE_ID = %s", (file_id,))
                        conn.commit()
                        response = {"status": "success", "message": "휴지통으로 이동되었습니다."}

                # ===========================================
                # 6-5. 클라우드: 휴지통 목록 조회
                # ===========================================
                elif action == "cloud_list_trash":
                    email = data.get("email")
                    cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (email,))
                    user = cursor.fetchone()
                    if not user:
                        response = {"status": "fail", "message": "사용자 정보를 찾을 수 없습니다."}
                    else:
                        cursor.execute("""
                            SELECT FILE_ID, FILE_NAME, ORIGINAL_NAME, FILE_SIZE, UPLOADED_AT
                            FROM FILE
                            WHERE USER_ID = %s AND STATUS = 'TRASH'
                        """, (user['USER_ID'],))
                        trash_files = cursor.fetchall()
                        response = {
                            "status": "success",
                            "files": trash_files
                        }
                # ===========================================
                # 6-6. 클라우드: 휴지통 복원 (신규 추가)
                # ===========================================
                elif action == "cloud_restore":
                    file_id = data.get("file_id")
                    if not file_id:
                        response = {"status": "fail", "message": "파일 ID가 제공되지 않았습니다."}
                    else:
                        cursor.execute("UPDATE FILE SET STATUS = 'COMPLETED' WHERE FILE_ID = %s", (file_id,))
                        conn.commit()
                        response = {"status": "success", "message": "정상적으로 복원되었습니다."}

                # ===========================================
                # 6-7. 클라우드: 영구 삭제
                # ===========================================
                elif action == "cloud_delete_permanently":
                    file_id = data.get("file_id")
                    if not file_id:
                        response = {"status": "fail", "message": "파일 ID가 제공되지 않았습니다."}
                    else:
                        cursor.execute("SELECT FILE_PATH FROM FILE WHERE FILE_ID = %s", (file_id,))
                        file_row = cursor.fetchone()

                        if file_row and file_row['FILE_PATH'] and os.path.exists(file_row['FILE_PATH']):
                            try:
                                os.remove(file_row['FILE_PATH'])
                            except Exception as file_err:
                                print(f"[파일 영구 삭제 실패] 디스크 파일 삭제 실패: {file_err}")

                        cursor.execute("DELETE FROM FILE WHERE FILE_ID = %s", (file_id,))
                        conn.commit()
                        response = {"status": "success", "message": "영구 삭제가 완료되었습니다."}
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
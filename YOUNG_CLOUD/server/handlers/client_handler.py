# server/client_hendler.py
import threading
import json
import pymysql
import random
import yagmail

# 로그인 성공 후 발급하는 임시 세션입니다.
# 서버 프로세스가 재시작되면 세션은 모두 만료됩니다.
ACTIVE_SESSIONS = {}
SESSION_LOCK = threading.Lock()
SESSION_TTL_SECONDS = 60 * 60 * 8
import hashlib
import uuid
import os
import base64
import time
import secrets

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

        # 로그인/회원가입/이메일 인증 외의 요청은 세션 토큰이 필요합니다.
        # 토큰에 저장된 사용자 정보로 data의 email을 덮어써서
        # 다른 사용자의 파일이나 메시지에 접근하지 못하게 합니다.
        if action not in ("login", "signup", "send_email"):
            token = data.pop("_session_token", None)
            with SESSION_LOCK:
                session = ACTIVE_SESSIONS.get(token)
                if not session or session["expires_at"] < time.time():
                    if token:
                        ACTIVE_SESSIONS.pop(token, None)
                    return {"status": "fail", "message": "로그인이 만료되었습니다. 다시 로그인해주세요."}
            data["email"] = session["email"]
            data["user_id"] = session["user_id"]
            data["is_admin"] = session["is_admin"]

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
                    # 입력받은 평문 비밀번호를 SHA-256 해시 문자열로 변환
                    hashed_pw = hashlib.sha256(password.encode("utf-8")).hexdigest()
                    
                    cursor.execute(
                        "SELECT * FROM USER WHERE EMAIL = %s AND LOWER(PASSWORD_HASH) = LOWER(%s)",
                        (user_id, hashed_pw),
                    )
                    user = cursor.fetchone()
                    
                    if user:
                        token = secrets.token_urlsafe(32)
                        with SESSION_LOCK:
                            ACTIVE_SESSIONS[token] = {
                                "user_id": user.get("USER_ID"),
                                "email": user.get("EMAIL", user_id),
                                "is_admin": bool(user.get("IS_ADMIN", 0)),
                                "expires_at": time.time() + SESSION_TTL_SECONDS,
                            }
                        response = {
                            "status": "success", 
                            "message": "로그인 성공", 
                            "session_token": token,
                            "email": user.get("EMAIL", user_id),
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
                

                # ---------------------------------------------------------
                # 메시지 기능 처리
                # MESSAGE 테이블 기준:
                # MESSAGE_ID, SENDER_ID, RECEIVER_ID, TITLE, CONTENT,
                # IS_READ, RECEIVED_AT, IS_DELETED
                # ---------------------------------------------------------
                elif action == "message_received":
                    email = data.get("email")
                    cursor.execute(
                        "SELECT M.MESSAGE_ID AS id, SU.EMAIL AS sender, "
                        "SU.NAME AS sender_name, '' AS title, "
                        "M.CONTENT AS content, M.IS_READ AS is_read, "
                        "M.CREATED_AT AS received_at "
                        "FROM MESSAGE M "
                        "JOIN USER RU ON M.RECEIVER_ID = RU.USER_ID "
                        "JOIN USER SU ON M.SENDER_ID = SU.USER_ID "
                        "WHERE RU.EMAIL = %s "
                        "ORDER BY M.CREATED_AT DESC",
                        (email,)
                    )
                    response = {"status": "success", "messages": cursor.fetchall()}

                elif action == "message_sent":
                    cursor.execute(
                        "SELECT M.MESSAGE_ID AS id, RU.EMAIL AS sender, "
                        "RU.NAME AS sender_name, '' AS title, "
                        "M.CONTENT AS content, M.IS_READ AS is_read, "
                        "M.CREATED_AT AS received_at "
                        "FROM MESSAGE M "
                        "JOIN USER SU ON M.SENDER_ID = SU.USER_ID "
                        "JOIN USER RU ON M.RECEIVER_ID = RU.USER_ID "
                        "WHERE SU.EMAIL = %s "
                        "ORDER BY M.CREATED_AT DESC",
                        (data.get("email"),)
                    )
                    response = {"status": "success", "messages": cursor.fetchall()}

                elif action == "message_send":
                    sender = data.get("sender")
                    receiver = data.get("receiver")
                    title = data.get("title", "")
                    content = data.get("content", "")
                    if not sender or not receiver or not content:
                        response = {"status": "fail", "message": "보내는 사람, 받는 사람, 내용을 확인해주세요."}
                    else:
                        cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (sender,))
                        sender_row = cursor.fetchone()
                        cursor.execute("SELECT USER_ID FROM USER WHERE EMAIL = %s", (receiver,))
                        receiver_row = cursor.fetchone()
                        if not sender_row or not receiver_row:
                            response = {"status": "fail", "message": "받는 사람 아이디를 찾을 수 없습니다."}
                        else:
                            cursor.execute(
                                "INSERT INTO MESSAGE "
                                "(SENDER_ID, RECEIVER_ID, CONTENT, IS_READ) "
                                "VALUES (%s, %s, %s, 0)",
                                (sender_row["USER_ID"], receiver_row["USER_ID"], content)
                            )
                            conn.commit()
                            response = {"status": "success", "message": "메시지가 전송되었습니다."}

                elif action == "message_mark_read":
                    cursor.execute(
                        "UPDATE MESSAGE M JOIN USER U ON M.RECEIVER_ID = U.USER_ID "
                        "SET M.IS_READ = 1 "
                        "WHERE M.MESSAGE_ID = %s AND U.EMAIL = %s",
                        (data.get("message_id"), data.get("email"))
                    )
                    conn.commit()
                    response = {"status": "success", "message": "읽음 처리되었습니다."}

                elif action == "message_delete":
                    ids = data.get("message_ids", [])
                    if not ids:
                        response = {"status": "fail", "message": "삭제할 메시지가 없습니다."}
                    else:
                        placeholders = ",".join(["%s"] * len(ids))
                        cursor.execute(
                            f"DELETE M FROM MESSAGE M "
                            f"JOIN USER U ON M.RECEIVER_ID = U.USER_ID "
                            f"WHERE M.MESSAGE_ID IN ({placeholders}) AND U.EMAIL = %s",
                            list(ids) + [data.get("email")]
                        )
                        conn.commit()
                        response = {"status": "success", "message": "메시지가 삭제되었습니다."}


                elif action == "cloud_list":
                    cursor.execute(
                        "SELECT F.FILE_ID AS id, F.ORIGINAL_NAME AS name, "
                        "F.FILE_SIZE AS size, F.UPLOADED_AT AS date, "
                        "F.STATUS AS status, F.FOLDER_ID AS folder_id "
                        "FROM FILE F JOIN FOLDER D ON F.FOLDER_ID=D.FOLDER_ID "
                        "JOIN USER U ON D.USER_ID=U.USER_ID "
                        "WHERE U.EMAIL=%s AND F.STATUS='COMPLETE' "
                        "ORDER BY F.UPLOADED_AT DESC",
                        (data.get("email"),)
                    )
                    response = {"status": "success", "files": cursor.fetchall()}

                elif action == "cloud_trash":
                    cursor.execute(
                        "SELECT F.FILE_ID AS id, F.ORIGINAL_NAME AS name, "
                        "F.FILE_SIZE AS size, F.UPLOADED_AT AS date, F.STATUS AS status "
                        "FROM FILE F JOIN FOLDER D ON F.FOLDER_ID=D.FOLDER_ID "
                        "JOIN USER U ON D.USER_ID=U.USER_ID "
                        "WHERE U.EMAIL=%s AND F.STATUS='TRASH' "
                        "ORDER BY F.UPLOADED_AT DESC",
                        (data.get("email"),)
                    )
                    response = {"status": "success", "files": cursor.fetchall()}

                elif action == "cloud_shared":
                    cursor.execute(
                        "SELECT F.FILE_ID AS id, F.ORIGINAL_NAME AS name, "
                        "F.FILE_SIZE AS size, F.UPLOADED_AT AS date, F.STATUS AS status "
                        "FROM FILE F JOIN FOLDER D ON F.FOLDER_ID=D.FOLDER_ID "
                        "JOIN USER U ON D.COMP=U.COMP "
                        "WHERE U.EMAIL=%s AND D.FOLDER_TYPE='COMP' "
                        "AND F.STATUS='COMPLETE' ORDER BY F.UPLOADED_AT DESC",
                        (data.get("email"),)
                    )
                    response = {"status": "success", "files": cursor.fetchall()}

                elif action == "cloud_upload":
                    email = data.get("email")
                    original_name = os.path.basename(data.get("file_name", ""))
                    encoded = data.get("content_base64", "")
                    if not original_name or not encoded:
                        response = {"status": "fail", "message": "업로드할 파일이 없습니다."}
                    else:
                        cursor.execute(
                            "SELECT USER_ID, FILE_SIZE_LIMIT FROM USER WHERE EMAIL=%s",
                            (email,)
                        )
                        user = cursor.fetchone()
                        binary = base64.b64decode(encoded)
                        max_size = int(user.get("FILE_SIZE_LIMIT") or 50 * 1024 * 1024) if user else 0
                        if not user:
                            response = {"status": "fail", "message": "사용자를 찾을 수 없습니다."}
                        elif len(binary) > max_size:
                            response = {"status": "fail", "message": "파일 용량 제한을 초과했습니다."}
                        else:
                            cursor.execute(
                                "SELECT FOLDER_ID FROM FOLDER "
                                "WHERE USER_ID=%s AND FOLDER_TYPE='ROOT' LIMIT 1",
                                (user["USER_ID"],)
                            )
                            folder = cursor.fetchone()
                            if not folder:
                                cursor.execute(
                                    "INSERT INTO FOLDER (USER_ID,FOLDER_NAME,FOLDER_TYPE,RELATIVE_PATH) "
                                    "VALUES (%s,'내 파일','ROOT',%s)",
                                    (user["USER_ID"], str(user["USER_ID"]))
                                )
                                conn.commit()
                                folder_id = cursor.lastrowid
                            else:
                                folder_id = folder["FOLDER_ID"]
                            stored_name = str(uuid.uuid4()) + "_" + original_name
                            relative_path = os.path.join(
                                "storage", "users", str(user["USER_ID"]), stored_name
                            )
                            absolute_path = os.path.join(
                                os.path.dirname(os.path.dirname(__file__)), relative_path
                            )
                            os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
                            with open(absolute_path, "wb") as file_obj:
                                file_obj.write(binary)
                            cursor.execute(
                                "INSERT INTO FILE "
                                "(FOLDER_ID,USER_ID,FILE_NAME,ORIGINAL_NAME,FILE_PATH,FILE_SIZE,STATUS) "
                                "VALUES (%s,%s,%s,%s,%s,%s,'COMPLETE')",
                                (folder_id, user["USER_ID"], stored_name, original_name,
                                 relative_path, len(binary))
                            )
                            conn.commit()
                            response = {"status": "success", "message": "파일을 업로드했습니다."}

                elif action == "cloud_download":
                    cursor.execute(
                        "SELECT F.FILE_PATH, F.ORIGINAL_NAME FROM FILE F "
                        "JOIN USER U ON F.USER_ID=U.USER_ID "
                        "WHERE F.FILE_ID=%s AND U.EMAIL=%s AND F.STATUS='COMPLETE'",
                        (data.get("file_id"), data.get("email"))
                    )
                    file_row = cursor.fetchone()
                    if not file_row:
                        response = {"status": "fail", "message": "파일을 찾을 수 없습니다."}
                    else:
                        absolute_path = os.path.join(
                            os.path.dirname(os.path.dirname(__file__)),
                            file_row["FILE_PATH"]
                        )
                        with open(absolute_path, "rb") as file_obj:
                            encoded = base64.b64encode(file_obj.read()).decode("ascii")
                        response = {"status": "success",
                                    "file_name": file_row["ORIGINAL_NAME"],
                                    "content_base64": encoded}

                elif action == "cloud_delete":
                    cursor.execute(
                        "UPDATE FILE F JOIN USER U ON F.USER_ID=U.USER_ID "
                        "SET F.STATUS='TRASH' WHERE F.FILE_ID=%s AND U.EMAIL=%s",
                        (data.get("file_id"), data.get("email"))
                    )
                    conn.commit()
                    response = {"status": "success", "message": "휴지통으로 이동했습니다."}

                elif action == "cloud_restore":
                    cursor.execute(
                        "UPDATE FILE F JOIN USER U ON F.USER_ID=U.USER_ID "
                        "SET F.STATUS='COMPLETE' WHERE F.FILE_ID=%s AND U.EMAIL=%s",
                        (data.get("file_id"), data.get("email"))
                    )
                    conn.commit()
                    response = {"status": "success", "message": "파일을 복원했습니다."}

            except Exception as e:
                response = {"status": "error", "message": f"데이터베이스 오류: {str(e)}"}
            finally:
                if 'conn' in locals() and conn.open:
                    conn.close()

        return response
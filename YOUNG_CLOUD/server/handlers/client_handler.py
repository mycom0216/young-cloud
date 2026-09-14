import threading
import json
import pymysql  # sqlite3 대신 pymysql 사용

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
                # [핵심] 다른 컴퓨터(10.10.10.113)의 MariaDB에 원격 연결
                conn = pymysql.connect(
                    host='10.10.10.113',
                    port=3306,
                    user='young_user',
                    password='1234',
                    database='YOUNG_CLOUD',  # 혹은 팀원이 지정한 DB 이름
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )
                cursor = conn.cursor()
                
                response = {"status": "fail", "message": "알 수 없는 요청입니다."}

                if action == "login":
                    user_id = data.get("user_id")
                    password = data.get("password")
                    
                    # MariaDB 쿼리 실행
                    cursor.execute("SELECT * FROM USER WHERE EMAIL = %s AND PASSWORD_HASH = %s", (user_id, password))
                    user = cursor.fetchone()
                    
                    if user:
                        response = {
                            "status": "success", 
                            "message": "로그인 성공", 
                            "is_admin": bool(user.get('is_admin', 0))
                        }
                    else:
                        response = {"status": "fail", "message": "아이디 또는 비밀번호가 틀렸습니다."}
                
            except Exception as e:
                response = {"status": "error", "message": f"데이터베이스 오류: {str(e)}"}
            finally:
                if 'conn' in locals() and conn.open:
                    conn.close()

        return response
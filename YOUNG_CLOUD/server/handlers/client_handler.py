# server/client_handler.py
# --------------------------------------------------------
# 소켓 연결 1개 = 스레드 1개 (ST1~STN).
# common/protocol.py의 MessageType을 기준으로 요청을 분기 처리합니다.
# --------------------------------------------------------

import os
import socket
import sys
import threading
import traceback
from pathlib import Path

# messenger_client.py와 동일한 방식으로, project_root를 sys.path에 추가해서
# "common" 패키지를 어디서 실행하든 찾을 수 있게 합니다.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.protocol import MessageType, build_message, send_msg, recv_msg, ConnectionClosed, recv_exact_bytes

import auth_service
import admin_service
import file_service
import message_service
import settings_service
import session_registry
from config import FILE_CHUNK_SIZE


class ClientHandler(threading.Thread):
    def __init__(self, conn: socket.socket, addr):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr

        self.user_id: int | None = None
        self.email: str | None = None
        self.name: str | None = None
        self.is_admin: bool = False

        # 같은 커넥션에 대해 "정상 응답 스레드(자기 자신)"와 "다른 사람이 보낸 메시지를
        # push하려는 스레드"가 동시에 sendall()을 호출할 수 있으므로, 소켓 쓰기는 항상
        # 이 락을 잡고 해야 합니다. (TCP 소켓은 동시 write에 안전하지 않음)
        self.send_lock = threading.Lock()

    # ------------------------------------------------------------------
    def run(self):
        print(f"[연결] {self.addr} 접속")
        try:
            while True:
                message = recv_msg(self.conn)
                if message is None:
                    break  # 클라이언트가 정상적으로 연결을 끊음
                self._dispatch(message)
        except ConnectionClosed:
            pass
        except Exception:
            print(f"[오류] {self.addr} 처리 중 예외:")
            traceback.print_exc()
        finally:
            if self.user_id is not None:
                session_registry.unregister(self.user_id)
            self.conn.close()
            print(f"[종료] {self.addr} 연결 끊김")

    def _send(self, msg_type: str, payload: dict) -> None:
        with self.send_lock:
            send_msg(self.conn, build_message(msg_type, payload))

    def push(self, msg_type: str, payload: dict) -> None:
        """다른 스레드(다른 사용자를 처리 중인 핸들러)가 이 커넥션으로 실시간 알림을 보낼 때 사용."""
        self._send(msg_type, payload)

    def _require_login(self) -> bool:
        return self.user_id is not None

    # ------------------------------------------------------------------
    def _dispatch(self, message: dict) -> None:
        msg_type = message.get("type", "")
        data = message.get("payload", {}) or {}

        try:
            ok, msg, result, result_type = self._handle(msg_type, data)
        except KeyError as e:
            ok, msg, result = False, f"필수 파라미터가 누락되었습니다: {e}", {}
            result_type = MessageType.ERROR
        except Exception as e:
            traceback.print_exc()
            ok, msg, result = False, f"서버 오류: {e}", {}
            result_type = MessageType.ERROR

        if result_type is None:
            return  # 이미 해당 핸들러 내부에서 직접 응답을 보낸 경우 (파일 업/다운로드 등)

        payload = {**result, "success": ok, "message": msg}
        self._send(result_type, payload)

    # ------------------------------------------------------------------
    # msg_type -> (성공여부, 메시지, 결과데이터, 응답으로 보낼 MessageType) 반환
    # 응답 MessageType이 None이면 해당 핸들러가 이미 자체적으로 send_msg를 호출한 것으로 간주
    # ------------------------------------------------------------------
    def _handle(self, msg_type: str, data: dict):
        MT = MessageType

        # ── 로그인 불필요 ──
        if msg_type == MT.SIGNUP_REQUEST_CODE:
            ok, msg, r = auth_service.request_signup_code(data["email"])
            return ok, msg, r, MT.SIGNUP_REQUEST_CODE_RESULT

        if msg_type == MT.SIGNUP_VERIFY_CODE:
            ok, msg, r = auth_service.verify_signup_code(data["email"], data["code"])
            return ok, msg, r, MT.SIGNUP_VERIFY_CODE_RESULT

        if msg_type == MT.SIGNUP:
            ok, msg, r = auth_service.signup(
                data["email"], data["password"], data["name"],
                data.get("comp", ""), data.get("grade", "NORMAL"),
            )
            return ok, msg, r, MT.SIGNUP_RESULT

        if msg_type == MT.LOGIN:
            ok, msg, r = auth_service.login(data["email"], data["password"])
            if ok:
                user = r["user"]
                self.user_id = user["user_id"]
                self.email = user["email"]
                self.name = user["name"]
                self.is_admin = user["is_admin"]
                session_registry.register(self.user_id, self)
            return ok, msg, r, MT.LOGIN_RESULT

        if msg_type == MT.PASSWORD_CHECK_EMAIL:
            ok, msg, r = auth_service.check_email_registered(data["email"])
            return ok, msg, r, MT.PASSWORD_CHECK_EMAIL_RESULT

        if msg_type == MT.PASSWORD_RESET:
            ok, msg, r = auth_service.reset_password(data["email"], data["new_password"])
            return ok, msg, r, MT.PASSWORD_RESET_RESULT

        # ── 이 아래부터는 로그인 필요 ──
        if not self._require_login():
            return False, "로그인이 필요합니다.", {}, MT.ERROR

        if msg_type == MT.SEARCH_USER:
            ok, msg, r = message_service.search_users(data["keyword"], self.user_id)
            return ok, msg, r, MT.SEARCH_USER_RESULT

        if msg_type == MT.SEND_MESSAGE:
            ok, msg, r = message_service.send_message(self.user_id, data["receiver_id"], data["content"])
            if ok and r.get("delivered"):
                self._push_new_message(receiver_id=data["receiver_id"], message_id=r["message_id"], content=data["content"])
            return ok, msg, r, MT.SEND_MESSAGE_RESULT

        if msg_type == MT.GET_HISTORY:
            ok, msg, r = message_service.get_history(self.user_id, data["other_user_id"], data.get("page", 1))
            return ok, msg, r, MT.GET_HISTORY_RESULT

        if msg_type == MT.MARK_READ:
            ok, msg, r = message_service.mark_read(self.user_id, data["message_id"])
            return ok, msg, r, MT.MARK_READ_RESULT

        if msg_type == MT.BLOCK_USER:
            ok, msg, r = message_service.block_user(self.user_id, data["target_user_id"])
            return ok, msg, r, MT.BLOCK_USER_RESULT

        if msg_type == MT.UNBLOCK_USER:
            ok, msg, r = message_service.unblock_user(self.user_id, data["target_user_id"])
            return ok, msg, r, MT.UNBLOCK_USER_RESULT

        if msg_type == MT.GET_CLOUD_STORAGE:
            ok, msg, r = file_service.get_cloud_storage(self.user_id, data.get("folder_path", "/"))
            return ok, msg, r, MT.CLOUD_STORAGE_RESULT

        if msg_type == MT.UPLOAD_FILE:
            self._handle_upload(data)
            return None, None, None, None  # 이미 내부에서 응답을 다 보냄

        if msg_type == MT.DOWNLOAD_FILE:
            self._handle_download(data)
            return None, None, None, None

        if msg_type == MT.DELETE_FILE:
            ok, msg, r = file_service.delete_file(self.user_id, data["file_id"])
            return ok, msg, r, MT.FILE_DELETE_RESULT

        if msg_type == MT.GET_SETTINGS:
            ok, msg, r = settings_service.get_settings(self.user_id, data["category"])
            return ok, msg, r, MT.SETTINGS_LOAD_RESULT

        if msg_type == MT.UPDATE_SETTINGS:
            ok, msg, r = settings_service.update_settings(self.user_id, data["category"], data.get("data", {}))
            return ok, msg, r, MT.SETTINGS_UPDATE_RESULT

        # ── 관리자 전용 ──
        if msg_type.startswith("ADMIN_"):
            if not self.is_admin:
                return False, "관리자 권한이 필요합니다.", {}, MT.ERROR

            if msg_type == MT.ADMIN_SEND_GLOBAL_MESSAGE:
                ok, msg, r = admin_service.send_global_message(self.user_id, data["content"])
                if ok:
                    for uid in r.get("receiver_ids", []):
                        self._push_new_message(receiver_id=uid, message_id=None, content=data["content"], sender_override=self.user_id)
                return ok, msg, r, MT.ADMIN_SEND_GLOBAL_MESSAGE_RESULT

            if msg_type == MT.ADMIN_SEARCH_USERS:
                ok, msg, r = admin_service.search_users(data.get("keyword", ""))
                return ok, msg, r, MT.ADMIN_SEARCH_USERS_RESULT

            if msg_type == MT.ADMIN_BAN_USER:
                ok, msg, r = admin_service.ban_user(data["target_user_id"])
                return ok, msg, r, MT.ADMIN_BAN_USER_RESULT

            if msg_type == MT.ADMIN_UNBAN_USER:
                ok, msg, r = admin_service.unban_user(data["target_user_id"])
                return ok, msg, r, MT.ADMIN_UNBAN_USER_RESULT

        return False, f"알 수 없는 요청입니다: {msg_type}", {}, MT.ERROR

    # ------------------------------------------------------------------
    def _push_new_message(self, receiver_id: int, message_id, content: str, sender_override: int | None = None):
        """수신자가 현재 접속 중이면 NEW_MESSAGE를 즉시 push합니다."""
        receiver_handler = session_registry.get_handler(receiver_id)
        if receiver_handler is None:
            return  # 접속 중이 아니면 push 생략 (다음 GET_HISTORY 호출 시 확인하게 됨)
        receiver_handler.push(MessageType.NEW_MESSAGE, {
            "message_id": message_id,
            "sender_id": sender_override if sender_override is not None else self.user_id,
            "receiver_id": receiver_id,
            "content": content,
        })

    # ------------------------------------------------------------------
    # 파일 업로드: 메타데이터 응답(FILE_UPLOAD_READY) 후 raw 바이트 수신
    # ------------------------------------------------------------------
    def _handle_upload(self, data: dict) -> None:
        folder_path = data.get("folder_path", "/")
        file_name = data["file_name"]
        size_bytes = data["size_bytes"]

        lock = file_service.get_user_lock(self.user_id)
        if not lock.acquire(blocking=False):
            self._send(MessageType.FILE_UPLOAD_RESULT, {"success": False, "message": "다른 파일 작업이 진행 중입니다."})
            return

        stored_path = None
        try:
            ok, msg, prep = file_service.begin_upload(self.user_id, folder_path, file_name, size_bytes)
            if not ok:
                self._send(MessageType.FILE_UPLOAD_RESULT, {"success": False, "message": msg})
                return

            stored_path = prep["stored_path"]
            self._send("FILE_UPLOAD_READY", {"final_name": prep["final_name"]})

            with open(stored_path, "wb") as f:
                remaining = size_bytes
                while remaining > 0:
                    chunk = self.conn.recv(min(FILE_CHUNK_SIZE, remaining))
                    if not chunk:
                        raise ConnectionClosed("파일 전송 중 연결이 끊겼습니다.")
                    f.write(chunk)
                    remaining -= len(chunk)

            file_id = file_service.commit_upload(self.user_id, folder_path, prep["final_name"], stored_path, size_bytes)
            self._send(MessageType.FILE_UPLOAD_RESULT, {
                "success": True, "message": "파일 저장이 완료되었습니다.",
                "file_id": file_id, "final_name": prep["final_name"],
            })
        except Exception as e:
            if stored_path and os.path.exists(stored_path):
                os.remove(stored_path)
            self._send(MessageType.FILE_UPLOAD_RESULT, {"success": False, "message": f"업로드 실패: {e}"})
        finally:
            lock.release()

    # ------------------------------------------------------------------
    # 파일 다운로드: 메타데이터 응답(FILE_DOWNLOAD_READY) 후 raw 바이트 송신
    # ------------------------------------------------------------------
    def _handle_download(self, data: dict) -> None:
        file_id = data["file_id"]

        lock = file_service.get_user_lock(self.user_id)
        if not lock.acquire(blocking=False):
            self._send(MessageType.FILE_DOWNLOAD_RESULT, {"success": False, "message": "다른 파일 작업이 진행 중입니다."})
            return

        try:
            meta = file_service.get_file_meta(self.user_id, file_id)
            if not meta or not os.path.exists(meta["stored_path"]):
                self._send(MessageType.FILE_DOWNLOAD_RESULT, {"success": False, "message": "파일을 찾을 수 없습니다."})
                return

            with self.send_lock:
                send_msg(self.conn, build_message("FILE_DOWNLOAD_READY", {
                    "file_name": meta["display_name"], "size_bytes": meta["size_bytes"],
                }))
                with open(meta["stored_path"], "rb") as f:
                    while True:
                        chunk = f.read(FILE_CHUNK_SIZE)
                        if not chunk:
                            break
                        self.conn.sendall(chunk)

            self._send(MessageType.FILE_DOWNLOAD_RESULT, {"success": True, "message": "다운로드가 완료되었습니다."})
        finally:
            lock.release()

# -*- coding: utf-8 -*-
"""클라우드 화면의 실제 동작."""

import base64
import os
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from ui.cloud_ui import CloudUI


class CloudLogic(CloudUI):
    """서버의 FILE/FOLDER 데이터와 클라우드 테이블을 연결합니다."""

    def __init__(self, net_client=None, mode="my_files", user_email=""):
        super().__init__(mode=mode)
        self.net_client = net_client
        self.user_email = user_email
        self.btn_upload.clicked.connect(self.upload_action)
        self.btn_download.clicked.connect(self.download_action)
        self.btn_delete.clicked.connect(self.delete_action)
        self.btn_restore.clicked.connect(self.restore_action)
        self.table.cellDoubleClicked.connect(lambda row, column: self.download_action())
        self.load_files()

    def request(self, action, data=None):
        if not self.net_client:
            return {"status": "fail", "message": "네트워크 클라이언트가 없습니다."}
        return self.net_client.send_request(action, data or {})

    def load_files(self):
        action = {
            "my_files": "cloud_list",
            "shared": "cloud_shared",
            "trash": "cloud_trash",
        }.get(self.mode, "cloud_list")
        response = self.request(action, {"email": self.user_email})
        if response.get("status") == "success":
            self.set_files(response.get("files", []))
        else:
            QMessageBox.warning(self, "파일 조회 실패", response.get("message", "파일 목록을 조회하지 못했습니다."))

    def _selected_file_ids(self):
        result = []
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            checkbox = widget.findChild(type(widget)) if widget else None
            if widget and widget.layout() and widget.layout().itemAt(0):
                checkbox = widget.layout().itemAt(0).widget()
            if checkbox and checkbox.isChecked():
                item = self.table.item(row, 1)
                info = item.data(Qt.ItemDataRole.UserRole) if item else {}
                if info.get("id") is not None:
                    result.append(info["id"])
        return result

    def _selected_file_id(self):
        ids = self._selected_file_ids()
        if ids:
            return ids[0]
        row = self.table.currentRow()
        if row >= 0 and self.table.item(row, 1):
            info = self.table.item(row, 1).data(Qt.ItemDataRole.UserRole) or {}
            return info.get("id")
        return None

    def upload_action(self):
        if self.mode != "my_files":
            return
        path, _ = QFileDialog.getOpenFileName(self, "업로드할 파일 선택")
        if not path:
            return
        with open(path, "rb") as file_obj:
            encoded = base64.b64encode(file_obj.read()).decode("ascii")
        response = self.request("cloud_upload", {
            "email": self.user_email,
            "file_name": os.path.basename(path),
            "content_base64": encoded,
        })
        if response.get("status") == "success":
            self.load_files()
        else:
            QMessageBox.warning(self, "업로드 실패", response.get("message", "파일을 업로드하지 못했습니다."))

    def download_action(self):
        file_id = self._selected_file_id()
        if file_id is None:
            QMessageBox.information(self, "안내", "받을 파일을 선택해주세요.")
            return
        response = self.request("cloud_download", {
            "email": self.user_email, "file_id": file_id
        })
        if response.get("status") != "success":
            QMessageBox.warning(self, "다운로드 실패", response.get("message", "파일을 받지 못했습니다."))
            return
        target, _ = QFileDialog.getSaveFileName(
            self, "저장할 위치 선택", response.get("file_name", "")
        )
        if not target:
            return
        with open(target, "wb") as file_obj:
            file_obj.write(base64.b64decode(response["content_base64"]))
        QMessageBox.information(self, "완료", "파일을 저장했습니다.")

    def delete_action(self):
        ids = self._selected_file_ids()
        if not ids:
            QMessageBox.information(self, "안내", "삭제할 파일을 선택해주세요.")
            return
        for file_id in ids:
            self.request("cloud_delete", {"email": self.user_email, "file_id": file_id})
        self.load_files()

    def restore_action(self):
        file_id = self._selected_file_id()
        if file_id is None:
            QMessageBox.information(self, "안내", "복원할 파일을 선택해주세요.")
            return
        response = self.request("cloud_restore", {
            "email": self.user_email, "file_id": file_id
        })
        if response.get("status") != "success":
            QMessageBox.warning(self, "복원 실패", response.get("message", "복원하지 못했습니다."))
        self.load_files()


if __name__ == "__main__":
    app = QApplication([])
    window = CloudLogic()
    window.resize(800, 600)
    window.show()
    app.exec()

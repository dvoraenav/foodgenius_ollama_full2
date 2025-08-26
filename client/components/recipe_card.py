from typing import Callable
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import requests

class RecipeCard(QFrame):
    def __init__(self, summary: dict, on_open: Callable[[str], None]):
        super().__init__()
        self.setProperty("class", "card")
        self.setStyleSheet("""
            QFrame[class="card"] {
                background:#ffffff; border:1px solid #e5e7eb; border-radius:16px;
            }
            QLabel[class="title"] { font-weight:700; font-size:14px; }
            QPushButton[accent="true"] {
                background:#10b981; color:white; border:none; border-radius:10px; padding:8px 12px; font-weight:600;
            }
            QPushButton[accent="true"]:hover { background:#059669; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # --- Banner עליון (רק התמונה) ---
        banner = QWidget()
        banner.setFixedHeight(160)
        banner.setStyleSheet(
            "background:#0f172a; border-top-left-radius:16px; border-top-right-radius:16px;"
            "border-bottom-left-radius:0px; border-bottom-right-radius:0px;"
        )
        root.addWidget(banner)

        self.img = QLabel(banner)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setGeometry(0, 0, banner.width(), banner.height())
        self.img.setStyleSheet("border:0;")

        def _resize_banner():
            self.img.setGeometry(0, 0, banner.width(), banner.height())
            if getattr(self, "_orig_pix", None):
                self._apply_cover()
        banner.resizeEvent = lambda e: (_resize_banner(), QWidget.resizeEvent(banner, e))

        # --- אזור תוכן מתחת לתמונה ---
        content = QVBoxLayout()
        content.setContentsMargins(12, 8, 12, 12)
        content.setSpacing(8)
        root.addLayout(content)

        title = QLabel(summary.get("title", ""))
        title.setProperty("class", "title")
        title.setWordWrap(True)
        content.addWidget(title)

        badges = QHBoxLayout()

        cal = int((summary.get("nutrition") or {}).get("cal", 0))
        cal_lbl = QLabel(f"{cal} קק")
        cal_lbl.setStyleSheet("background:#eef2ff; color:#1f2937; padding:2px 8px; border-radius:10px; font-size:12px;")
        badges.addWidget(cal_lbl, 0, Qt.AlignRight)

        for tag in (summary.get("tags") or [])[:4]:
            t = QLabel(tag)
            t.setStyleSheet("background:#eef2ff; color:#1f2937; padding:2px 8px; border-radius:10px; font-size:12px;")
            badges.addWidget(t, 0, Qt.AlignRight)

        badges.addStretch(1)
        content.addLayout(badges)

        # --- כפתור לפרטים ---
        rid = str(
            summary.get("id")
            or summary.get("idMeal")
            or summary.get("recipe_id")
            or summary.get("rid")
            or ""
        )
        btn = QPushButton("לפרטים")
        btn.setProperty("accent", True)
        content.addWidget(btn)

        if rid and callable(on_open):
            # QPushButton.clicked מעביר פרמטר checked, לכן מוסיפים ברירת מחדל
            btn.clicked.connect(lambda checked=False, rid=rid: on_open(rid))
        else:
            btn.setEnabled(False)

        # --- טעינת התמונה עם אפקט cover בתוך הבאנר בלבד ---
        url = summary.get("image")
        if url:
            try:
                r = requests.get(url, timeout=8)
                r.raise_for_status()
                pix = QPixmap(); pix.loadFromData(r.content)
                self._orig_pix = pix
                self._apply_cover()
            except Exception:
                self.img.setText("No image")
        else:
            self.img.setText("No image")

    def _apply_cover(self):
        w = self.img.width() or 1
        h = self.img.height() or 1
        cover = self._orig_pix.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.img.setPixmap(cover)

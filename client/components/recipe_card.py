from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import requests, io

class RecipeCard(QFrame):
    def __init__(self, summary: dict, on_open):
        super().__init__()
        self.setProperty("class", "card")
        lay = QVBoxLayout(self); lay.setContentsMargins(12,12,12,12); lay.setSpacing(8)
        img = QLabel(); img.setFixedHeight(150); img.setAlignment(Qt.AlignCenter)
        url = summary.get("image")
        if url:
            try:
                pix = QPixmap(); pix.loadFromData(requests.get(url, timeout=8).content)
                img.setPixmap(pix.scaledToHeight(150, Qt.SmoothTransformation))
            except Exception: img.setText("No image")
        else: img.setText("No image")
        lay.addWidget(img)
        t = QLabel(summary.get("title","")); t.setWordWrap(True); t.setStyleSheet("font-weight:700; font-size:14px;"); lay.addWidget(t)
        badges = QHBoxLayout()
        cal = int((summary.get("nutrition") or {}).get("cal", 0))
        b1 = QLabel(f"{cal} קק"); b1.setStyleSheet("background:#eef2ff; padding:2px 8px; border-radius:10px;"); badges.addWidget(b1, 0, Qt.AlignRight)
        for tag in (summary.get("tags") or [])[:2]:
            lbl = QLabel(tag); lbl.setStyleSheet("background:#ecfeff; padding:2px 8px; border-radius:10px;"); badges.addWidget(lbl, 0, Qt.AlignRight)
        badges.addStretch(1); lay.addLayout(badges)
        btn = QPushButton("לפרטים"); btn.setProperty("accent", True); btn.clicked.connect(lambda: on_open(summary.get("id"))); lay.addWidget(btn)

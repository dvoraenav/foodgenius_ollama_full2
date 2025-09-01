from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QSizePolicy, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QPieSeries, QChartView, QPieSlice
from PySide6.QtGui import QFont, QPainter, QColor, QBrush
from PySide6.QtGui import QPen


class NutritionChart(QFrame):
    def __init__(self, nutrition_data=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setFixedHeight(350)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet('''
            QFrame[class="card"] {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
            }
            QFrame[class="card"]:hover { border-color: #10b981; }
        ''')

        # === root layout ===
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(15, 15, 15, 15)
        self.root.setSpacing(10)

        # === title (נשאר קבוע, רק הטקסט מתעדכן) ===
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: 800; color: #374151; margin-bottom: 6px;")
        self.root.addWidget(self.title_label)

        # === אזור הגרף + לג'נד ===
        self.chart_row = QHBoxLayout()
        self.chart_row.setContentsMargins(0, 0, 0, 0)
        self.chart_row.setSpacing(16)
        self.root.addLayout(self.chart_row)

        # --- chart/series/view בניה חד-פעמית ---
        self.series = QPieSeries()
        self.series.setHoleSize(0.0)   # חשוב: בלי חור
        self.series.setPieSize(0.96)   # מעט גדול יותר
        self.series.setLabelsVisible(True)

        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setBackgroundVisible(False)
        self.chart.legend().setVisible(False)  # לג'נד מותאם משלנו
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumSize(300, 250)
        self.chart_view.setStyleSheet("background: transparent;")
        self.chart_row.addWidget(self.chart_view, 2)

        # --- legend מותאם: נבנה פעם אחת ומרעננים תוכן ---
        self.legend_widget = QWidget()
        self.legend_layout = QVBoxLayout(self.legend_widget)
        self.legend_layout.setContentsMargins(0, 4, 0, 0)
        self.legend_layout.setSpacing(8)

        self.legend_title = QLabel("Macronutrients")
        self.legend_title.setStyleSheet("font-weight: 700; font-size: 13px; color: #374151;")
        self.legend_layout.addWidget(self.legend_title)

        self.legend_layout.addStretch()
        self.chart_row.addWidget(self.legend_widget, 1)
        self.chart_row.setAlignment(self.legend_widget, Qt.AlignLeft | Qt.AlignVCenter)


        # נתוני ברירת מחדל
        if nutrition_data is None:
            nutrition_data = {'calories': 300, 'protein': 25, 'carbs': 35, 'fat': 15}

        self.update_nutrition_data(nutrition_data)

    def update_nutrition_data(self, data: dict):
        # 1) כותרת
        self.title_label.setText(f"Total: {int(data.get('calories', 0))} calories")

        # 2) חישובים (קלוריות לפי 4/4/9)
        protein_cal = float(data.get('protein', 0)) * 4
        carbs_cal   = float(data.get('carbs',   0)) * 4
        fat_cal     = float(data.get('fat',     0)) * 9
        if protein_cal == 0 and carbs_cal == 0 and fat_cal == 0:
            protein_cal, carbs_cal, fat_cal = 100, 140, 135  # fallback כמו בקוד הישן

        # צבעים מדויקים (כמו שרצית)
        CARBS_COLOR   = "#38BDF8"   # כחול
        PROTEIN_COLOR = "#34D399"   # ירוק
        FAT_COLOR     = "#A78BFA"   # סגול

        parts = [
            ("Carbs",   carbs_cal,   CARBS_COLOR,   data.get("carbs",   0)),
            ("Protein", protein_cal, PROTEIN_COLOR, data.get("protein", 0)),
            ("Fat",     fat_cal,     FAT_COLOR,     data.get("fat",     0)),
        ]
        parts = [p for p in parts if p[1] > 0.01]

        # 3) מחליפים סדרה ישנה בחדשה (בדיוק כמו שהיית עושה Figure חדש במאטפלוטליב)
        if hasattr(self, "series") and self.series is not None:
            self.chart.removeSeries(self.series)
            self.series.deleteLater()

        new_series = QPieSeries()
        new_series.setHoleSize(0.0)   # עוגה מלאה (אם תרצי דונאט: 0.52)
        new_series.setPieSize(0.96)
        new_series.setLabelsVisible(True)

        total = sum(v for _, v, _, _ in parts) or 1.0  # אחוזים לפי קלוריות
        # (אם תרצי לפי גרמים: total = sum(g for (_,_,_,g) in parts) or 1.0)

        for name, cal_value, color_hex, grams in parts:
            sl = new_series.append(name, cal_value)
            sl.setBrush(QColor(color_hex))
            sl.setColor(QColor(color_hex))           # מבטיח את הגוון המדויק
            sl.setPen(QPen(QColor("#ffffff"), 2))    # קווי הפרדה לבנים

            pct = (cal_value / total) * 100.0        # או: grams / total * 100.0
            sl.setLabel(f"{pct:.0f}%")               # מציגים תמיד את האחוזים
            sl.setLabelVisible(True)
            sl.setLabelPosition(QPieSlice.LabelInsideHorizontal)

            f = QFont(); f.setPointSize(12); f.setBold(True)
            sl.setLabelFont(f)
            sl.setLabelBrush(QBrush(QColor("white")))  # לבן נראה מצוין על הגוונים הללו

        # מוסיפים את הסדרה החדשה לגרף ומעדכנים רפרנס
        self.chart.addSeries(new_series)
        self.series = new_series

        # 4) מרעננים את הלג'נד המותאם (שם + גרמים, באותם צבעים)
        self._rebuild_legend([(n, g, c) for (n, _cal, c, g) in parts])

    # ---------- עזר: בניית לג׳נד מותאם ----------
    def _rebuild_legend(self, items):
        # מוחקים כל פריט קיים חוץ מהכותרת הראשונה
        while self.legend_layout.count() > 1:
            it = self.legend_layout.takeAt(1)   # אלמנט אחרי הכותרת
            w = it.widget()
            if w:
                w.deleteLater()

        for name, grams, color_hex in items:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)

            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color_hex}; font-size: 16px;")
            dot.setFixedWidth(18)

            text = QLabel(f"{name}  {int(round(grams))}g")
            text.setStyleSheet("font-size: 12px; color: #374151;")

            row.addWidget(dot)
            row.addWidget(text)
            row.addStretch()

            # עוטפים כל שורה ב־QWidget כדי לנקות בקלות בעדכונים
            container = QWidget()
            c_lay = QHBoxLayout(container)
            c_lay.setContentsMargins(0, 0, 0, 0)
            c_lay.setSpacing(0)
            c_lay.addLayout(row)

            self.legend_layout.addWidget(container)

        self.legend_layout.addStretch()



# ====== נשאר כפי שהיה: פונקציה פשוטה לאומדן מקומי (fallback) ======
def calculate_nutrition_from_ingredients(ingredients):
    nutrition_db = {
        'flour': {'cal': 364, 'protein': 10, 'carbs': 76, 'fat': 1},
        'egg': {'cal': 155, 'protein': 13, 'carbs': 1, 'fat': 11},
        'milk': {'cal': 42, 'protein': 3.4, 'carbs': 5, 'fat': 1},
        'sugar': {'cal': 387, 'protein': 0, 'carbs': 100, 'fat': 0},
        'oil': {'cal': 884, 'protein': 0, 'carbs': 0, 'fat': 100},
        'butter': {'cal': 717, 'protein': 0.9, 'carbs': 0.1, 'fat': 81},
        'chicken': {'cal': 239, 'protein': 27, 'carbs': 0, 'fat': 14},
        'garlic': {'cal': 149, 'protein': 6.4, 'carbs': 33, 'fat': 0.5},
        'onion': {'cal': 40, 'protein': 1.1, 'carbs': 9.3, 'fat': 0.1},
        'tomato': {'cal': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2},
        'rice': {'cal': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3},
        'potato': {'cal': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1},
    }

    total_cal = total_protein = total_carbs = total_fat = 0
    found = 0

    for ing in ingredients or []:
        name = (ing.get('name') or '').lower()
        for key, v in nutrition_db.items():
            if key in name:
                found += 1
                if key in ['flour']: portion = 1.0
                elif key in ['egg']: portion = 0.5
                elif key in ['milk']: portion = 3.0
                elif key in ['sugar']: portion = 0.2
                elif key in ['oil','Butter'.lower()]: portion = 0.15
                elif key in ['chicken','rice','potato']: portion = 1.5
                else: portion = 0.1
                total_cal += v['cal'] * portion
                total_protein += v['protein'] * portion
                total_carbs += v['carbs'] * portion
                total_fat += v['fat'] * portion
                break

    if not found:
        return {'calories': 300, 'protein': 20, 'carbs': 35, 'fat': 12}

    return {
        'calories': int(total_cal),
        'protein': int(total_protein),
        'carbs': int(total_carbs),
        'fat': int(total_fat)
    }

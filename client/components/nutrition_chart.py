from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QSizePolicy
from PySide6.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class NutritionChart(QFrame):
    def __init__(self, nutrition_data=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setFixedHeight(280)  # גובה קבוע שלא “ימשוך” את הדף
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.setStyleSheet('''
            QFrame[class="card"] {
                background: #ffffff; border: 1px solid #e5e7eb; border-radius: 16px;
            }
            QFrame[class="card"]:hover { border-color: #10b981; }
        ''')

        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(5)

        self.chart_widget = QWidget()
        root.addWidget(self.chart_widget)

        self._canvas = None

        if nutrition_data is None:
            nutrition_data = {'calories': 300, 'protein': 25, 'carbs': 35, 'fat': 15}
        self.create_chart(nutrition_data)

    def create_chart(self, nutrition_data):
        protein_cal = float(nutrition_data.get('protein', 0)) * 4
        carbs_cal   = float(nutrition_data.get('carbs',   0)) * 4
        fat_cal     = float(nutrition_data.get('fat',     0)) * 9
        if protein_cal == 0 and carbs_cal == 0 and fat_cal == 0:
            protein_cal, carbs_cal, fat_cal = 100, 140, 135

        parts = [
            ("Carbs",   carbs_cal,   "#38bdf8", nutrition_data.get("carbs",   0)),
            ("Protein", protein_cal, "#34d399", nutrition_data.get("protein", 0)),
            ("Fat",     fat_cal,     "#a78bfa", nutrition_data.get("fat",     0)),
        ]
        parts = [p for p in parts if p[1] > 0.01]

        labels = [p[0] for p in parts]
        sizes  = [p[1] for p in parts]
        colors = [p[2] for p in parts]
        grams  = [int(round(p[3])) for p in parts]

        fig = Figure(figsize=(6.5, 3.8), dpi=100, facecolor='white')
        # מפנה שוליים ללג'נד מימין כדי שלא ייחתך
        fig.subplots_adjust(left=0.06, right=0.78, top=0.86, bottom=0.14)
        ax = fig.add_subplot(111)

        wedges, _texts, _auto = ax.pie(
            sizes,
            labels=None,
            colors=colors,
            autopct=lambda pct: f"{pct:.0f}%" if pct >= 4 else "",
            startangle=90,
            counterclock=False,
            pctdistance=0.72,
            wedgeprops={'width': 0.48, 'edgecolor': 'none', 'linewidth': 0},
            textprops={'fontsize': 11, 'color': 'white', 'weight': 'bold'}
        )

        fig.suptitle(
            f'Total: {int(nutrition_data.get("calories", 0))} calories',
            fontsize=16, fontweight='bold', color='#374151', y=0.98
        )

        legend_labels = [f"{lbl}  {g}g" for lbl, g in zip(labels, grams)]
        ax.legend(
            wedges, legend_labels,
            title="Macronutrients",
            loc='center left', bbox_to_anchor=(1.00, 0.5),
            frameon=False, borderaxespad=0.0
        )

        ax.axis('equal'); ax.set_frame_on(False)

        canvas = FigureCanvas(fig)
        self._canvas = canvas

        # משתמשים בלייאאוט קיים ומרכזים את הקנבס
        if self.chart_widget.layout() is None:
            lay = QVBoxLayout(self.chart_widget)
            lay.setContentsMargins(0, 0, 0, 0)
        else:
            lay = self.chart_widget.layout()
        lay.addWidget(canvas, 0, Qt.AlignCenter)

    def update_nutrition_data(self, data):
        lay = self.chart_widget.layout()
        if lay:
            for i in reversed(range(lay.count())):
                w = lay.itemAt(i).widget()
                if w:
                    w.setParent(None)
                    w.deleteLater()
        self.create_chart(data)



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

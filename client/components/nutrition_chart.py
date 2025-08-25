# client/components/nutrition_chart.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')


class NutritionChart(QFrame):
    def __init__(self, nutrition_data=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setFixedHeight(280)
        
        # Apply card styling to match your theme
        self.setStyleSheet('''
            QFrame[class="card"] {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
            }
            QFrame[class="card"]:hover {
                border-color: #10b981;
            }
        ''')
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Chart container
        self.chart_widget = QWidget()
        layout.addWidget(self.chart_widget)
        
        # Default nutrition data if none provided
        if nutrition_data is None:
            nutrition_data = {
                'calories': 300,
                'protein': 25,
                'carbs': 35,
                'fat': 15
            }
        
        self.create_chart(nutrition_data)
    
    def create_chart(self, nutrition_data):
        """Pie/Donut נקי בלי רווחים וללא חפיפות טקסט"""
        # חישוב לפי קלוריות מכל מאקרו
        protein_cal = float(nutrition_data.get('protein', 0)) * 4
        carbs_cal   = float(nutrition_data.get('carbs',   0)) * 4
        fat_cal     = float(nutrition_data.get('fat',     0)) * 9

        if protein_cal == 0 and carbs_cal == 0 and fat_cal == 0:
            protein_cal, carbs_cal, fat_cal = 100, 140, 135  # fallback סביר

        # סדר עקבי + סינון אפסים
        parts = [
            ("Carbs",   carbs_cal,   "#38bdf8", nutrition_data.get("carbs",   0)),
            ("Protein", protein_cal, "#34d399", nutrition_data.get("protein", 0)),
            ("Fat",     fat_cal,     "#a78bfa", nutrition_data.get("fat",     0)),
        ]
        parts = [p for p in parts if p[1] > 0.01]

        labels  = [p[0] for p in parts]
        sizes   = [p[1] for p in parts]       # בקלוריות – לזה pie מסתכל
        colors  = [p[2] for p in parts]
        grams   = [int(round(p[3])) for p in parts]  # לגרמים ב-legend

        # פיגור וקאנבס
        fig = Figure(figsize=(7, 5), dpi=100, facecolor='white', tight_layout=True)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # דונאט נקי: בלי explode, בלי קצוות לבנים, בלי labels על הפלח
        wedges, _texts, autotexts = ax.pie(
            sizes,
            labels=None,
            colors=colors,
            autopct=lambda pct: f"{pct:.0f}%" if pct >= 4 else "",  # מציגים אחוזים רק מפלחי 4%+
            startangle=90,
            counterclock=False,
            pctdistance=0.72,
            wedgeprops={'width': 0.48, 'edgecolor': 'none', 'linewidth': 0},  # אין חריצים
            textprops={'fontsize': 11, 'color': 'white', 'weight': 'bold'}
        )

        # כותרת קלוריות — משאירים כמו שהיה
        fig.suptitle(f'Total: {int(nutrition_data.get("calories", 0))} calories',
                    fontsize=16, fontweight='bold', color='#374151', y=0.98)

        # Legend אלגנטי עם גרמים
        legend_labels = [f"{lbl}  {g}g" for lbl, g in zip(labels, grams)]
        ax.legend(
            wedges, legend_labels,
            title="Macronutrients",
            loc='center left', bbox_to_anchor=(1.02, 0.5),
            frameon=False, borderaxespad=0.0
        )

        ax.axis('equal')      # עיגול מושלם
        ax.set_frame_on(False)

        # הזרקת הקאנבס ל-QWidget
        chart_layout = QVBoxLayout(self.chart_widget)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.addWidget(canvas)



# Simple local nutrition calculation
def calculate_nutrition_from_ingredients(ingredients):
    """Local nutrition estimation based on ingredients"""
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
    found_ingredients = 0
    
    for ingredient in ingredients:
        name = ingredient.get('name', '').lower()
        for key, values in nutrition_db.items():
            if key in name:
                found_ingredients += 1
                # Estimate portions based on ingredient type
                if key in ['flour']:
                    portion = 1.0  # 100g
                elif key in ['egg']:
                    portion = 0.5  # 50g per egg
                elif key in ['milk']:
                    portion = 3.0  # 300ml
                elif key in ['sugar']:
                    portion = 0.2  # 20g
                elif key in ['oil', 'butter']:
                    portion = 0.15  # 15g
                elif key in ['chicken', 'rice', 'potato']:
                    portion = 1.5  # 150g
                else:
                    portion = 0.1  # 10g for spices
                
                total_cal += values['cal'] * portion
                total_protein += values['protein'] * portion
                total_carbs += values['carbs'] * portion
                total_fat += values['fat'] * portion
                break
    
    # Default values if no ingredients found
    if found_ingredients == 0:
        return {'calories': 300, 'protein': 20, 'carbs': 35, 'fat': 12}
    
    return {
        'calories': int(total_cal),
        'protein': int(total_protein), 
        'carbs': int(total_carbs),
        'fat': int(total_fat)
    }
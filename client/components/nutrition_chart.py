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
        """Create a beautiful pie chart for nutrition data"""
        # Calculate calories from macronutrients (protein=4cal/g, carbs=4cal/g, fat=9cal/g)
        protein_cal = nutrition_data['protein'] * 4
        carbs_cal = nutrition_data['carbs'] * 4
        fat_cal = nutrition_data['fat'] * 9
        
        # Ensure we have meaningful data - use default if all zeros
        if protein_cal == 0 and carbs_cal == 0 and fat_cal == 0:
            protein_cal, carbs_cal, fat_cal = 100, 140, 135
            nutrition_data = {'calories': 375, 'protein': 25, 'carbs': 35, 'fat': 15}
        
        # Data for pie chart - only show non-zero values
        sizes = []
        labels = []
        colors = []
        
        if protein_cal > 5:
            sizes.append(protein_cal)
            labels.append(f'Protein\n{nutrition_data["protein"]}g')
            colors.append('#10b981')  # Green
            
        if carbs_cal > 5:
            sizes.append(carbs_cal)
            labels.append(f'Carbs\n{nutrition_data["carbs"]}g')
            colors.append('#0ea5e9')  # Blue
            
        if fat_cal > 5:
            sizes.append(fat_cal)
            labels.append(f'Fat\n{nutrition_data["fat"]}g')
            colors.append('#f59e0b')  # Orange
        
        # Create matplotlib figure with better proportions
        fig = Figure(figsize=(7, 6), dpi=90, facecolor='white')
        canvas = FigureCanvas(fig)
        
        # Create subplot with custom positioning
        ax = fig.add_subplot(111, position=[0.1, 0.1, 0.8, 0.7])
        
        # Create pie chart with better styling
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            colors=colors,
            autopct='%1.0f%%',
            startangle=90,
            explode=[0.05] * len(sizes),  # Smaller separation
            textprops={'fontsize': 12, 'color': '#374151', 'weight': 'bold'},
            pctdistance=0.75,  # Percentages closer to center
            labeldistance=1.15,  # Labels further out
            wedgeprops={'linewidth': 2, 'edgecolor': 'white'}  # White borders
        )
        
        # Style the title - positioned at top
        fig.suptitle(f'Total: {nutrition_data["calories"]} calories', 
                    fontsize=16, fontweight='bold', color='#374151', y=0.9)
        
        # Style the percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
        
        # Style the labels - make them more readable
        for text in texts:
            text.set_fontsize(11)
            text.set_color('#374151')
            text.set_fontweight('600')
            text.set_ha('center')  # Center alignment
        
        # Perfect circle
        ax.axis('equal')
        
        # Remove axes completely
        ax.set_frame_on(False)
        
        # Add canvas to widget
        chart_layout = QVBoxLayout(self.chart_widget)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.addWidget(canvas)
    
    def update_nutrition_data(self, nutrition_data):
        """Update chart with new nutrition data"""
        # Clear existing chart
        for i in reversed(range(self.chart_widget.layout().count())): 
            self.chart_widget.layout().itemAt(i).widget().setParent(None)
        
        # Create new chart
        self.create_chart(nutrition_data)


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
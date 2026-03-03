import sys
import os
os.environ["QT_LOGGING_RULES"] = "*.warning=false"
import math
import re
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QGridLayout, 
                             QPushButton, QTextEdit, QHBoxLayout, QLabel)
from PyQt5.QtGui import QFont, QIcon, QTextOption, QTextCursor
from PyQt5.QtCore import Qt

class JEEEngineeringCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JEE Advanced Engineering Calculator")
        
        # Window Maximization & Icon
        self.setMinimumSize(450, 750)
        self.setWindowIcon(QIcon('icon.png')) 
        
        self.setStyleSheet("background-color: #202124;")
        
        self.history_log = []
        self.is_degree = True 
        self.sci_mode = False 

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(self.main_layout)

        # --- Top Bar ---
        top_bar = QHBoxLayout()
        self.history_btn = QPushButton("🕒") 
        self.history_btn.setFixedSize(70, 40) 
        self.history_btn.setStyleSheet("color: white; font-size: 24px; border: none;")
        self.history_btn.clicked.connect(self.toggle_history_view)
        
        self.unit_toggle = QPushButton("DEG")
        self.unit_toggle.setFixedSize(60, 30)
        self.unit_toggle.setStyleSheet("background-color: #3c4043; color: #8ab4f8; border-radius: 5px; font-weight: bold;")
        self.unit_toggle.clicked.connect(self.switch_units)
        
        top_bar.addWidget(self.history_btn)
        top_bar.addStretch()
        top_bar.addWidget(self.unit_toggle)
        self.main_layout.addLayout(top_bar)

        # --- History Panel ---
        self.history_panel = QTextEdit()
        self.history_panel.setReadOnly(True)
        self.history_panel.setStyleSheet("background-color: #303134; color: #e8eaed; border: none; font-size: 16px;")
        self.history_panel.hide()
        self.main_layout.addWidget(self.history_panel)

        # --- Main Display (Multi-line with Word Wrap) ---
        self.display = QTextEdit()
        self.display.setMinimumHeight(100)
        self.display.setMaximumHeight(180) 
        
        doc = self.display.document()
        option = doc.defaultTextOption()
        option.setAlignment(Qt.AlignRight)
        doc.setDefaultTextOption(option)
        
        self.display.setStyleSheet("background-color: #202124; color: white; border: none; font-size: 32px; padding: 10px;")
        self.main_layout.addWidget(self.display)

        # --- Scientific Grid (Saffron & Bold) ---
        self.sci_container = QWidget()
        self.sci_grid = QGridLayout(self.sci_container)
        sci_buttons = [
            ('sin', '#FF9933'), ('cos', '#FF9933'), ('tan', '#FF9933'), ('π', '#FF9933'),
            ('asin', '#FF9933'), ('acos', '#FF9933'), ('atan', '#FF9933'), ('e', '#FF9933'),
            ('ln', '#FF9933'), ('log', '#FF9933'), ('n!', '#FF9933'), ('Abs', '#FF9933'),
            ('exp', '#FF9933'), ('10ˣ', '#FF9933'), ('xʸ', '#FF9933'), ('ʸ√x', '#FF9933')
        ]
        self.create_grid(self.sci_grid, sci_buttons, 4, color_all=True)
        self.sci_container.hide()
        self.main_layout.addWidget(self.sci_container)

        # --- Basic Grid (1st Row Saffron & Bold) ---
        self.basic_container = QWidget()
        self.basic_grid = QGridLayout(self.basic_container)
        basic_buttons = [
            ('()', '#FF9933'), ('CE', '#FF9933'), ('C', '#FF9933'), ('%', '#FF9933'),
            ('1/x', '#3c4043'), ('x²', '#3c4043'), ('√', '#3c4043'), ('÷', '#8ab4f8'),
            ('7', '#3c4043'), ('8', '#3c4043'), ('9', '#3c4043'), ('×', '#8ab4f8'),
            ('4', '#3c4043'), ('5', '#3c4043'), ('6', '#3c4043'), ('-', '#8ab4f8'),
            ('1', '#3c4043'), ('2', '#3c4043'), ('3', '#3c4043'), ('+', '#8ab4f8'),
            ('.', '#3c4043'), ('0', '#3c4043'), ('⌫', '#3c4043'), ('=', '#8ab4f8')
        ]
        self.create_grid(self.basic_grid, basic_buttons, 4, color_first_row=True)
        self.main_layout.addWidget(self.basic_container)

        # --- Bottom Area: Toggle and Signature ---
        bottom_layout = QHBoxLayout()
        
        self.mode_toggle = QPushButton("INV (Scientific)")
        self.mode_toggle.setStyleSheet("color: #8ab4f8; font-size: 12px; border: none; padding: 5px;")
        self.mode_toggle.clicked.connect(self.toggle_sci_mode)
        bottom_layout.addWidget(self.mode_toggle, alignment=Qt.AlignLeft)
        
        self.signature = QLabel("आमन् आर्य")
        self.signature.setStyleSheet("color: #FF9933; font-size: 11px; font-weight: bold; padding-right: 5px;")
        bottom_layout.addWidget(self.signature, alignment=Qt.AlignRight | Qt.AlignBottom)
        
        self.main_layout.addLayout(bottom_layout)

    def create_grid(self, layout, buttons, cols, color_all=False, color_first_row=False):
        row, col = 0, 0
        for text, color in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(55)
            is_saffron = color_all or (color_first_row and row == 0)
            text_color = "#FF9933" if is_saffron else (color if color != '#3c4043' else 'white')
            weight = "bold" if is_saffron else "normal"
            style = f"background-color: #3c4043; color: {text_color}; border-radius: 10px; font-size: 16px; font-weight: {weight};"
            if text == '=': style = "background-color: #8ab4f8; color: #202124; border-radius: 10px; font-size: 18px; font-weight: bold;"
            btn.setStyleSheet(style)
            btn.clicked.connect(self.on_click)
            layout.addWidget(btn, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def switch_units(self):
        self.is_degree = not self.is_degree
        self.unit_toggle.setText("DEG" if self.is_degree else "RAD")
        
        # Dynamically transform existing text units
        current_text = self.display.toPlainText()
        if self.is_degree:
            new_text = current_text.replace('rad', '°')
        else:
            new_text = current_text.replace('°', 'rad')
            
        if current_text != new_text:
            self.display.setPlainText(new_text)
            cursor = self.display.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.display.setTextCursor(cursor)

    def toggle_sci_mode(self):
        self.sci_mode = not self.sci_mode
        self.sci_container.setVisible(self.sci_mode)
        self.mode_toggle.setText("Basic Mode" if self.sci_mode else "INV (Scientific)")

    def toggle_history_view(self):
        if self.history_panel.isHidden():
            self.history_panel.show()
            self.basic_container.hide()
            self.sci_container.hide()
            self.display.hide()
            self.history_btn.setText("BACK") 
            self.history_btn.setStyleSheet("color: #8ab4f8; font-size: 16px; font-weight: bold; border: none;")
            self.history_panel.setPlainText("\n".join([f"{eq} = {res}" for eq, res in self.history_log[-10:]]))
        else:
            self.history_panel.hide()
            self.basic_container.show()
            if self.sci_mode: self.sci_container.show()
            self.display.show()
            self.history_btn.setText("🕒") 
            self.history_btn.setStyleSheet("color: white; font-size: 24px; border: none;")

    def format_result(self, val):
        if float(val).is_integer(): return str(int(val))
        s = f"{val:.15f}".split('.')
        decimal_part = s[1]
        round_to = 7
        non_zero_seen = 0
        for i, char in enumerate(decimal_part):
            if char != '0': non_zero_seen += 1
            if non_zero_seen == 3:
                round_to = max(7, i + 1)
                break
        res = round(val, round_to)
        return f"{res:.{round_to}f}".rstrip('0').rstrip('.')

    def on_click(self):
        btn_text = self.sender().text()
        current = self.display.toPlainText()
        cursor = self.display.textCursor()
        suffix = "°" if self.is_degree else "rad"

        if btn_text == "C" or btn_text == "CE": 
            self.display.clear()
        elif btn_text == "⌫": 
            cursor.deletePreviousChar()
        elif btn_text == "=":
            open_br = current.count('(')
            close_br = current.count(')')
            if open_br > close_br:
                current += ')' * (open_br - close_br)
                self.display.setPlainText(current)
            
            try:
                # 1. Base Setup
                expr = current.replace('×', '*').replace('÷', '/').replace('%', '/100')
                expr = expr.replace('10ˣ', '10**').replace('²', '**2').replace('⁻¹', '**(-1)')
                
                # 2. Degrees and Radians
                expr = re.sub(r'(\d+\.?\d*)°', r'radians(\1)', expr)
                expr = re.sub(r'(\d+\.?\d*)rad', r'\1', expr)
                
                # 3. Power and Root (Reverse Entry Method B)
                expr = expr.replace('xʸ', '**')
                expr = re.sub(r'(\d+\.?\d*)ʸ√x(\d+\.?\d*)', r'(\1)**(1/\2)', expr)
                
                # 4. Implicit Multiplication (Including e4 -> e*4)
                expr = re.sub(r'(\d+)(sin|cos|tan|asin|acos|atan|ln|log|Abs|exp|π|e|√|\()', r'\1*\2', expr)
                expr = re.sub(r'(π|e)(\d+)', r'\1*\2', expr) 
                
                # 5. Visual to Math mapping
                expr = expr.replace('π', 'pi')
                expr = expr.replace('√(', 'sqrt(')
                expr = expr.replace('Abs(', 'abs(')
                expr = re.sub(r'(\d+)!', r'factorial(\1)', expr)
                expr = re.sub(r'\b0+(?=\d)', '', expr) 

                # 6. Safe Dictionary Evaluator
                safe_math_env = {
                    "sin": math.sin, "cos": math.cos, "tan": math.tan,
                    "asin": math.asin, "acos": math.acos, "atan": math.atan,
                    "ln": math.log, "log": math.log10, "exp": math.exp,
                    "abs": abs, "sqrt": math.sqrt, "factorial": math.factorial,
                    "radians": math.radians, "e": math.e, "pi": math.pi
                }

                res = eval(expr, {"__builtins__": {}}, safe_math_env)
                
                formatted = self.format_result(res)
                self.history_log.append((current, formatted))
                
                self.display.setPlainText(formatted)
                cursor = self.display.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.display.setTextCursor(cursor)
                
            except:
                pass 
        else:
            text_before_cursor = current[:cursor.position()]
            
            if btn_text.isdigit() or btn_text == '.':
                trig_funcs = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']
                if any(func + '(' in text_before_cursor for func in trig_funcs) and ')' not in text_before_cursor.split('(')[-1]:
                    if text_before_cursor.endswith(suffix):
                        for _ in range(len(suffix)):
                            cursor.deletePreviousChar()
                        cursor.insertText(btn_text + suffix)
                    else:
                        cursor.insertText(btn_text + suffix)
                else:
                    cursor.insertText(btn_text)
            
            elif btn_text in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'ln', 'log', 'Abs', 'exp', '√']:
                cursor.insertText(btn_text + "(")
                
            elif btn_text == "()":
                cursor.insertText(")" if current.count('(') > current.count(')') else "(")
            elif btn_text == 'x²': cursor.insertText('²')
            elif btn_text == '1/x': cursor.insertText('⁻¹')
            elif btn_text == 'n!': cursor.insertText('!')
            elif btn_text == 'xʸ': cursor.insertText('xʸ')
            elif btn_text == 'ʸ√x': cursor.insertText('ʸ√x')
            else: 
                cursor.insertText(btn_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = JEEEngineeringCalculator()
    calc.show()
    sys.exit(app.exec_())
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QDockWidget, QTextBrowser, QLabel, QToolButton, QMenu, QPushButton
from ui.components import Button, IconButton
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSettings, QPoint
from logic.calculator_logic import calculate
from ui.error_ui import Error
import re

def load_stylesheet(path):
    with open(path, 'r') as f:
        return f.read()

light_stylesheet = load_stylesheet('ui/styles/light.qss')
dark_stylesheet = load_stylesheet('ui/styles/dark.qss')


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(50)
        self._startPos = QPoint(0, 0)
        self._clickPos = None

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)

        self.logo_label = QLabel()
        self.logo_label.setStyleSheet("background-color: transparent;")
        pixmap = QPixmap("assets/icons/calculator.ico")
        self.logo_label.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(self.logo_label)

        self.title_label = QLabel("Basic Calculator")
        self.title_font = QFont("Segoe UI Variable", 14, QFont.Bold)
        self.title_label.setFont(self.title_font)
        layout.addWidget(self.title_label)

        layout.addStretch()

        self.min_button = QPushButton("─")
        self.min_button.setFixedSize(32, 32)
        self.min_button.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.min_button)

        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(32, 32)
        self.close_button.clicked.connect(self.parent.close)
        layout.addWidget(self.close_button)

        if self.parent.mode:
            self.mode = "dark"
        else:
            self.mode = "light"
        self.update_theme(self.mode)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #19232d;")

    def update_theme(self, mode):
        if mode == "dark":
            bg_color = "#19232d"
            text_color = "#F0F0F0"
            btn_hover = "rgba(255, 255, 255, 0.2)"
        else:
            bg_color = "#f0f0f0"
            text_color = "#212121"
            btn_hover = "rgba(0, 0, 0, 0.1)"

        self.setStyleSheet(f"background-color: {bg_color};")

        self.title_label.setStyleSheet(f"background-color: transparent; color: {text_color}; font: bold 14px;")

        btn_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {text_color};
                border: none;
                font: bold 16px;
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
            }}
        """
        self.min_button.setStyleSheet(btn_style)
        self.close_button.setStyleSheet(btn_style)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._clickPos = event.globalPos()
            self._startPos = self.parent.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        if self._clickPos is not None:
            delta = event.globalPos() - self._clickPos
            self.parent.move(self._startPos + delta)
        event.accept()

    def mouseReleaseEvent(self, event):
        self._clickPos = None
        event.accept()

class CalculatorUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.history = []

        self.base_width = 350
        self.base_height = 620
        self.expanded_width = 550

        self.settings = QSettings("MagicCo", "CalculatorApp")
        
        self.load_settings()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)
        self.icon = QIcon("assets/icons/calculator.ico")
        self.setMinimumSize(self.base_width, self.base_height)
        self.setMaximumSize(self.expanded_width, self.base_height)
        self.setWindowIcon(self.icon)
        self.setGeometry(100, 100, 300, 400)
        
        self.create_ui()

    def create_ui(self):
        self.central_widget = QWidget()

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        self.display = QLineEdit()
        self.display.setFixedHeight(80)
        self.display.setFont(QFont("Helvetica", 24))
        self.display.setAlignment(Qt.AlignRight)
        self.display.setStyleSheet("""
            background-color: #222;
            color: white;
            border-radius: 10px;
            padding-right: 15px;
        """)
        self.display.returnPressed.connect(self.on_enter_pressed)
        self.main_layout.addWidget(self.display)

        self.top_bar = QHBoxLayout()
        self.main_layout.addLayout(self.top_bar)

        self.toggle_dark_mode_btn = Button("Toggle Dark Mode")
        self.toggle_dark_mode_btn.setFixedHeight(50)
        self.toggle_dark_mode_btn.setFont(QFont("Helvetica", 12))
        self.toggle_dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        self.top_bar.addWidget(self.toggle_dark_mode_btn)

        history_icon_paths = {"light_normal": "assets/icons/light/normal_history.ico", "light_hover": "assets/icons/light/hover_history.ico", "dark_normal": "assets/icons/dark/normal_history.ico", "dark_hover": "assets/icons/dark/hover_history.ico"}
        self.history_btn = IconButton(history_icon_paths, self.mode)
        self.history_btn.setFixedSize(50, 50)
        self.history_btn.clicked.connect(self.toggle_history_panel)
        self.top_bar.addWidget(self.history_btn)

        self.history_panel = QDockWidget("", self)
        self.history_panel.setAllowedAreas(Qt.RightDockWidgetArea)
        self.history_panel.setFixedSize(200, self.base_height)
        self.history_list = QTextBrowser()
        self.history_list.setFont(QFont("Courier New", 12))
        self.history_panel.setWidget(self.history_list)
        self.history_panel.setVisible(False)
        self.history_panel.setFeatures((QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable) & ~QDockWidget.DockWidgetClosable)
        self.history_panel.setTitleBarWidget(QWidget())
        self.addDockWidget(Qt.RightDockWidgetArea, self.history_panel)

        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(8)

        buttons = [
            'C', '(', ')', '^',
            '7', '8', '9', '÷',
            '4', '5', '6', '×',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        self.buttons = {}
        row, col = 0, 0
        for btn_text in buttons:
            btn = Button(btn_text)
            btn.setFixedSize(70, 70)
            btn.setFont(QFont("Helvetica", 18))
            btn.setStyleSheet(self.button_style(btn_text))
            btn.clicked.connect(lambda checked, b=btn_text: self.on_button_clicked(b))
            buttons_layout.addWidget(btn, row, col)
            self.buttons[btn_text] = btn
            col += 1
            if col > 3:
                col = 0
                row += 1

        self.main_layout.addLayout(buttons_layout)

        self.central_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.central_widget)


    def button_style(self, btn_text):
        if btn_text in ['C', '(', ')', '^']:
            return "background-color: #555; color: white; border-radius: 15px;"
        elif btn_text in ['÷', '×', '-', '+', '=']:
            return "background-color: #ff9500; color: white; border-radius: 15px;"
        else:
            return "background-color: #333; color: white; border-radius: 15px;"

    def on_button_clicked(self, button_text):
        text = self.display.text()
        if button_text == "=":
            try:
                result = calculate(text)
                self.display.setText(result)
                self.add_to_history(text, result)
            except Exception as e:
                error = Error()
                error.show_error_message(e)
        elif button_text == 'C':
            self.display.setText('')
        else:
            self.display.setText(text + button_text)

    def on_enter_pressed(self):
        text = self.display.text()
        self.display.setText(calculate(text))

    def toggle_dark_mode(self):
        if self.styleSheet() == dark_stylesheet:
            self.setStyleSheet(light_stylesheet)
            self.title_bar.update_theme("light")
            self.history_btn.toggle_mode("light")
            self.settings.setValue("dark_mode", False)
        else:
            self.setStyleSheet(dark_stylesheet)
            self.title_bar.update_theme("dark")
            self.history_btn.toggle_mode("dark")
            self.settings.setValue("dark_mode", True)

    def add_to_history(self, operation, result):
        history_text = f"{operation}=\n{result}"
        self.history.append((operation+"=", result))
        self.history_list.append(history_text)
        self.history_list.append('─────────────')

    def toggle_history_panel(self):
        if self.history_panel.isVisible():
            self.history_panel.hide()
            self.setFixedSize(self.base_width, self.base_height)
        else:
            self.history_panel.show()
            self.setMinimumSize(self.base_width, self.base_height)
            self.setMaximumSize(self.expanded_width, self.base_height)
            self.resize(self.expanded_width, self.base_height)
            self.setFixedSize(self.expanded_width, self.base_height)

    def load_settings(self):
        self.mode = self.settings.value("dark_mode", False, type=bool)
        if self.mode:
            self.setStyleSheet(dark_stylesheet)
        else:
            self.setStyleSheet(light_stylesheet)
import sys
import subprocess
import time
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea,
    QDialog, QFormLayout, QSpinBox, QComboBox, QDialogButtonBox, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSettings
from PySide6.QtGui import QFont, QPixmap, QKeyEvent
import numpy as np
import matplotlib.pyplot as plt

# SettingsDialog: Pre-terminal configuration window
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Terminal Settings")
        # Use QSettings to persist settings between runs
        self.settings = QSettings("MyCompany", "TerminalGUI")
        # Load saved values or default values
        default_font = self.settings.value("font", "Times New Roman")
        default_font_size = int(self.settings.value("font_size", 20))
        default_color = self.settings.value("text_color", "green")

        # Create main horizontal layout
        main_layout = QHBoxLayout(self)
        
        # Left side: form layout for settings
        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)
        
        # Font Size (word size)
        self.fontSizeSpin = QSpinBox()
        self.fontSizeSpin.setRange(8, 72)
        self.fontSizeSpin.setValue(default_font_size)
        form_layout.addRow("Font Size:", self.fontSizeSpin)
        
        # Font selection
        self.fontCombo = QComboBox()
        self.fontCombo.addItems(["Times New Roman", "Courier New", "Arial", "Verdana"])
        index = self.fontCombo.findText(default_font)
        if index >= 0:
            self.fontCombo.setCurrentIndex(index)
        form_layout.addRow("Font:", self.fontCombo)
        
        # Text color selection
        self.colorCombo = QComboBox()
        self.colorCombo.addItems(["green", "yellow", "red", "blue", "white"])
        index = self.colorCombo.findText(default_color)
        if index >= 0:
            self.colorCombo.setCurrentIndex(index)
        form_layout.addRow("Text Color:", self.colorCombo)
        
        # OK and Cancel buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        # Right side: Preview area
        self.previewLabel = QLabel("Sample Terminal Text")
        self.previewLabel.setAlignment(Qt.AlignCenter)
        self.previewLabel.setWordWrap(True)
        # Use an expanding size policy so the preview shows its full content
        self.previewLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.previewLabel)
        
        # Connect changes to update preview
        self.fontSizeSpin.valueChanged.connect(self.updatePreview)
        self.fontCombo.currentTextChanged.connect(self.updatePreview)
        self.colorCombo.currentTextChanged.connect(self.updatePreview)
        self.updatePreview()
        
        # Fix overall dialog size so the window doesn't move
        self.setFixedSize(400, 200)
    
    def updatePreview(self):
        font = QFont(self.fontCombo.currentText(), self.fontSizeSpin.value())
        self.previewLabel.setFont(font)
        self.previewLabel.setStyleSheet(f"color: {self.colorCombo.currentText()};")
    
    def getSettings(self):
        return {
            "font_name": self.fontCombo.currentText(),
            "font_size": self.fontSizeSpin.value(),
            "text_color": self.colorCombo.currentText()
        }
    
    def accept(self):
        # Save settings for next time
        settings = self.getSettings()
        self.settings.setValue("font", settings["font_name"])
        self.settings.setValue("font_size", settings["font_size"])
        self.settings.setValue("text_color", settings["text_color"])
        super().accept()

# WorkerThread used for running external scripts
class WorkerThread(QThread):
    output_signal = Signal(str)
    finished_signal = Signal()
    progress_signal = Signal(int, int)

    def __init__(self, script_name, user_inputs=None, show_progress=False):
        super().__init__()
        self.script_name = script_name
        self.user_inputs = user_inputs or []
        self.show_progress = show_progress
        self.process = None  # Store subprocess reference

    def run(self):
        if self.show_progress:
            start_time = time.time()
            elapsed_time = 0
            progress = 0
            self.process = subprocess.Popen(
                ["python", "-u", self.script_name] + self.user_inputs,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            if os.name == "nt":
                import msvcrt
                msvcrt.setmode(self.process.stdout.fileno(), os.O_TEXT)
                msvcrt.setmode(self.process.stderr.fileno(), os.O_TEXT)
            first_output_received = False
            while not first_output_received:
                line = self.process.stdout.readline()
                if line:
                    first_output_received = True
                    self.output_signal.emit(f"Main: {line.strip()}")
                    break
                elapsed_time = int(time.time() - start_time)
                progress = min(100, elapsed_time * 10)
                self.progress_signal.emit(progress, elapsed_time)
                time.sleep(1)
            for line in iter(self.process.stdout.readline, ""):
                self.output_signal.emit(f"Main: {line.strip()}")
            for error_line in iter(self.process.stderr.readline, ""):
                self.output_signal.emit(f"Main: ERROR: {error_line.strip()}")
            self.process.stdout.close()
            self.process.stderr.close()
            self.process.wait()
            self.finished_signal.emit()
        else:
            try:
                self.process = subprocess.Popen(
                    ["python", self.script_name] + self.user_inputs,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
            except Exception as e:
                self.output_signal.emit(f"Main: ERROR: Failed to start script: {e}")
                return
            while self.process.poll() is None:
                output = self.process.stdout.readline().strip()
                error_output = self.process.stderr.readline().strip()
                if output:
                    self.output_signal.emit(f"Main: {output}")
                if error_output:
                    self.output_signal.emit(f"Main: ERROR: {error_output}")
            self.process.stdout.close()
            self.process.stderr.close()
            self.process.wait()
            self.finished_signal.emit()

# TerminalGUI: Main terminal-based interface
class TerminalGUI(QWidget):
    def __init__(self, font_name="Times New Roman", font_size=20, text_color="green"):
        super().__init__()
        self.font_name = font_name
        self.font_size = font_size
        self.text_color = text_color
        self.worker_thread = None
        self.waiting_for_input = False
        self.waiting_for_predictions = False
        self.user_inputs = []
        self.run_all_mode = False  # Flag set when "run_all" is chosen
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Terminal GUI")
        self.setGeometry(0, 0, 1920, 1080)
        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Horizontal layout: terminal output and graph area
        self.h_layout = QHBoxLayout()
        main_layout.addLayout(self.h_layout)
        
        # Terminal output (scrollable)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.h_layout.addWidget(self.scroll_area, stretch=2)
        self.output_label = QLabel()
        self.output_label.setAlignment(Qt.AlignTop)
        output_font = QFont(self.font_name, self.font_size)
        self.output_label.setFont(output_font)
        self.output_label.setStyleSheet(f"color: {self.text_color};")
        self.scroll_area.setWidget(self.output_label)
        
        # Graph container (initially hidden)
        self.graph_container = QWidget()
        self.graph_layout = QVBoxLayout()
        self.graph_container.setLayout(self.graph_layout)
        self.h_layout.addWidget(self.graph_container, stretch=3)
        self.graph_placeholder = QLabel()
        self.graph_placeholder.setAlignment(Qt.AlignRight)
        self.graph_layout.addWidget(self.graph_placeholder)
        self.graph_container.hide()  # Hide right side until needed
        
        # Bottom section: input field
        bottom_layout = QHBoxLayout()
        main_layout.addLayout(bottom_layout)
        bottom_layout.setAlignment(Qt.AlignBottom)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command...")
        self.input_field.returnPressed.connect(self.process_input)
        input_font = QFont(self.font_name, self.font_size)
        self.input_field.setFont(input_font)
        self.input_field.setStyleSheet(f"color: {self.text_color};")
        bottom_layout.addWidget(self.input_field)
        self.input_field.setFocus()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            if self.worker_thread is not None and self.worker_thread.isRunning():
                if hasattr(self.worker_thread, "process") and self.worker_thread.process:
                    self.worker_thread.process.terminate()
                    self.update_terminal("Main: Execution stopped by user (Ctrl+C pressed).")
                    self.input_field.setReadOnly(False)
                    self.input_field.clear()
                    self.input_field.setStyleSheet(f"color: {self.text_color};")
                    return
        self.input_field.setFocus()
        self.input_field.insert(event.text())

    def update_terminal(self, message):
        current_output = self.output_label.text()
        self.output_label.setText(f"{current_output}\n{message}")
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def process_input(self):
        self.input_field.setFocus()
        input_text = self.input_field.text().strip()
        if not input_text:
            return

        # Map numeric commands (top-level) if not in interactive flow.
        if not (self.waiting_for_input or self.waiting_for_predictions) and input_text.isdigit():
            command_map = {
                "1": "run_all",
                "2": "run_data_prepare",
                "3": "run_combination_analysis",
                "4": "run_current_graph_analysis",
                "5": "clear",
                "6": "quit"
            }
            input_text = command_map.get(input_text, input_text)

        # Map numeric choices for trend mode if in interactive flow.
        if self.waiting_for_input and input_text.isdigit():
            interactive_map = {
                "1": "random",
                "2": "top3",
                "3": "single most frequency"
            }
            input_text = interactive_map.get(input_text, input_text)

        self.update_terminal(f"Main: {input_text}")
        self.input_field.clear()
        
        # Interactive flow for choosing Trend Mode
        if self.waiting_for_input:
            if input_text.lower() == "cancel":
                self.waiting_for_input = False
                self.waiting_for_predictions = False
                self.user_inputs = []
                self.update_terminal("Main: run_combination_analysis canceled.")
                return
            if input_text.lower() == "quit":
                self.close()
                return
            if input_text.lower() in ["random", "top3", "single most frequency"]:
                self.user_inputs.append(input_text.lower())
                self.waiting_for_input = False
                self.waiting_for_predictions = True
                self.update_terminal("Main: Choose How Many Predictions?")
                return
            else:
                self.update_terminal("Main: Error: Invalid input. Please retype or type 'cancel' to cancel run_combination_analysis.")
            return

        # Interactive flow for choosing number of predictions
        if self.waiting_for_predictions:
            if input_text.lower() == "quit":
                self.close()
                return
            if input_text.lower() == "cancel":
                self.waiting_for_predictions = False
                self.user_inputs = []
                self.update_terminal("Main: run_combination_analysis canceled.")
                return
            if input_text.isdigit():
                self.user_inputs.append(input_text)
                self.run_combination_analysis()
            else:
                self.update_terminal("Main: Error: Invalid input. Please enter a number or type 'cancel' to cancel.")
            return

        # Process top-level commands
        if input_text.lower() == "run_all":
            self.run_all_mode = True
            self.run_data_prepare()
        elif input_text.lower() == "run_data_prepare":
            self.run_data_prepare()
        elif input_text.lower() == "run_combination_analysis":
            self.update_terminal("Main: Choose Trend Mode:\n1 - Random\n2 - Top3\n3 - Single Most Frequency")
            self.waiting_for_input = True
            self.user_inputs = []
        elif input_text.lower() == "run_current_graph_analysis":
            result_file = os.path.join(os.getcwd(), "combination_analysis_result.txt")
            if not os.path.exists(result_file) or os.path.getsize(result_file) == 0:
                self.update_terminal("Main: run_current_graph_analysis is not exist, please run combination_analysis")
                return
            self.run_graph_analysis()
        elif input_text.lower() == "clear":
            self.output_label.setText("Terminal clear!\nType 'help' for available commands.")
            self.clear_graph_container()
            self.graph_container.hide()  # Hide the right side as well
        elif input_text.lower() == "quit":
            self.close()
        elif input_text.lower() == "help":
            help_text = """
Available commands:
1 - run_all (recommended when first using this program)
2 - run_data_prepare: Execute the Data_prepare.py script and show progress
3 - run_combination_analysis: Predict next draw based on historical trends
4 - run_current_graph_analysis: Activate embedded graph analysis tool (requires valid combination_analysis_result.txt)
5 - clear: Clear the output and graph area
6 - quit: Close the application
            """
            self.update_terminal(f"Main: {help_text}")
        else:
            self.update_terminal("Main: Unknown command. Type 'help' for available commands.")

    def clear_graph_container(self):
        for i in reversed(range(self.graph_layout.count())):
            widget = self.graph_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

    def run_data_prepare(self):
        self.update_terminal("Main: Running Data_prepare.py...")
        self.update_terminal("Main: Execution progress - 0% (0 sec)")
        self.input_field.setText("File is running,Please wait......")
        self.input_field.setStyleSheet(f"color: {self.text_color}; background-color: red;")
        self.input_field.setReadOnly(True)
        self.worker_thread = WorkerThread("Data_prepare.py", show_progress=True)
        self.worker_thread.output_signal.connect(self.update_terminal)
        self.worker_thread.progress_signal.connect(self.update_execution_progress)
        self.worker_thread.finished_signal.connect(self.script_finished)
        self.worker_thread.start()

    def update_execution_progress(self, progress, elapsed_time):
        self.update_terminal(f"Main: Execution progress - {progress}% ({elapsed_time} sec)")

    def script_finished(self):
        self.update_terminal("Main: Data_prepare.py execution completed.")
        self.input_field.setReadOnly(False)
        self.input_field.clear()
        self.input_field.setStyleSheet(f"color: {self.text_color};")
        # If run_all mode was chosen, then after Data_prepare, clear terminal and prompt for trend mode.
        if self.run_all_mode:
            self.run_all_mode = False
            self.output_label.setText("Terminal clear!\nType 'help' for available commands.")
            self.update_terminal("Main: Choose Trend Mode:\n1 - Random\n2 - Top3\n3 - Single Most Frequency")
            self.waiting_for_input = True

    def run_combination_analysis(self):
        self.waiting_for_predictions = False
        cwd = os.getcwd()
        script_path = os.path.join(cwd, "combination_analysis.py")
        self.input_field.setText("File is running,Please wait......")
        self.input_field.setStyleSheet(f"color: {self.text_color}; background-color: red;")
        self.input_field.setReadOnly(True)
        self.worker_thread = WorkerThread(script_path, self.user_inputs, show_progress=False)
        self.worker_thread.output_signal.connect(self.update_terminal)
        self.worker_thread.finished_signal.connect(self.display_result)
        self.worker_thread.start()
        self.user_inputs = []

    def display_result(self):
        result_file = os.path.join(os.getcwd(), "combination_analysis_result.txt")
        if os.path.exists(result_file):
            with open(result_file, "r", encoding="utf-8") as f:
                result_content = f.read()
            self.update_terminal(f"Main: Task Completed.\n{result_content}")
            # Note: The file is no longer cleared, so that its contents persist for graph analysis.
        else:
            self.update_terminal("Main: No result file found.")
        self.update_terminal("Main: Updating Data_Storage_Lib.py...")
        subprocess.run(["python", os.path.join(os.getcwd(), "Data_storage_Lib.py")])
        self.update_terminal("Main: Data_Storage_Lib.py updated successfully.")
        self.input_field.setReadOnly(False)
        self.input_field.clear()
        self.input_field.setStyleSheet(f"color: {self.text_color};")

    def run_graph_analysis(self):
        self.update_terminal("Main: Running graph analysis tool...")
        self.clear_graph_container()
        self.graph_container.show()  # Show the right side container when graph analysis is triggered
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
        import pyqtgraph as pg
        import importlib.util
        from sklearn.linear_model import LinearRegression
        from sklearn.neighbors import KNeighborsRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import mean_squared_error
        from PySide6.QtCore import QTimer

        class GraphAnalysisWidget(QWidget):
            def __init__(self):
                super().__init__()
                self.setStyleSheet("background-color: white;")
                main_layout = QHBoxLayout(self)
                self.plot_widget = pg.PlotWidget(title="Real vs Virtual Line Plot")
                self.plot_widget.setLabel('left', 'Y', units='(percentage)')
                self.plot_widget.setLabel('bottom', 'X', units='(point number)')
                self.plot_widget.showGrid(x=True, y=True)
                main_layout.addWidget(self.plot_widget, stretch=3)
                right_layout = QVBoxLayout()
                main_layout.addLayout(right_layout, stretch=1)
                self.text_edit = QTextEdit()
                self.text_edit.setReadOnly(True)
                right_layout.addWidget(self.text_edit)
                btn_layout = QHBoxLayout()
                self.next_button = QPushButton("Next Prediction")
                self.next_button.clicked.connect(self.on_next_button_clicked)
                btn_layout.addWidget(self.next_button)
                self.total_predict_button = QPushButton("Total Predict")
                self.total_predict_button.clicked.connect(self.on_total_predict_button_clicked)
                btn_layout.addWidget(self.total_predict_button)
                right_layout.addLayout(btn_layout)
                
                ds_path = os.path.join(os.getcwd(), "Data_storage_Lib.py")
                spec = importlib.util.spec_from_file_location("Data_storage_Lib", ds_path)
                ds_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(ds_module)
                self.graph_plot_info = getattr(ds_module, "graph_plot_info", {})
                self.predict_dict = getattr(ds_module, "predict_dict", {})
                self.prediction_index = 1
                self.is_total_predict = False
                self.best_prediction_key = None
                self.flash_timer = QTimer(self)
                self.flash_timer.timeout.connect(self.toggle_flash_color)
                self.flash_state = False
                if self.predict_dict:
                    self.show_prediction(self.prediction_index)
                else:
                    self.text_edit.setPlainText("No prediction data found in Data_storage_Lib.py.")
            
            def on_next_button_clicked(self):
                self.prediction_index += 1
                if self.prediction_index > len(self.predict_dict):
                    self.prediction_index = 1
                self.plot_widget.clear()
                self.flash_timer.stop()
                self.show_prediction(self.prediction_index)
            
            def on_total_predict_button_clicked(self):
                self.is_total_predict = True
                self.plot_widget.clear()
                self.text_edit.clear()
                self.plot_all_predictions()
                self.display_total_predict_info()
                self.plot_green_line()
                self.plot_widget.setInteractive(True)
            
            def show_prediction(self, i_info):
                self.plot_widget.clear()
                prediction_key = f'predict_{i_info}'
                real_line = self.predict_dict.get(prediction_key, [])
                if not real_line:
                    self.text_edit.setPlainText(f"No data for {prediction_key}")
                    return
                virtual_line = self.generate_virtual_line(real_line)
                yellow_virtual_line, yellow_date = self.generate_yellow_virtual_line(real_line)
                self.plot_data(real_line, virtual_line, yellow_virtual_line, prediction_key, yellow_date)
                self.update_message_display(prediction_key, yellow_date, real_line, virtual_line, yellow_virtual_line)
            
            def plot_data(self, real_line, virtual_line, yellow_virtual_line, prediction_key, yellow_date):
                x_real, y_real = zip(*real_line)
                self.plot_widget.plot(x_real, y_real, pen=pg.mkPen('b', width=2), symbol='o', symbolBrush='b')
                x_virtual, y_virtual = zip(*virtual_line)
                red_pen = pg.mkPen(color='r', width=2, style=Qt.PenStyle.DashLine)
                self.plot_widget.plot(x_virtual, y_virtual, pen=red_pen)
                x_yellow, y_yellow = zip(*yellow_virtual_line)
                yellow_pen = pg.mkPen(color='y', width=2, style=Qt.PenStyle.DashLine)
                self.plot_widget.plot(x_yellow, y_yellow, pen=yellow_pen)
                self.adjust_range(x_real, y_real)
            
            def adjust_range(self, x_data, y_data):
                if self.is_total_predict:
                    return
                y_min, y_max = min(y_data), max(y_data)
                y_buffer = 0.03 * (y_max - y_min)
                self.plot_widget.setYRange(y_min - y_buffer, y_max + y_buffer)
            
            def plot_green_line(self):
                all_y_values = []
                for key in self.predict_dict:
                    real_line = self.predict_dict.get(key, [])
                    if real_line:
                        _, y_real = zip(*real_line)
                        all_y_values.extend(y_real)
                if all_y_values:
                    highest_y_value = max(all_y_values)
                    self.plot_widget.plot([25, 25], [0, highest_y_value * 1.03],
                                          pen=pg.mkPen('g', width=2))
            
            def update_message_display(self, prediction_key, yellow_date, real_line, virtual_line, yellow_virtual_line):
                x_real, y_real = zip(*real_line)
                x_virtual, y_virtual = zip(*virtual_line)
                x_yellow, y_yellow = zip(*yellow_virtual_line)
                mse_real_vs_virtual = mean_squared_error(y_real, y_virtual)
                mse_real_vs_yellow = mean_squared_error(y_real, y_yellow)
                message = (
                    f"Graph Information:\n\n"
                    f"Prediction Key: {prediction_key}\n"
                    f"Closest Trend Date: {yellow_date}\n\n"
                    f"Explanation:\n"
                    f"- Blue line: Prediction ({prediction_key}).\n"
                    f"- Red dashed line: Virtual line (Linear Regression).\n"
                    f"- Yellow dashed line: Closest historical trend.\n\n"
                    f"AI Analysis:\n"
                    f"- MSE (Blue vs Red) = {mse_real_vs_virtual:.4f}\n"
                    f"- MSE (Blue vs Yellow) = {mse_real_vs_yellow:.4f}\n"
                    f"\nInterpretation:\n"
                    f"- Smaller MSE indicates a better model fit."
                )
                self.text_edit.setPlainText(message)
            
            def plot_all_predictions(self):
                self.best_prediction_key = None
                self.best_mse = float('inf')
                for i_info in range(1, len(self.predict_dict) + 1):
                    prediction_key = f'predict_{i_info}'
                    real_line = self.predict_dict.get(prediction_key, [])
                    if not real_line:
                        continue
                    virtual_line = self.generate_virtual_line(real_line)
                    yellow_virtual_line, yellow_date = self.generate_yellow_virtual_line(real_line)
                    self.plot_data(real_line, virtual_line, yellow_virtual_line, prediction_key, yellow_date)
                    x_real, y_real = zip(*real_line)
                    x_yellow, y_yellow = zip(*yellow_virtual_line)
                    mse_real_vs_yellow = mean_squared_error(y_real, y_yellow)
                    if mse_real_vs_yellow < self.best_mse:
                        self.best_mse = mse_real_vs_yellow
                        self.best_prediction_key = prediction_key
                if self.best_prediction_key:
                    self.flash_best_prediction(self.best_prediction_key)
            
            def display_total_predict_info(self):
                total_mse = []
                for i_info in range(1, len(self.predict_dict) + 1):
                    prediction_key = f'predict_{i_info}'
                    real_line = self.predict_dict.get(prediction_key, [])
                    if not real_line:
                        continue
                    virtual_line = self.generate_virtual_line(real_line)
                    yellow_virtual_line, yellow_date = self.generate_yellow_virtual_line(real_line)
                    x_real, y_real = zip(*real_line)
                    x_yellow, y_yellow = zip(*yellow_virtual_line)
                    mse_real_vs_yellow = mean_squared_error(y_real, y_yellow)
                    total_mse.append((prediction_key, mse_real_vs_yellow))
                if total_mse:
                    best_prediction = min(total_mse, key=lambda x: x[1])
                    message = (
                        f"Total Predictions Analysis:\n\n"
                        f"Most accurate prediction: {best_prediction[0]} with MSE = {best_prediction[1]:.4f}\n\n"
                        f"Based on MSE, the prediction with the smallest error is deemed most accurate."
                    )
                    self.text_edit.append(message)
            
            def flash_best_prediction(self, best_prediction_key):
                self.best_prediction_key = best_prediction_key
                self.flash_timer.start(500)
            
            def toggle_flash_color(self):
                color = 'b' if self.flash_state else 'c'
                real_line = self.predict_dict.get(self.best_prediction_key, [])
                if not real_line:
                    return
                virtual_line = self.generate_virtual_line(real_line)
                yellow_virtual_line, yellow_date = self.generate_yellow_virtual_line(real_line)
                self.plot_widget.clear()
                self.plot_data(real_line, virtual_line, yellow_virtual_line, self.best_prediction_key, yellow_date)
                self.plot_widget.plot([x for x, _ in real_line], [y for _, y in real_line],
                                      pen=pg.mkPen(color=color, width=2))
                self.flash_state = not self.flash_state
            
            def generate_virtual_line(self, real_line):
                x_real, y_real = zip(*real_line)
                import numpy as np
                x_real_arr = np.array(x_real).reshape(-1, 1)
                model = LinearRegression()
                model.fit(x_real_arr, y_real)
                y_virtual = model.predict(x_real_arr)
                return list(zip(x_real, y_virtual))
            
            def generate_yellow_virtual_line(self, real_line):
                X, y = [], []
                for date, trend in self.graph_plot_info.items():
                    if trend:
                        x_trend, y_trend = zip(*trend)
                        X.append(x_trend)
                        y.append(y_trend)
                if not X:
                    return real_line, "N/A"
                import numpy as np
                X = np.array(X)
                y = np.array(y)
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                x_real, _ = zip(*real_line)
                x_real_arr = np.array(x_real).reshape(1, -1)
                x_real_scaled = scaler.transform(x_real_arr)
                knn = KNeighborsRegressor(n_neighbors=1)
                knn.fit(X_scaled, y)
                yellow_virtual_y = knn.predict(x_real_scaled)
                yellow_virtual_line = list(zip(x_real, yellow_virtual_y.flatten()))
                yellow_date = list(self.graph_plot_info.keys())[0]
                return yellow_virtual_line, yellow_date

        widget = GraphAnalysisWidget()
        self.graph_layout.addWidget(widget)
        self.update_terminal("Main: Graph analysis tool activated.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settingsDialog = SettingsDialog()
    if settingsDialog.exec() == QDialog.Accepted:
        settings = settingsDialog.getSettings()
        font_name = settings["font_name"]
        font_size = settings["font_size"]
        text_color = settings["text_color"]
        gui = TerminalGUI(font_name, font_size, text_color)
        gui.show()
        gui.update_terminal("Welcome to the Terminal GUI!\nType 'help' for available commands.")
        sys.exit(app.exec())
    else:
        sys.exit(0)

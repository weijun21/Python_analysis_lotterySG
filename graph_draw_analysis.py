import os
import numpy as np
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QMessageBox, QSpinBox, QTextEdit, QDialog)
from PyQt6.QtCore import Qt
from docx import Document
from datetime import datetime

# New helper: enforce strictly increasing order for the main 6 numbers.
def enforce_strictly_increasing(nums):
    fixed = nums.copy()
    for i in range(1, len(fixed)):
        if fixed[i] <= fixed[i-1]:
            new_val = fixed[i-1] + 1
            if new_val > 49:
                new_val = fixed[i-1] - 1
                while new_val in fixed and new_val > 0:
                    new_val -= 1
                if new_val <= 0:
                    new_val = fixed[i-1]
            fixed[i] = new_val
    return fixed

# Helper: check if pattern is unlikely.
def is_unlikely_pattern(nums):
    sorted_nums = sorted(nums)
    if all(sorted_nums[i] + 1 == sorted_nums[i+1] for i in range(len(sorted_nums)-1)):
        return True
    if all(n % 2 == 0 for n in nums) or all(n % 2 == 1 for n in nums):
        return True
    if (max(nums) - min(nums)) < 15:
        return True
    return False

# Helper: occurrence scaling.
def occurrence_scale(percent):
    return 1.4 - 0.005 * percent

# New helper: compute chain length if candidate is added to chosen.
def chain_length_with(candidate, chosen):
    current = sorted(list(chosen) + [candidate])
    max_chain = 1
    current_chain = 1
    for i in range(1, len(current)):
        if current[i] == current[i-1] + 1:
            current_chain += 1
            max_chain = max(max_chain, current_chain)
        else:
            current_chain = 1
    return max_chain

class AIModelGraphAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cwd = os.getcwd()
        self.data_storage_file = os.path.join(self.cwd, "Data_storage_Lib.py")
        self.graph_plot_info = {}  # date -> list of (x,y) pairs
        self.table_data = {}       # table number -> list of date strings
        self.allowed_lists = {}    # allowed numbers for positions 1-7 (keys "C".."I")
        self.occurrence_pattern = [100.0, 20.0, 10.0, 0.0, 80.0, 90.0, 50.0]
        self.list_percentages = {}  # loaded from Data_storage_Lib.py
        self.prediction_result = ""
        self.load_data()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AI Graph Analyzer - Next Draw Prediction")
        self.setGeometry(100, 100, 800, 400)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        self.predict_button = QPushButton("Generate Candidate Predictions")
        self.predict_button.clicked.connect(self.run_candidate_predictions)
        layout.addWidget(self.predict_button)
        
        self.candidate_spin = QSpinBox()
        self.candidate_spin.setRange(1, 20)
        self.candidate_spin.setValue(3)
        self.candidate_spin.setSuffix(" candidates")
        layout.addWidget(self.candidate_spin)
        
        self.save_button = QPushButton("Save Prediction to Text File")
        self.save_button.clicked.connect(self.save_prediction)
        layout.addWidget(self.save_button)

    def load_data(self):
        if not os.path.exists(self.data_storage_file):
            QMessageBox.critical(self, "Error", f"{self.data_storage_file} not found!")
            return
        try:
            ns = {}
            with open(self.data_storage_file, "r", encoding="utf-8") as f:
                exec(f.read(), ns)
            if "graph_plot_info" not in ns:
                QMessageBox.critical(self, "Error", "graph_plot_info not found in Data_storage_Lib.py")
                return
            self.graph_plot_info = ns["graph_plot_info"]
            for key in ["C", "D", "E", "F", "G", "H", "I"]:
                self.allowed_lists[key] = ns.get(key, list(range(1, 50)))
            # Load list_percent1 to list_percent7; convert lists to dicts if necessary.
            for i in range(1, 8):
                key = f"list_percent{i}"
                value = ns.get(key, None)
                if value is None:
                    self.list_percentages[key] = {x: 0 for x in range(1, 50)}
                elif isinstance(value, list):
                    d = {}
                    for item in value:
                        try:
                            parts = item.split(":")
                            if len(parts) >= 2:
                                candidate_str = parts[0].strip()  # e.g., "Value 1"
                                candidate = int(candidate_str.replace("Value", "").strip())
                                perc_str = parts[1].strip().strip("()%")
                                percent = float(perc_str)
                                d[candidate] = percent
                        except Exception:
                            continue
                    self.list_percentages[key] = d
                elif isinstance(value, dict):
                    self.list_percentages[key] = value
                else:
                    self.list_percentages[key] = {x: 0 for x in range(1, 50)}
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading data: {e}")
        
        table_analysis_path = os.path.join(self.cwd, "table_analysis.docx")
        if not os.path.exists(table_analysis_path):
            QMessageBox.critical(self, "Error", f"{table_analysis_path} not found!")
            return
        try:
            from docx import Document
            doc = Document(table_analysis_path)
            self.table_data = {}
            for idx, table in enumerate(doc.tables):
                tname = str(idx+1)
                self.table_data[tname] = []
                for row in table.rows[1:]:
                    d = row.cells[0].text.strip()
                    if d in self.graph_plot_info:
                        self.table_data[tname].append(d)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error parsing table_analysis.docx: {e}")

    def run_candidate_predictions(self):
        num_candidates = self.candidate_spin.value()
        all_reports = ""
        for candidate_index in range(num_candidates):
            report = self.run_prediction(noise_seed=candidate_index)
            all_reports += f"Candidate {candidate_index+1}:\n" + report + "\n" + ("-"*40) + "\n"
        self.prediction_result = all_reports
        self.show_candidate_dialog(all_reports)

    def show_candidate_dialog(self, text):
        dialog = QDialog(self)
        dialog.setWindowTitle("Candidate Predictions")
        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(text)
        layout.addWidget(text_edit)
        dialog.resize(600, 400)
        dialog.exec()

    def run_prediction(self, noise_seed=0):
        all_dates = []
        for dates in self.table_data.values():
            all_dates.extend(dates)
        if len(all_dates) == 0:
            return "No historical draws available."
        all_dates_sorted = sorted(all_dates, key=lambda d: datetime.strptime(d[:10], "%Y-%m-%d"))
        history = [self.graph_plot_info[d] for d in all_dates_sorted 
                   if d in self.graph_plot_info and len(self.graph_plot_info[d]) == 7]
        if len(history) == 0:
            return "No valid draws found in history."
        
        # Deterministic bias: use pure averages with a small bias based on noise_seed.
        predicted_y = []
        for pos in range(7):
            ys = [draw[pos][1] for draw in history]
            avg_y = np.mean(ys)
            bias = (noise_seed * 0.02) * avg_y  # 2% per candidate index
            predicted_y.append(avg_y + bias)

        target_draw = history[-1]
        predicted_x = []
        already_chosen = set()
        allowed_keys = ["C", "D", "E", "F", "G", "H", "I"]
        for pos in range(7):
            allowed = self.allowed_lists.get(allowed_keys[pos], list(range(1,50)))
            allowed_candidates = [a for a in allowed if a not in already_chosen]
            
            percent_dict = self.list_percentages.get(f"list_percent{pos+1}", {})
            hist_vals = [draw[pos] for draw in history]
            candidate_avg = {}
            candidate_freq = {}
            for (x_val, y_val) in hist_vals:
                if x_val in allowed_candidates:
                    candidate_avg.setdefault(x_val, []).append(y_val)
                    candidate_freq[x_val] = candidate_freq.get(x_val, 0) + 1
            for x_val in candidate_avg:
                candidate_avg[x_val] = np.mean(candidate_avg[x_val])
            
            candidate_items = []
            target_value = target_draw[pos][0]
            for x_val, avg in candidate_avg.items():
                # NEW: Skip candidate if adding it to already_chosen creates a chain of 3+ consecutive numbers.
                if chain_length_with(x_val, already_chosen) >= 3:
                    continue
                freq = candidate_freq.get(x_val, 0)
                penalty = 0
                if x_val == target_value and freq < 2:
                    penalty += 1000
                candidate_percentage = percent_dict.get(x_val, 0)
                if candidate_percentage == 0:
                    penalty += 1000
                candidate_items.append((x_val, penalty, abs(avg - predicted_y[pos]), candidate_percentage))
            if candidate_items:
                sorted_candidates = sorted(candidate_items, key=lambda kv: (kv[1], kv[2], kv[3]))
                candidate = sorted_candidates[0][0]
            else:
                if allowed_candidates:
                    candidate = min(allowed_candidates)
                else:
                    candidate = min(allowed)
            while candidate in already_chosen:
                candidate = candidate + 1 if candidate < 49 else candidate - 1
            predicted_x.append(candidate)
            already_chosen.add(candidate)

        # Enforce strictly increasing order for main positions (positions 1-6).
        main_x = enforce_strictly_increasing(predicted_x[:6])
        final_x = main_x + [predicted_x[6]]
        # Final check: ensure candidate for point 7 is not a duplicate.
        if final_x[6] in main_x:
            # Choose the smallest number from 1..49 not in main_x.
            for candidate in range(1, 50):
                if candidate not in main_x:
                    final_x[6] = candidate
                    break
        
        adjusted_y = [predicted_y[i] * occurrence_scale(self.occurrence_pattern[i]) for i in range(7)]
        final_pattern = list(zip(final_x, adjusted_y))
        main_numbers = [pt[0] for pt in final_pattern[:6]]
        if is_unlikely_pattern(main_numbers):
            final_pattern[2] = (min(final_pattern[2][0] + 1, 49), final_pattern[2][1])
        final_pattern = [(max(1, min(x,49)), y) for (x,y) in final_pattern]
        
        report = ""
        for i, (x, y) in enumerate(final_pattern, start=1):
            report += f"  Point {i}: x = {x}, predicted y = {y:.2f}\n"
        report += "\nRules enforced:\n"
        report += "  - Strictly unique X values enforced (no duplicates across any points)\n"
        report += "  - Avoid candidate equal to target's x if frequency < 2\n"
        report += "  - Candidates that produce a chain of 3+ consecutive numbers are skipped\n"
        report += "  - Main numbers (positions 1-6) forced to be strictly increasing\n"
        report += "  - Occurrence adjustment applied\n"
        report += "  - Selection prioritized based on list_percent1 to list_percent7 (0% gets heavy penalty)\n"
        report += "  - Unlikely patterns adjusted\n"
        return report

    def save_prediction(self):
        if not self.prediction_result:
            QMessageBox.information(self, "Save Prediction", "No prediction result to save.")
            return
        file_path = os.path.join(self.cwd, "next_graph.txt")
        try:
            with open(file_path, "w") as f:
                f.write(self.prediction_result)
            QMessageBox.information(self, "Save Prediction", f"Prediction saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Prediction", f"Failed to save prediction:\n{e}")

    def run(self):
        self.show()

# New helper: enforce strictly increasing order for main positions.
def enforce_strictly_increasing(nums):
    fixed = nums.copy()
    for i in range(1, len(fixed)):
        if fixed[i] <= fixed[i-1]:
            new_val = fixed[i-1] + 1
            if new_val > 49:
                new_val = fixed[i-1] - 1
                while new_val in fixed and new_val > 0:
                    new_val -= 1
                if new_val <= 0:
                    new_val = fixed[i-1]
            fixed[i] = new_val
    return fixed

if __name__ == "__main__":
    app = QApplication([])
    window = AIModelGraphAnalyzer()
    window.show()
    app.exec()

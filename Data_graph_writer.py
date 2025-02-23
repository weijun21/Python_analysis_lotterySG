import os
import re
from docx import Document

class TableAnalysisExtractor:
    def __init__(self):
        """
        Initialize with paths from the current working directory (cwd).
        """
        self.cwd = os.getcwd()
        self.input_filename = os.path.join(self.cwd, "table_analysis.docx")
        self.output_file = os.path.join(self.cwd, "Data_storage_Lib.py")

    def clean_row_name(self, row_name):
        """
        Cleans row names by removing '00:00:00' from date values.
        """
        return row_name.split()[0] if " " in row_name else row_name

    def extract_table_data(self):
        """
        Extracts data from table_analysis.docx, ensuring all rows and correct percentages are processed.
        Uses the first column as the row identifier (e.g., date).
        """
        if not os.path.exists(self.input_filename):
            print(f"Error: {self.input_filename} not found!")
            return {}

        doc = Document(self.input_filename)
        graph_plot_info = {}  # Dictionary to store extracted data
        total_rows_extracted = 0

        for table_idx, table in enumerate(doc.tables):
            for i, row in enumerate(table.rows[1:], start=1):  # Skip header row
                row_data, row_numbers = [], []

                # Extract row name from the first column (e.g., Date or Category)
                raw_row_name = row.cells[0].text.strip() if row.cells else f"Row_{i}"
                row_name = self.clean_row_name(raw_row_name)

                for j, cell in enumerate(row.cells[1:], start=1):  # Skip first column
                    text = cell.text.strip()
                    matches = re.findall(r"(\d+)\s*\(\s*([\d.]+)%", text)

                    if matches:
                        for value_part, percentage_part in matches:
                            if value_part.isdigit():
                                num_value = int(value_part)
                                percent_value = float(percentage_part)
                                row_numbers.append(num_value)
                                row_data.append(percent_value)

                if row_data and row_numbers:
                    filtered_xy = [(x, y) for x, y in zip(row_numbers, row_data) if y is not None]
                    graph_plot_info[row_name] = filtered_xy[:7]  # Store first 7 points
                    total_rows_extracted += 1

        print(f"✅ Extracted {total_rows_extracted} rows from `table_analysis.docx`")
        return graph_plot_info

    def update_data_storage_file(self, graph_plot_info):
        """
        Completely overwrites the `graph_plot_info` section in `Data_storage_Lib.py`
        while preserving all other contents.
        """
        if not os.path.exists(self.output_file):
            print(f"Error: {self.output_file} not found!")
            return

        with open(self.output_file, "r", encoding="utf-8") as f:
            existing_data = f.readlines()

        updated_data = []
        inside_graph_section = False

        for line in existing_data:
            # Detect start of graph_plot_info section
            if line.strip().startswith("graph_plot_info"):
                inside_graph_section = True
                continue  # Skip existing data

            # Detect end of graph_plot_info section
            if inside_graph_section and (line.strip() == "" or not line.strip().startswith("graph_plot_info")):
                inside_graph_section = False  # Stop skipping
                updated_data.append("\n")  # Ensure spacing before writing new section

            if not inside_graph_section:
                updated_data.append(line)

        # Append new auto-generated graph data
        updated_data.append("# Auto-generated Plot Data - DO NOT MODIFY MANUALLY\n")
        updated_data.append("graph_plot_info = {}\n")  # Reset dictionary

        for key, value in graph_plot_info.items():
            updated_data.append(f"graph_plot_info[{repr(key)}] = {value}\n")

        # Save back to file
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.writelines(updated_data)

        print(f"✅ Successfully overwrote `graph_plot_info` in {self.output_file}!")

    def run(self):
        """Runs the full extraction and update process."""
        graph_plot_info = self.extract_table_data()
        self.update_data_storage_file(graph_plot_info)




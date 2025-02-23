# Python_analysis_lotterySG






## Description
This project is built on python 3.10, recommended this for best performance
This repository is a personal project for learning and developing analytical techniques to study the Toto SG lottery in Singapore. The primary objective is to gain deeper insights into lottery patterns, understand combination probabilities, and explore trends that may enhance predictive accuracy. The project leverages various data analysis methods, including statistical modeling and machine learning approaches, to identify meaningful patterns in past draw results.

One of the advanced features incorporated into this project is the ability to visualize lottery trends through graphical representation. By transforming numerical data into interactive visual formats, users can better understand the distribution of winning numbers, frequency of occurrences, and potential correlations between different numbers. While this project is intended for learning and exploration, it is important to note that all predictions and analysis outcomes are based on historical data and do not guarantee the accuracy or financial gains.

## Project Features

This project is structured into three distinct phases, each focusing on a crucial aspect of the analysis process. By systematically breaking down the workflow, users can better understand how the data is processed, analyzed, and interpreted. Below is a detailed breakdown of each section:

1. **Data Preparation**:

   - The first stage involves collecting lottery data from a reliable external source: [Lottolyzer](https://en.lottolyzer.com/history/singapore/toto/page/1/per-page/50/summary-view).
   - The data is then formatted and cleaned to ensure consistency and remove anomalies or missing values.
   - This step is crucial for establishing a solid foundation for meaningful analysis.
   - Please take note to make sure your network is on when first time running this program to obtain data from external website

2. **Data Sorting and Analysis**:

   - Once the data is cleaned, it is sorted and categorized based on various parameters such as frequency, occurrence rate, and historical trends.
   - The project utilizes **sci-kit-learn Lib**, a popular machine-learning library, to conduct statistical analysis and recognize potential patterns.
   - Different algorithms and models are tested to determine the most effective approach for predicting likely outcomes based on historical trends.

3. **Trend Prediction**:

   There are two primary methods employed in this phase:

   1. **Combination Method** – This approach uses recognized patterns in historical data to identify potential draws with higher probability. By examining recurring patterns, frequencies, and intervals among past winning numbers, it attempts to forecast the most likely outcomes.
   2. **Visualization Techniques - Trend Lines Method** – This advanced approach utilizes sci-kit-learn to detect similarities between newly produced results and historical data. By plotting regression lines, using classification models, generating heatmaps, and employing other visualization strategies, it provides a valuable reference for users seeking to uncover correlations between new patterns and historical draws.



## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

1. Clone the repository and navigate to the project directory:

   ```sh
   git clone https://github.com/weijun21/Python_analysis_lotterySG.git && cd Python_analysis_lotterySG
   ```

## Usage

To use the file, run the following command:

```sh
run_terminal_gui.bat
```

## Example GUI Output

Below is a screenshot of the project's Terminal GUI alongside a dynamic line chart. It demonstrates how the tool displays final combinations, applied trends, and statistical analyses in real time:
![image](https://github.com/user-attachments/assets/28339981-7071-4772-aeb0-7cccdb7952c0)



This interface allows you to:

- **Review Analysis Results**: Displays the final predicted combinations along with the most frequent trends and historical patterns.
- **Visualize Trends**: Plots real vs. virtual (linear regression) lines, indicating how the current predictions compare to identified historical trends.
- **Monitor Machine Learning Metrics**: Provides MSE (Mean Squared Error) values, which measure how closely your predictions align with actual or historical data.

**Key Elements**:

- **Blue Line (Prediction)**: Shows the `predict_1` or `predict_2` forecast.
- **Red Dashed Line (Virtual / Linear Regression)**: Represents a model-based regression line for comparison.
- **Yellow Dashed Line (Closest Historical Trend)**: Highlights a closely matched trend from past data.

  .

```sh
run_terminal_gui.bat
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch`
3. Commit your changes: `git commit -m "Add new feature"`
4. Push to the branch: `git push origin feature-branch`
5. Open a Pull Request.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

## Contact

Maintainer: weijun21\
Email: [lolkk33@outlook.com](mailto\:lolkk33@outlook.com)


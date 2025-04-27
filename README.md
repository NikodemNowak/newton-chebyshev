# Newton-Chebyshev Interpolation

This project provides an interactive web-based tool for polynomial interpolation. Using Newton's method with divided differences and Chebyshev nodes, the application enables users to visualize interpolation results using built-in mathematical functions or custom datasets.

## Features

- Polynomial interpolation using Newton's method.
- Support for Chebyshev nodes, which reduce interpolation errors.
- Interactive visualizations:
  - Original function (if selected).
  - Interpolated polynomial.
  - Data points (Chebyshev nodes or custom input).
- Ability to upload datasets in CSV or TXT format for custom interpolation.

---

## Requirements

To run the application, you will need the following software and packages installed:

- Python (version 3.8 or higher)
- Libraries:
  - `streamlit`
  - `numpy`
  - `matplotlib`
  - `pandas`

---

## Usage

1. **Launch the Application: Run the following command in your terminal:**
   ```bash
   python -m streamlit run interpolation_app.py

2. **Open in Browser:**
   After running the above command, Streamlit will provide a URL (e.g., http://localhost:8501). Open it in your browser.

3. **Using the Application:**
   - Choose a data source:
     - **Predefined Functions:** Select a mathematical function, input the range, and set the degree of the interpolating polynomial.
     - **Custom Dataset:** Upload a file (CSV or TXT) with x and y values in two columns.
   - View the results:
     - Visualize the interpolating polynomial.
     - Compare it with the original function (if applicable).
     - Analyze the data points.
    
---

## Example Dataset Format

For custom datasets, upload a file formatted as follows (no headers):
  ```bash
  x1 y1
  x2 y2
  x3 y3
  ...
  ```

---

## Notes

- Ensure the uploaded file contains two numeric columns (x and y) separated by spaces, commas, or tabs.
- Chebyshev nodes are automatically generated for predefined functions to improve accuracy.
- The application dynamically adjusts the y-axis range based on the data.

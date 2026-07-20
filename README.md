# 🛢️ Oil Well Production Dashboard

A Python-based data analysis and visualization project that analyzes oil well production data from the Volve Field dataset using **Pandas** and **Matplotlib**.

This project demonstrates how production data can be cleaned, analyzed, summarized, and visualized to provide useful insights into oil field performance.

---

## Features

* Load production data from Excel
* Clean and preprocess production data
* Calculate:

  * Total Oil Produced
  * Total Gas Produced
  * Total Water Produced
* Identify the Top 5 Oil Producing Wells
* Generate monthly production trends for:

  * Oil
  * Gas
  * Water
* Generate professional charts automatically
* Display a production summary report in the terminal

---

## Technologies Used

* Python
* Pandas
* Matplotlib
* Git
* GitHub

---

## Project Structure

```text
oil-well-production-dashboard/
│
├── charts/
│   ├── monthly_oil_trend.png
│   └── top_5_oil_producing_wells.png
│
├── data/
│   └── Volve production data.xlsx
│
├── src/
│   ├── analysis.py
│   ├── loader.py
│   ├── main.py
│   ├── report.py
│   └── visualization.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Sample Output

### Production Summary

* Total Oil Produced
* Total Gas Produced
* Total Water Produced
* Top 5 Producing Wells

### Visualizations

* Top 5 Oil Producing Wells
* Monthly Oil Production Trend
* Monthly Gas Production Trend
* Monthly Water Production Trend

---

## How to Run

Clone the repository:

```bash
git clone https://github.com/Abdulhhakeem/oil-well-production-dashboard.git
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the project:

```bash
python src/main.py
```

---

## Future Improvements

* Interactive dashboard using Plotly
* Streamlit web application
* Yearly production analysis
* Water cut analysis
* Export reports to Excel and PDF
* Interactive filtering by well

---

## Author

**Abdul Hakeem**

Geology graduate passionate about Python, data analysis, and oil & gas technology.

Currently building projects that combine geology with data analytics and software development.

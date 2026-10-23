<div align="center">

# 🛒 E-commerce Sales Analyzer

### Apne sales data ko insights me badlo — sirf ek command se.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c)
![Seaborn](https://img.shields.io/badge/Seaborn-4c72b0)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 📌 Ye project kya karta hai?

**E-commerce Sales Analyzer** ek Python tool hai jo kisi bhi online store ke order data ko padh kar
poora business analysis karta hai aur sundar charts + ready-to-read report bana deta hai.

Is project me ye sab analyze hota hai:

| # | Analysis | Aapko kya pata chalega |
|---|----------|------------------------|
| 1 | 💰 **Sales & Profit** | Total revenue, profit, margin, average order value |
| 2 | 🏆 **Best-selling products** | Kaun sa product sabse zyada bikta hai aur kaun sabse zyada profit deta hai |
| 3 | 📈 **Monthly revenue** | Kaun se mahine me sale peak par thi, growth trend kaisa hai |
| 4 | 👥 **Customer spending** | Top customers kaun hain, Bronze → Platinum segments |
| 5 | 🗺️ **Regional performance** | Kaun sa region sabse strong hai, region × month heatmap |

---

## 📊 Output ki jhalak

<table>
  <tr>
    <td><img src="assets/01_monthly_revenue.png" alt="Monthly Revenue"></td>
    <td><img src="assets/02_top_products.png" alt="Top Products"></td>
  </tr>
  <tr>
    <td align="center"><b>Monthly Revenue vs Profit</b></td>
    <td align="center"><b>Top Products</b></td>
  </tr>
  <tr>
    <td><img src="assets/03_category_performance.png" alt="Category Performance"></td>
    <td><img src="assets/04_customer_spending.png" alt="Customer Spending"></td>
  </tr>
  <tr>
    <td align="center"><b>Category Performance</b></td>
    <td align="center"><b>Customer Spending & Segments</b></td>
  </tr>
</table>

<p align="center">
  <img src="assets/05_regional_performance.png" alt="Regional Performance" width="90%">
  <br><b>Regional Performance + Region × Month Heatmap</b>
</p>

---

## ✨ Features

- 🧹 **Auto data cleaning** — duplicate orders, missing values aur galat quantity/price hata deta hai
- 🎲 **Built-in sample data generator** — CSV na ho tab bhi turant demo chalao (festive-season spike ke saath!)
- 📉 **6 professional charts** — Matplotlib + Seaborn se, high-resolution PNG
- 🇮🇳 **Indian-style axis** — amounts Lakh (L) / Crore (Cr) me dikhte hain
- 🧾 **Text report** — key insights ek hi file me (`sales_report.txt`)
- 📁 **CSV exports** — product, monthly, customer aur region ke tables Excel me kholne ke liye
- ⚙️ **Command-line options** — apni CSV, output folder, rows aur seed customize karo

---

## 🚀 Quick Start

### 1. Repository clone karo

```bash
git clone https://github.com/<your-username>/ecommerce-sales-analyzer.git
cd ecommerce-sales-analyzer
```

### 2. Libraries install karo

```bash
pip install -r requirements.txt
```

### 3. Run karo

```bash
# Sample data ke saath demo
python ecommerce_sales_analyzer.py

# Apni CSV file ke saath
python ecommerce_sales_analyzer.py --data my_sales.csv

# Zyada rows aur alag output folder
python ecommerce_sales_analyzer.py --rows 20000 --seed 7 --output results
```

Run hone ke baad sab kuch `output/` folder me mil jayega. ✅

---

## 🧾 Apna data kaise use karein?

Aapki CSV me ye **10 columns** hone chahiye:

| Column | Description | Example |
|--------|-------------|---------|
| `order_id` | Unique order ID | `ORD100001` |
| `order_date` | Order ki date | `2025-11-14` |
| `customer_id` | Customer ID | `C0042` |
| `product` | Product ka naam | `Wireless Earbuds` |
| `category` | Product category | `Electronics` |
| `region` | Region / zone | `South` |
| `quantity` | Kitni units | `2` |
| `unit_price` | Ek unit ki selling price (Rs) | `2499` |
| `cost_price` | Ek unit ki cost (Rs) | `1500` |
| `discount` | Discount (0 se 1 ke beech) | `0.10` |

> 💡 **Tip:** `discount` ko fraction me likho — 10% discount ke liye `0.10`.

**Formulas jo use hue hain:**

```text
Revenue = quantity × unit_price × (1 − discount)
Cost    = quantity × cost_price
Profit  = Revenue − Cost
Margin  = Profit ÷ Revenue × 100
```

---

## 📂 Project Structure

```text
ecommerce-sales-analyzer/
│
├── ecommerce_sales_analyzer.py   # Main script (data → analysis → charts → report)
├── requirements.txt              # Python dependencies
├── README.md                     # Ye file
├── assets/                       # README ke screenshots
└── output/                       # Run karne par ban jata hai
    ├── 01_monthly_revenue.png
    ├── 02_top_products.png
    ├── 03_category_performance.png
    ├── 04_customer_spending.png
    ├── 05_regional_performance.png
    ├── 06_correlation.png
    ├── sales_report.txt
    ├── product_performance.csv
    ├── monthly_trend.csv
    ├── customer_spending.csv
    ├── regional_performance.csv
    └── sample_sales_data.csv
```

---

## 🧠 Code kaise kaam karta hai?

```text
 CSV / Sample data
        │
        ▼
  prepare_data()  ──►  clean + revenue, cost, profit columns
        │
        ▼
  Analysis functions
   ├─ product_performance()
   ├─ category_performance()
   ├─ monthly_trend()
   ├─ customer_spending()   (quartile-based segments)
   └─ regional_performance()
        │
        ▼
  plot_*() functions  ──►  PNG charts
        │
        ▼
  build_text_report() ──►  sales_report.txt + CSV exports
```

Har function ek kaam karta hai, isliye aap kisi bhi hisse ko alag se import karke apne project me use kar sakte ho:

```python
from ecommerce_sales_analyzer import prepare_data, regional_performance
import pandas as pd

df = prepare_data(pd.read_csv("my_sales.csv"))
print(regional_performance(df))
```

---

## 📝 Sample Report

```text
-- OVERVIEW --
Total Orders        : 8,000
Total Revenue       : Rs 25,079,639
Total Profit        : Rs 9,364,992
Profit Margin %     : 37.3%

-- KEY INSIGHTS --
* Best seller (units)  : Notebook Pack (2,392 units)
* Most profitable      : Running Shoes
* Peak month           : November 2025
* Top region           : South (28.3% of revenue)
* Top 5% customers     : 23.2% of total revenue
```

> ⚠️ Ye numbers **randomly generated sample data** se aaye hain, kisi real business ke nahi.

---

## 🛠️ Tech Stack

| Library | Kaam |
|---------|------|
| **NumPy** | Random data generation, fast calculations |
| **Pandas** | Data cleaning, groupby, pivot tables |
| **Matplotlib** | Charts ka base, formatting |
| **Seaborn** | Beautiful bar plots, histograms, heatmaps |

---

## 🔮 Future Ideas

- [ ] RFM analysis (Recency, Frequency, Monetary)
- [ ] Sales forecasting (next 3 months)
- [ ] Interactive dashboard (Streamlit / Plotly)
- [ ] Return & cancellation analysis
- [ ] Excel report export

Contributions welcome hain! 🙌

---

## 🤝 Contributing

1. Repo ko **Fork** karo
2. Naya branch banao: `git checkout -b feature/amazing-idea`
3. Changes commit karo: `git commit -m "Add amazing idea"`
4. Push karo: `git push origin feature/amazing-idea`
5. **Pull Request** open karo

---

## 📄 License

Ye project **MIT License** ke under hai — free use, modify aur share karo.

---

<div align="center">

⭐ **Agar project pasand aaya to repo ko star zaroor karein!** ⭐

Made with ❤️ using Python

</div>

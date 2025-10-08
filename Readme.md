### Dynamic Pricing Allocator

### Overview

Dynamic Pricing Allocator is a data-driven system designed to automate and optimize product pricing decisions based on competitor data, pricing trends, and business constraints.
It integrates data extraction, analysis, and pricing logic to recommend competitive prices in real time — helping e-commerce or retail businesses maintain market competitiveness while ensuring profit margins.

This project consists of two key components:

1. Competitor Pricing Extractor – Collects and structures competitor price data.
2. Pricing Engine – Applies rule-based and data-driven logic to generate optimal product prices.

 ### Features

* 🔍 Competitor Data Extraction – Reads structured price offers from CSV or web sources.
* ⚙️ Dynamic Pricing Logic – Implements logic for pricing within target margins or top-N competitors.
* 📊 Data Cleaning & Analysis – Handles missing data, outliers, and ensures consistent price comparisons.
* 📈 Visualization Ready – Outputs clean, ready-to-plot data for dashboards or analytics.
* 🧮 Customizable Pricing Strategy – Supports rule-based strategies such as:

  * Match lowest competitor price
  * Stay within top 3 competitors
  * Maintain minimum margin floor


 ### Dataset Description (`SKU123_offers.csv`)

This dataset represents competitor price offers for a specific SKU (product).
It includes data points like:

* source – Competitor platform (e.g., Amazon, Flipkart)
* comparable_price – Observed market price
* timestamp – Date/time of price observation
* (Optional) Additional fields for analysis such as brand, seller, or discount indicators


 ### Workflow

1. Data Extraction (`competitor_pricing_extractor.ipynb`)

   * Reads the dataset (`SKU123_offers.csv`)
   * Cleans and structures data
   * Outputs comparable competitor prices

2. Dynamic Pricing Computation (`pricing_engine_starter.ipynb`)

   * Reads processed competitor data
   * Applies strategy logic (e.g., `within_top3`, `margin_floor`)
   * Computes final recommended price
   * Exports results with justification notes


### Installation & Setup

 ### Requirements

* Python ≥ 3.9
* Jupyter Notebook
* Required Libraries:

     bash
  pip install pandas numpy requests
  


 ### To Run

1. Clone the repository:

      bash
   git clone https://github.com/<your-username>/dynamic-pricing-allocator.git
   cd dynamic-pricing-allocator
   
2. Launch Jupyter Notebook:

      bash
   jupyter notebook
   
3. Open and run:

   * competitor_pricing_extractor.ipynb
   * pricing_engine_starter.ipynb


 ### Example Output

After execution, the pricing engine outputs a JSON-like or DataFrame result:

json
{
  "recommended_price": 114.0,
  "margin_floor": 105.8,
  "P_lowest": 112.0,
  "P_top3": 115.0,
  "strategy": "within_top3",
  "notes": ["Selected price within top 3 competitor range"]
}


 ### Future Enhancements

* Integrate live web scraping for real-time competitor data.
* Add reinforcement learning or regression-based dynamic pricing models.
* Build a dashboard for visual monitoring of price trends.
* Include price elasticity and demand forecasting components.

 ### Author

**Pruthvi Shivade**
M.Tech | Thermal Engineering | Application Engineer (CFD) | MBA (Finance & Analytics)
📫 *Contact:* [Your Email or LinkedIn Profile]


🏷️ License

This project is for academic and learning purposes only.
All data used is for demonstration; no commercial use intended.



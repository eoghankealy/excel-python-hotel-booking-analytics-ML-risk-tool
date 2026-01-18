## Data Cleaning, Feature Engineering & Dashboard Preparation

### Data Cleaning Workflow
- Converted the dataset into an Excel table and standardized column formats.  
- Reservation dates were reformatted to `YYYY-MM-DD`.

- **Removal of incomplete stay records**  
  715 rows contained no valid stay or revenue information (`stays_in_week_nights = 0`, `stays_in_weekend_nights = 0`, and `adr = 0`).  
  - 35 of these were legitimate cancellations and were retained.  
  - The remaining 680 rows (~0.6% of data) lacked usable stay information and were removed to avoid distortions in revenue metrics.

- **Missing values**
  - `children = NA` → replaced with **0** (4 rows).
  - `country = NULL` → replaced with **“Unknown”** (488 rows).
  - `agent / company = NULL` → replaced with **“No Agent” / “No Company”** to maintain slicer consistency.

- **Zero-ADR records**
  - 1,066 “Check-Out” rows had ADR = 0.
  - 574 belonged to the **Complementary** segment (valid staff/promotional stays) and were retained.
  - The remaining 492 rows with unexplained zero revenue were removed.

- **Outliers & invalid values**
  - One negative ADR value was removed.
  - ADR validity ranges were defined using ±2σ per hotel:
    - City Hotel → €20–€191  
    - Resort Hotel → €25–€218  
  - Operational threshold applied: bookings below **€35 ADR** (and not complementary) were excluded as implausible.  
  - Complimentary stays were standardized to **ADR = 0**.
  - Two records with undefined `distribution_channel` were removed.

After cleaning, **115,958 rows remained** (from 119,391) — ~3% reduction, focused on removing records that lacked analytical value or introduced bias.

---

### Feature Engineering
The following derived fields were added to support analysis and modeling:

- `arrival_date` — combined existing date components  
- `total_nights = stays_in_week_nights + stays_in_weekend_nights`  
- `total_revenue = adr * total_nights`  
- `total_guests = adults + children + babies`  
- `revenue_per_guest = total_revenue / total_guests`  
- `is_family = Yes if children > 0 or babies > 0`  
- `season` — month-based seasonal mapping  
  (`Winter / Spring / Summer / Autumn`)

These fields were used across dashboards, KPIs, and model feature exploration.

---

### Dashboard Preparation & Analytical Decisions
- All dashboards **exclude cancelled reservations**, except where cancellations are explicitly analyzed.
- KPI comparison arrows were added to highlight which hotel performs better per metric.
- For “Top Countries by Spend per Guest”, countries with **fewer than 200 guests** were excluded to avoid rankings dominated by very small sample sizes.
- A calculated field was created for:
  - `revenue_per_guest_per_stay = total_revenue_per_stay / total_guests`
- Helper columns ensured countries were only included when guest-count thresholds were met and cancellations excluded.

- Two extreme outliers were removed from the **Resort scatter plot** to maintain chart readability.

- Revenue growth analysis compared:
  - **Aug 2015–Jul 2016 vs. Aug 2016–Jul 2017**
  - This avoided distortion caused by unusually weak City Hotel performance in early 2015, which likely reflected operational or external factors rather than true demand.

- Dashboard navigation was enhanced using **hyperlinked tab-style buttons** and conditional formatting to show the active page.

- To avoid empty month rows in charts (due to incomplete years), blank-row handling logic was added using:
  - `=IF(A5="", "", A5)`

---

### Forecasting & Scenario Tools
- Built an **interactive cancellation-rate scenario dashboard** using pivot tables, slicers, and logic to simulate revenue outcomes for each hotel.
- A slider control (Developer tools) allows users to adjust cancellation rates dynamically; results feed across linked visuals.
- A 12-month **seasonality-aware revenue forecast** was created using:
  - `FORECAST.ETS(..., seasonality = 12)`  
  to prevent winter months from being over-estimated due to partial-year effects.

---

### Summary
Overall, the cleaning and transformation choices prioritize:
- Analytical reliability over raw dataset completeness
- Removal of structurally invalid stays and implausible ADR values
- Consistency across dashboards, calculations, and modeling inputs
- Transparency in how exclusions and thresholds were determined

---
      
While the dashboards and analytical models provide meaningful operational insight, it is important to recognise the scope and constraints of the Cancellation Risk Tool. The following section outlines key modelling assumptions and limitations to ensure the results are interpreted appropriately.

---

# Cancellation Risk Model — Evolution & Rationale

This project documents the progression from a rule-based heuristic model built entirely in Excel to a statistically optimized logistic regression model trained in Python and operationalized in Excel.

## 1️⃣ Initial Approach: Heuristic Scorecard Model (Excel)

To remain fully within Excel initially, I designed a heuristic cancellation risk scorecard, assigning weighted points to predictors based on exploratory analysis and business intuition.

Key features included:

* Lead time (engineered using bins informed by weighted cancellation-rate analysis)
* Previous cancellations
* Deposit type
* Repeat guest indicator
* Number of booking changes
* Market segment (scaled to prevent dominance of a single variable)

This model produced a monotonic increase in cancellation rates across score bands and was evaluated using confusion matrices, ROC curves, and threshold testing implemented directly in Excel.

Limitations identified:

* Recall of approximately 41%, indicating many missed cancellations
* Low precision, resulting in a high false-positive rate
* ROC performance close to random (AUC ≈ 0.50)

These results indicated that while the model had structure, it lacked statistical optimization.

## 2️⃣ Transition to Logistic Regression (Excel → Python)

To improve predictive performance, I implemented a logistic regression model. Due to numerical instability and Solver limitations in Excel (overflow and convergence issues), model estimation was transitioned to Python.

Additional variables and feature engineering introduced in the final model:

* Standardised ADR (z-score) to ensure numerical stability and comparability across predictors
* Nationality binary indicator, coded as:
   * `1` = Portuguese guests
   * `0` = all other nationalities This was included to capture domestic vs international booking behavior
* Market segment dummy variables, created to represent categorical booking channels
   * Direct bookings were used as the reference category, as one category must be excluded to avoid multicollinearity (dummy variable trap)

Continuous variables (Lead Time, ADR) were standardized prior to modeling, and categorical variables were converted to binary indicators to enable proper coefficient estimation.

### 🔍 Key Insight: Lead Time Reinterpreted

A major analytical insight emerged when comparing the heuristic and regression models:

* Heuristic (bivariate) analysis suggested longer lead times increased cancellation risk.
* Multivariate logistic regression revealed a negative coefficient for lead time once deposit type and booking channel were controlled for.

This demonstrated that lead time was acting as a proxy variable for more influential predictors (particularly deposit policy). Once these factors were accounted for, longer lead times slightly reduced cancellation risk — highlighting the difference between correlation and causation.

## 3️⃣ Threshold Optimization & Model Selection

Multiple probability thresholds were tested on out-of-sample (2017) data. A cutoff of 0.30 was selected based on operational cost trade-offs:

* Recall: ~63% (significant reduction in missed cancellations)
* Precision: ~51% (manageable false-positive rate)
* False negatives reduced by ~37% relative to the heuristic model
* AUC ≈ 0.78, indicating strong discriminative power

This threshold reflects revenue-management priorities, where missed cancellations are more costly than additional follow-up on high-risk bookings.

## 4️⃣ Final Outcome & Deployment

* The logistic regression model fully replaces the heuristic scorecard
* Python is used for model training, validation, and coefficient estimation
* Excel is used for deployment, allowing non-technical users to:
   * Input new bookings
   * Automatically calculate cancellation probabilities
   * Flag high-risk reservations using the optimized 0.30 threshold

This workflow mirrors real-world analytics practice: statistical modeling in Python, operational decision-making in Excel.

## Model Assumptions & Limitations

This cancellation-risk tool was developed as an analytical and learning project using historical hotel reservation data. While it provides actionable insight and demonstrates the value of data-driven decision-making, the model operates under several assumptions and limitations that should be considered before relying on it in a real-world operational setting.

### **Data Scope & Generalizability**

- The model was trained using data from one Portuguese resort hotel (identity anonymized in source dataset named as **Resort Hotel** ) and over a **limited time period (July 2015 – Aug 2017)**. As a result, patterns learned by the model may not fully generalize to:
  - Other hotels
  - Different markets or guest segments
  - Future time periods with changing conditions

- Customer behavior, pricing strategies, and channel mix may evolve over time (**feature drift**), meaning the model should be **re-trained and monitored periodically**.

- **No macro-context variables:**  
  External drivers such as weather events, flight disruption, economic shocks, or local event calendars are not included in the dataset, even though they can significantly influence cancellation behavior.

- **Data context limitation example — City Hotel dataset:**  
  In the City Hotel data, the summer period of 2015 shows unusually low revenue (€364,765 vs. €2,185,199 in Summer 2016) and an extremely high cancellation rate of 57% (compared with 39% in Summer 2016, which is closer to the overall average of 42%).  
  These large discrepancies strongly suggest external or operational explanations (e.g., newly opened property, refurbishment period, supply constraints, or travel disruption). Because the dataset does not provide contextual information to explain these anomalies, the **City Hotel data was excluded from the Cancellation Risk Tool training process** to avoid introducing bias into the model.

### **Features, Signals & Interpretation**
- The model identifies **correlations**, not causation. A high predicted risk does not imply that a specific feature *causes* cancellation.
- Variable accuracy and completeness in reservation records may introduce bias into predictions.
- The model performance reflects the features available in the dataset; additional operational or behavioral features (payments, guest history, corporate contracts, etc.) could improve accuracy.

### **Operational Use & Decision Impact**
- The tool is intended as a **decision-support aid**, not an automated policy engine. Business rules (e.g., deposit requests or overbooking buffers) should remain under human oversight.
- The chosen probability thresholds affect outcomes and trade-offs between:
  - False positives (flagging guests who would not cancel)
  - False negatives (failing to identify true cancellations)
- Targeted interventions (such as stricter deposit rules for high-risk bookings) should be evaluated for **fairness, guest experience, and revenue impact**.
---

##  Platform & Environment Considerations

- The project was developed in **Excel and Python** for demonstration and portfolio purposes.  
  In a production environment, deployment would typically run on a **centralized server or Windows-based system**, where automation, scheduling, and integration with hotel operations tools can be managed more reliably.
- Some Excel automation features, macros, and add-ins may behave differently across **Mac and Windows environments**, so minor adjustments may be required during enterprise implementation.
- For real-world deployment, the preferred approach would include:
  - A controlled execution environment
  - Versioned datasets and pipelines
  - Monitoring, logging, and scheduled retraining

---

These limitations do not reduce the usefulness of the tool, but instead highlight where future iterations could be strengthened through additional data sources, broader hotel coverage, and periodic model retraining.

---




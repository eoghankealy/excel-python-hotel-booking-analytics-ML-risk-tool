# Hotel Booking Cancellation Risk Analysis & Revenue Optimization Project Overview


An end-to-end data analytics solution designed to predict hotel booking cancellations and optimize revenue preservation through targeted guest interventions. Built using booking data from two Portuguese hotels (one city hotel, one resort hotel) spanning July 2015 to August 2017.
This project demonstrates the complete analytics lifecycle: from exploratory analysis and dashboard development, through predictive modeling and validation, to actionable business tools with quantified ROI.

## Business Problem
Hotels face significant revenue loss from booking cancellations. The Resort Hotel experienced a 28% cancellation rate while the City Hotel faced 42% cancellations during the analysis period. Without a systematic approach to identify high-risk bookings, hotels must choose between:

- Accepting revenue loss from cancellations
- Implementing blanket policies that may frustrate low-risk guests
Manually reviewing all bookings (time-intensive and inconsistent)

Solution: A machine learning-powered risk assessment tool that identifies high-risk bookings for targeted intervention, with potential to preserve €160k-€300k in annual revenue.

## Key Components

1. **Interactive Business Dashboards**
Four comprehensive Excel dashboards providing operational insights 
- Resort Hotel Dashboard - Performance metrics including €11.4M total revenue, €96 average ADR, 26,854 bookings, and seasonal revenue patterns
- City Hotel Dashboard - Analytics showing €14.4M total revenue, €107 average ADR, 45,434 bookings, with market segment breakdowns
- Comparative Analysis Dashboard - Side-by-side comparison of both properties across key metrics, revealing operational differences and opportunities
- Forecast & Statistics Dashboard - Revenue forecasting tools with adjustable cancellation rates, historical "what-if" analysis, and cancellation risk model performance metrics

 Technical Features:
- Interactive slicers for filtering by year, season, market segment, and country
- Adjustable slider controls for forecasting scenarios
- Professional design mimicking Tableau/Power BI aesthetic using - Excel shapes and formatting
Custom navigation system with hyperlinked page buttons


2. **Cancellation Risk Prediction Model**

Model Development Journey
- Phase 1 - Heuristic Scorecard Model:

Manually engineered point-based scoring system
Variables selected through business logic and exploratory analysis
Complete ROC curve analysis and confusion matrix performed manually in Excel.
Result: ROC curve showed the model did not quite capture as many cancellations as hoped and that the model could be improved upon

- Phase 2 - Logistic Regression Model (Final):

Training period: July 2015 - December 2016
Validation period: January 2017 - August 2017
Python used for coefficient calculation (Excel computation limitations)
Coefficients implemented back into Excel for operational deployment

**Model Performance**

| Metric | Value | Interpretation |
| :--- | :--- | :--- |
| **AUC Score** | 0.8034 | Strong discriminatory power between cancellations and completions |
| **Recall** | 51% | Identifies over half of all actual cancellations |
| **Precision** | 62% | 62% of flagged bookings are correct (38% false alarm rate) |
| **Optimal Threshold** | 0.30 | Maximizes revenue preservation given €650 average booking value |


Lead time until arrival,
Average Daily Rate (ADR),
Market segment,
Previous cancellation history,
Booking changes,
Deposit type,
Special requests,
Guest nationality and repeat guest status

3. **Operational Risk Tool**

An Excel-based interface that translates model predictions into actionable risk categories:

| Risk Level | Probability Range | Recommended Action | Volume |
| :--- | :--- | :--- | :--- |
| **Low Risk** | 0-29% | Passive monitoring only | ~51% of bookings |
| **Medium Risk** | 30-49% | Automated email reminders, flexible upsell offers | ~46/week |
| **High Risk** | 50%+ | Direct contact via email/phone, retention incentives | ~54/week |


**User Workflow:**

Input booking variables from reservation system
Tool calculates cancellation probability
Color-coded risk level displayed (red/yellow/blue)
Specific intervention actions recommended
Staff can track and update booking status

 4. **ROI Analysis & Business Case
Cost-Benefit Modeling**

The model evaluates intervention effectiveness across multiple scenarios:

- Conservative Case (€3 cost, 5% success rate): +€96,761/year

- Base Case (€5 cost, 10% success rate): +€196,801/year

- Strong Case (€8 cost, 15% success rate): +€293,562/year

**Key Finding:**

 The model generates positive ROI across all realistic intervention scenarios, with returns of €164,001 to €310,000 annually even at conservative success rates of 5-10%.
Risk Segmentation Results
From 2017 test data, the model flagged 3,280 bookings requiring intervention:

- 1,763 High-Risk bookings (54/week) - Priority for direct contact

- 1,517 Medium-Risk bookings (46/week) - Suitable for automated follow-ups

- Low-Risk bookings monitored passively

Revenue at Risk: €4,134,202 in 2017, with potential to save nearly 5% through targeted interventions.

## Technical Skills Demonstrated

**Data Analysis & Visualization**

- Exploratory data analysis on 115,000+ booking records
- Dashboard design and development in Excel
- Visual storytelling through appropriate chart selection
- Interactive filtering and navigation systems

**Statistical Modeling**
- Feature engineering and selection
- Heuristic model development
- Logistic regression implementation
- Model evaluation (ROC curves, AUC, confusion matrices)
- Threshold optimization for business objectives
- Train-test validation methodology

**Business Analytics**

- Cost-benefit analysis
- ROI calculation and scenario modeling
- Revenue forecasting with adjustable parameters
- Risk segmentation strategy
- Conversion of technical metrics into business KPIs

**Technical Tools**

Excel: Advanced formulas, conditional formatting, data modeling, dashboard design
Python: Logistic regression, coefficient calculation
Domain Knowledge: Hospitality revenue management, booking behavior patterns

## Model Insights & Validation

The logistic regression model's ROC-AUC of 0.803 represents strong separation between guests who cancel versus those who complete their stays. The selected operating threshold of 0.30 probability balances:

Recall (51%): Catching half of all cancellations before they occur

Precision (62%): Maintaining reasonable accuracy to avoid intervention fatigue

False Alarm Rate (38%): Acceptable given low intervention costs and high booking values

This threshold maximizes expected revenue preservation given the high average booking value (€650) and manageable cost of interventions.
Data Source & Period

Source: Booking data from two hotels in Portugal

Properties: One resort hotel, one city hotel

Period: July 2015 - August 2017 (25 months)

Records: Approximately 115,000+ bookings

Training Window: July 2015 - December 2016 (18 months)

Test Window: January 2017 - August 2017 (8 months)





## Dashboards & Model Screenshots


- **Resort Hotel Dashboard**  
  ![Resort Hotel Dashboard](./screenshots/resort_dashboard.png)
`


## Project Status
🔧 **Work in progress** — new features, documentation, and refinements will be added soon.

# Data Analysis Project - Autodoc

## 📊 About the Project
This project was developed as part of an Autodoc task, addressing multiple analytical requirements for understanding customer behavior. The solution uses SQL-based analysis to build a purchase funnel, analyze first-session behavior, and identify anomalous user patterns, followed by Power BI visualizations.

## 🎯 Business Requirements
The project addresses the following key business requirements:

### Part 1 - Purchase Funnel Analysis
The product owner wants to change the marketing strategy based on customers' behavior:
1. Build a custom purchase funnel based on tracking data, showing the customer journey from site visit to purchase
2. Define metrics that effectively describe user behavior at each funnel stage
3. Identify additional data needed to evaluate current strategy effectiveness
4. Analyze how customer journeys vary depending on which page type was visited first in a session

### Part 2 - First Session Analysis
1. Write an SQL query that returns the number of clients by day that only viewed products in their first session

### Part 3 - Anomalous Behavior Detection
1. Write a query that will return any abnormal user behavior and describe why the behavior is unusual

## 🛠️ Technologies Used
- **MySQL Workbench 8.0** - Database management and SQL development
  - Primary tool for SQL query development and testing
  - Custom queries for funnel, first-session, and anomaly detection analysis
- **Power BI** - Data visualization and dashboards

## 📁 Project Structure
```
project-autodoc/
│
├── data/                       # Raw and processed data
│   └── data.csv               # Source CSV file
├── sql/                       # SQL queries
│   ├── customer_funnel.sql    # Customer funnel analysis
│   ├── first_session.sql      # First session analysis
│   └── anomaly_detection.sql  # Anomalous behavior detection
├── powerbi/                  # Power BI dashboard files
└── README.md
```

## 💻 Implementation Details

### 1. Purchase Funnel Analysis
To address the product owner's requirements for marketing strategy refinement, a custom SQL view was created that analyzes the purchase funnel with segmentation by entry point:

```sql
CREATE OR REPLACE VIEW customer_funnel_analysis AS
WITH session_steps AS (
    SELECT 
        session,
        user,
        MIN(DATE(event_date)) AS first_visit_date,
        MIN(CASE WHEN event_type = 'view' THEN page_type END) AS first_page_visited,
        COUNT(DISTINCT CASE WHEN event_type = 'view' THEN session END) AS views,
        COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN session END) AS add_to_cart_sessions,
        COUNT(DISTINCT CASE WHEN event_type = 'order' THEN session END) AS purchase_sessions
    FROM USER_EVENTS
    GROUP BY session, user
)
SELECT 
    first_page_visited,
    COUNT(DISTINCT session) AS total_sessions,
    COUNT(DISTINCT user) AS unique_users,
    SUM(views) AS total_views,
    SUM(add_to_cart_sessions) AS total_add_to_cart,
    SUM(purchase_sessions) AS total_purchases,
    ROUND(SUM(add_to_cart_sessions) * 100.0 / NULLIF(SUM(views), 0), 2) AS add_to_cart_rate,
    ROUND(SUM(purchase_sessions) * 100.0 / NULLIF(SUM(add_to_cart_sessions), 0), 2) AS purchase_conversion_rate
FROM session_steps
GROUP BY first_page_visited
ORDER BY total_sessions DESC;
```

#### Key Components of Funnel Analysis

1. **Purchase Funnel Definition**: Three main stages identified (View → Add to Cart → Purchase)
2. **Entry Point Segmentation**: Analysis of how the first page visited impacts the journey
3. **Key Metrics**: Session counts, unique users, stage completion counts, and conversion rates
4. **Journey Variation**: Metrics grouped by entry point to compare different starting points

### 2. First Session Analysis
The following SQL query addresses the requirement to track clients who only viewed products in their first session, grouped by day:

```sql
SELECT 
    DATE(first_session_date) AS first_session_date,
    COUNT(distinct user) AS total_clients
FROM (
    SELECT 
        `user`, 
        MIN(event_date) AS first_session_date
    FROM user_events
    WHERE 
        page_type = 'product_page'
        AND event_date IS NOT NULL      
    GROUP BY 
        `user`
    HAVING 
        COUNT(DISTINCT `session`) = 1 
) AS first_sessions
GROUP BY 
    DATE(first_session_date)
ORDER BY 
    DATE(first_session_date);
```

#### Key Components of First Session Analysis

1. **First Session Identification**: Subquery identifies the earliest event date for each user
2. **Single Session Filter**: The `HAVING COUNT(DISTINCT session) = 1` clause ensures we only include users who had exactly one session
3. **Product Page Filter**: The WHERE condition restricts to product page views
4. **Daily Aggregation**: Results are grouped by date to show the daily count of users

### 3. Anomalous Behavior Detection
The following SQL query identifies users with unusual behavior patterns based on their interaction with the purchase funnel:

```sql
SELECT 
    user,
    COUNT(DISTINCT session) AS session_count,
    COUNT(DISTINCT CASE WHEN event_type = 'view' THEN session END) AS view_sessions,
    COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN session END) AS add_to_cart_sessions,
    COUNT(DISTINCT CASE WHEN event_type = 'order' THEN session END) AS purchase_sessions,
    CASE
        WHEN COUNT(DISTINCT CASE WHEN event_type = 'view' THEN session END) > 5
             AND COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN session END) = 0
             AND COUNT(DISTINCT CASE WHEN event_type = 'order' THEN session END) = 0 THEN 'Unusual'
        WHEN COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN session END) > 0
             AND COUNT(DISTINCT CASE WHEN event_type = 'order' THEN session END) = 0 THEN 'Unusual'
        WHEN COUNT(DISTINCT session) > 10
             AND COUNT(DISTINCT CASE WHEN event_type = 'order' THEN session END) = 0 THEN 'Unusual'
        ELSE 'Normal'
    END AS behavior_status
FROM 
    user_events
GROUP BY 
    user
HAVING 
    behavior_status != 'Normal'
ORDER BY 
    behavior_status DESC;
```

#### Key Components of Anomaly Detection

The query identifies three specific types of anomalous behavior:

1. **Excessive Views Without Add-to-Cart**:
   - Users who have viewed products in more than 5 sessions
   - Never added any item to cart
   - Never made a purchase
   - This may indicate users who are researching but facing barriers to conversion, or possibly bot traffic

2. **Cart Abandonment**:
   - Users who have added items to cart
   - Never completed a purchase
   - This indicates a conversion problem at the final funnel stage, possibly related to pricing, shipping, payment options, or checkout process issues

3. **Excessive Sessions Without Conversion**:
   - Users with more than 10 distinct sessions
   - Never completed a purchase
   - This may indicate users who are highly engaged but unconvinced, or users facing technical issues that prevent completion

#### Business Value of Anomaly Detection

This analysis provides significant business value by:
- Identifying potential conversion blockers in the purchase funnel
- Highlighting opportunities for targeted remarketing
- Detecting possible technical issues with the checkout process
- Revealing segments of users who may need special attention or incentives
- Differentiating between normal shopping behavior and problematic patterns

## 🚀 How to Run

1. Import the tracking data into your MySQL database
2. Execute the SQL scripts to create the analyses:
   ```
   source /path/to/customer_funnel.sql
   source /path/to/first_session.sql
   source /path/to/anomaly_detection.sql
   ```
3. Connect Power BI to the MySQL database
4. Create visualizations based on all analyses:
   - Funnel visualization showing drop-off rates
   - Time series chart showing first-session product viewers by day
   - Dashboard for monitoring anomalous user behavior

## 📊 Key Deliverables

1. **Purchase Funnel Analysis**: Comprehensive view of customer journey with entry point segmentation
2. **First Session Analysis**: Daily trend of users who only viewed products in their first session
3. **Anomaly Detection**: Identification of users with unusual behavior patterns
4. **Defined Metrics**: Clear metrics established for evaluating marketing effectiveness
5. **Recommendations**: Actionable insights for improving conversion rates

## 🔄 Future Enhancements

Based on the analyses performed, the following enhancements are recommended:

1. **Integrated Dashboard**: Combine all three analyses into a comprehensive dashboard
2. **User Segmentation**: Expand analysis to include demographic and behavioral segmentation
3. **A/B Testing**: Implement tracking for A/B tests to measure effectiveness of conversion improvements
4. **Predictive Models**: Develop models to predict likely cart abandonment based on early session behavior
5. **Automated Alerting**: Create automated alerts for significant changes in anomaly patterns

## 👤 Author
Vítor Marques
Senior Data Analyst

## 📫 Contact
- LinkedIn: [Vítor Marques](https://www.linkedin.com/in/vitormarquesds/)
- Email: vitormarques0328@gmail.com

## 🙏 Acknowledgments
Thanks to the Autodoc team for the opportunity to develop this project.

---
⭐ If this project was helpful to you, consider giving it a star!
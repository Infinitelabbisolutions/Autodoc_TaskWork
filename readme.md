# Data Analysis Project - Autodoc

## 📊 About the Project
This project was developed as part of an Autodoc task, addressing multiple analytical requirements for understanding customer behavior. The solution uses SQL-based analysis to build a purchase funnel and analyze first-session behavior, followed by Power BI visualizations.

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

## 🛠️ Technologies Used
- **MySQL Workbench 8.0** - Database management and SQL development
  - Primary tool for SQL query development and testing
  - Custom view creation for funnel and first-session analysis
- **Power BI** - Data visualization and dashboards

## 📁 Project Structure
```
project-autodoc/
│
├── data/                       # Raw and processed data
│   └── data.csv               # Source CSV file
├── sql/                       # SQL queries
│   ├── customer_funnel.sql    # Customer funnel analysis
│   └── first_session.sql      # First session analysis
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

#### Additional Data Needed for Marketing Strategy
To fully evaluate marketing effectiveness, additional data would enhance the analysis:
- Marketing campaign attribution
- Customer demographic information
- Product category and pricing data
- Session duration and engagement metrics
- Additional interaction events beyond the basic funnel

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
        # AND event_type = 'page_view'           
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

1. **First Session Identification**: Subquery identifies the earliest event date for each user where they viewed a product page
2. **Single Session Filter**: The `HAVING COUNT(DISTINCT session) = 1` clause ensures we only include users who had exactly one session
3. **Product Page Filter**: The WHERE condition restricts to product page views
4. **Daily Aggregation**: Results are grouped by date to show the daily count of users meeting these criteria
5. **User Counting**: Distinct users are counted to avoid duplication

#### Insights from First Session Analysis
This query provides valuable insights for several business applications:
- Identifying the rate of one-time product browsers
- Tracking new user acquisition trends over time
- Detecting potential issues with user retention after initial product interest
- Evaluating the effectiveness of product pages for first-time visitors

## 🚀 How to Run

1. Import the tracking data into your MySQL database
2. Execute the SQL scripts to create the analyses:
   ```
   source /path/to/customer_funnel.sql
   source /path/to/first_session.sql
   ```
3. Connect Power BI to the MySQL database
4. Create visualizations based on both analyses:
   - Funnel visualization showing drop-off rates
   - Time series chart showing first-session product viewers by day
   - Comparative analysis between entry points and conversion rates

## 📊 Key Deliverables

1. **Purchase Funnel Analysis**: Comprehensive view of customer journey with entry point segmentation
2. **First Session Analysis**: Daily trend of users who only viewed products in their first session
3. **Defined Metrics**: Clear metrics established for evaluating marketing effectiveness
4. **Recommendations**: Identification of additional data needed for deeper analysis

## 🔄 Future Enhancements

Based on the initial analyses, the following enhancements are recommended:

1. **Integrated Analysis**: Combine funnel analysis with first-session behavior for deeper insights
2. **User Segmentation**: Analyze how different user types progress through the purchase funnel
3. **Temporal Analysis**: Extend analysis to understand seasonal patterns and trends
4. **Path Analysis**: Create more detailed navigation path analysis
5. **Retention Metrics**: Add analysis of repeat visits and purchases after the first session

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
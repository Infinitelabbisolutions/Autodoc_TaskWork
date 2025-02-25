# Data Analysis Project - Autodoc

## 📊 About the Project
This project was developed as part of an Autodoc task, implementing a data analytics pipeline. The solution involves SQL-based ETL transformations and analysis, followed by Power BI visualizations.

The workflow includes:
1. Data transformation and analysis using SQL views
2. Funnel analysis and behavior pattern extraction
3. Visualization of insights using Power BI

## 🛠️ Technologies Used
- **MySQL Workbench 8.0** - Database management, ETL process and SQL development
  - Primary tool for SQL query development, ETL transformations and testing
  - Note: SQL syntax may need adjustments if using different database tools
  - Specific features like `GROUP_CONCAT` and `TIMESTAMPDIFF` are MySQL-specific
- **Power BI** - Data visualization and dashboards

### ⚠️ Important Note About SQL Compatibility
The SQL views in this project were developed and tested in MySQL Workbench 8.0. If you're using a different SQL environment, you may need to adjust:
- Function names (e.g., `TIMESTAMPDIFF` might be different in PostgreSQL)
- String concatenation syntax (e.g., `GROUP_CONCAT` is MySQL-specific)
- Date/time functions (may vary across different SQL flavors)
- Index creation syntax
- Window function syntax

## 📁 Project Structure
```
project-autodoc/
│
├── data/                    # Raw and processed data
│   └── data.csv            # Source CSV file
├── sql/                    # SQL queries and ETL processes
├── powerbi/               # Power BI dashboard files
└── README.md
```

## 💻 Implementation Details

### SQL ETL Process and Analysis
The project uses MySQL views to transform raw data into analytical insights. The ETL process begins with SQL transformations that:
- Create customer journey analysis views
- Build temporal behavior analysis models
- Develop cohort retention analysis
- Construct purchase funnel metrics

The SQL views serve both as transformation layers and as analytical endpoints for Power BI visualization.

#### Customer Journey Analysis View
```sql
CREATE VIEW vw_customer_journey AS
WITH journey AS (
    SELECT 
        session,
        user,
        page_type,
        FIRST_VALUE(page_type) OVER (
            PARTITION BY session 
            ORDER BY event_date
        ) as first_page_type  
    FROM user_events
    WHERE session IS NOT NULL
)
SELECT 
    first_page_type,         
    page_type,
    COUNT(DISTINCT session) as sessions,
    COUNT(DISTINCT user) as users,
    COUNT(*) as page_views
FROM journey
GROUP BY 
    first_page_type,         
    page_type;
```

This view analyzes user journey patterns by:
- Tracking the first page type visited in each session
- Analyzing subsequent page type visits
- Measuring session and user counts for each page type transition
- Calculating total page views for each combination

#### Customer Funnel Analysis View
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

This view provides complete e-commerce funnel metrics:
- First page visited in each session
- Number of sessions and unique users
- Conversion rates through the purchase funnel
- Add-to-cart rates by entry point
- Purchase conversion rates by entry point
- Funnel progression segmented by first page visited

#### User Behavior Analysis View
```sql
CREATE VIEW vw_user_behavior AS 
WITH user_patterns AS (
    SELECT 
        user,
        session,
        -- Temporal patterns
        HOUR(event_date) as hour_of_day,
        WEEKDAY(event_date) as day_of_week,
        COUNT(DISTINCT page_type) as pages_types_visited,
        COUNT(DISTINCT product) as products_viewed,
        -- Navigation sequence
        GROUP_CONCAT(page_type ORDER BY event_date SEPARATOR ' > ') as navigation_path
    FROM user_events
    GROUP BY 
        user, 
        session, 
        HOUR(event_date), 
        WEEKDAY(event_date)
)
SELECT 
    hour_of_day,
    COUNT(DISTINCT session) as sessions_count,
    COUNT(DISTINCT user) as users_count,
    -- Engagement metrics
    ROUND(AVG(pages_types_visited), 2) as avg_page_types_per_session,
    ROUND(AVG(products_viewed), 2) as avg_products_per_session,
    COUNT(DISTINCT navigation_path) as unique_paths
FROM user_patterns
GROUP BY hour_of_day
ORDER BY hour_of_day;
```

This view analyzes temporal user behavior patterns:
- Hourly activity distribution
- Session engagement metrics
- Navigation path analysis
- User interaction patterns throughout the day

#### Cohort Analysis View
```sql
CREATE VIEW vw_cohort_analysis AS
WITH user_first_visit AS (
    SELECT 
        user,
        DATE(MIN(event_date)) as first_visit_date
    FROM user_events
    GROUP BY user
),
user_activity AS (
    SELECT 
        ufv.user,
        ufv.first_visit_date,
        DATE(d.event_date) as activity_date,
        DATEDIFF(DATE(d.event_date), ufv.first_visit_date) as days_since_first_visit
    FROM user_first_visit ufv
    JOIN user_events d ON ufv.user = d.user
)
SELECT 
    first_visit_date as cohort_date,
    days_since_first_visit,
    COUNT(DISTINCT user) as active_users,
    -- Retention relative to day one
    ROUND(COUNT(DISTINCT user) / 
          FIRST_VALUE(COUNT(DISTINCT user)) OVER (
              PARTITION BY first_visit_date 
              ORDER BY days_since_first_visit
          ) * 100, 2) as retention_rate
FROM user_activity
GROUP BY first_visit_date, days_since_first_visit
ORDER BY first_visit_date, days_since_first_visit;
```

This view performs cohort analysis to track user retention:
- Groups users by their first visit date
- Tracks user activity over time
- Calculates retention rates for each cohort
- Measures user engagement longevity

The combination of these views provides a comprehensive understanding of:
- Customer journey and conversion funnel
- Temporal usage patterns
- User engagement and behavior
- Navigation flow analysis
- Cohort-based retention metrics

### Database Schema
The `user_events` table is optimized with indexes for common query patterns:
- Primary key on `id`
- Indexes on event_date, user, session, page_type, and event_type
- UTF-8 character encoding for international data support

## 🚀 How to Run

1. Import the data into your MySQL database
2. Execute SQL ETL processes in MySQL Workbench
   Run the SQL scripts in the sql/ directory to create the necessary views and transformations
3. Connect Power BI to the MySQL database and build visualizations based on the created views

## 📊 Key Features
- SQL-based ETL for data transformation and analysis
- Optimized database schema with appropriate indexing
- Customer journey and conversion funnel analysis
- Temporal user behavior analysis
- Cohort retention analysis

## 🔄 Future Improvements
- Develop more advanced SQL-based ETL transformations
- Create automated refresh processes for the analytical views
- Implement more sophisticated cohort analysis techniques
- Enhance visualization capabilities in Power BI
- Add additional dimensions to the funnel analysis

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
# Data Analysis Project - Autodoc

## 📊 About the Project
This project was developed as part of an Autodoc task, implementing a robust data pipeline for processing and analyzing user events data. The solution includes a scalable ETL process using Python for data ingestion into MySQL, followed by SQL analysis and Power BI visualizations.

## 🛠️ Technologies Used
- **Python 3.x** - Data processing and MySQL integration
  - pandas - Data manipulation and CSV processing
  - mysql-connector-python - Database connection and operations
  - typing - Type hints for better code maintenance
  - logging - Comprehensive error tracking and operation logging
- **MySQL Workbench 8.0** - Database management and SQL development
  - Primary tool for SQL query development and testing
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
├── src/                    # Source code
│   └── data_ingestion.py  # Main ETL script
├── sql/                   # SQL queries
├── powerbi/              # Power BI dashboard files
└── README.md
```

## 💻 Implementation Details

### Data Ingestion Process
The project implements a memory-efficient ETL process that:
- Processes large CSV files in chunks to manage memory usage
- Creates optimized MySQL table structure with appropriate indexes
- Implements batch processing for efficient data insertion
- Includes comprehensive error handling and logging
- Maintains data integrity through transaction management

### Python Implementation

The ETL process is implemented in Python with a focus on efficiency and reliability. Here's the complete implementation:

```python
import pandas as pd
import mysql.connector
from mysql.connector import Error
from typing import Iterator
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_csv_in_chunks(filename: str, chunksize: int = 10000) -> Iterator[pd.DataFrame]:
    """
    Processes CSV file in chunks to optimize memory usage.
    """
    try:
        for chunk in pd.read_csv(filename, chunksize=chunksize):
            chunk['event_date'] = pd.to_datetime(chunk['event_date'])
            yield chunk
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        raise

def create_table_if_not_exists(cursor) -> None:
    """
    Creates table with optimized structure and indexes.
    Includes indexes for common query patterns.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_events (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        event_date DATETIME,
        session VARCHAR(255),
        user VARCHAR(255),
        page_type VARCHAR(50),
        event_type VARCHAR(50),
        product BIGINT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_event_date (event_date),
        INDEX idx_user (user),
        INDEX idx_session (session),
        INDEX idx_page_type (page_type),
        INDEX idx_event_type (event_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    try:
        cursor.execute(create_table_query)
        logger.info("Table created or already exists")
    except Error as e:
        logger.error(f"Error creating table: {e}")
        raise

def insert_data_batch(connection, cursor, chunk: pd.DataFrame) -> None:
    """
    Inserts data in batches using executemany for better performance.
    """
    insert_query = """
    INSERT INTO user_events 
    (event_date, session, user, page_type, event_type, product)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        values = chunk.values.tolist()
        cursor.executemany(insert_query, values)
        connection.commit()
        logger.info(f"Successfully inserted {len(values)} records")
    except Error as e:
        logger.error(f"Error inserting batch: {e}")
        connection.rollback()
        raise

def import_csv_to_mysql(host: str, user: str, password: str, database: str, csv_file: str, 
                       chunksize: int = 10000) -> None:
    """
    Main function coordinating the data import process.
    Features:
    - Chunk-based processing
    - Performance monitoring
    - Error handling
    - Transaction management
    """
    start_time = datetime.now()
    total_records = 0

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            use_unicode=True,
            buffered=True
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            create_table_if_not_exists(cursor)
            
            for chunk in process_csv_in_chunks(csv_file, chunksize):
                insert_data_batch(connection, cursor, chunk)
                total_records += len(chunk)
                
            cursor.execute("OPTIMIZE TABLE user_events")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Import completed! Total time: {duration:.2f} seconds")
            logger.info(f"Total records imported: {total_records}")

    except Error as e:
        logger.error(f"MySQL connection error: {e}")
        raise
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("MySQL connection closed")

if __name__ == "__main__":
    # Configuration
    mysql_config = {
        'host': 'localhost',
        'user': 'your_username',
        'password': 'your_password',
        'database': 'autodoc'
    }
    
    config = {
        'csv_file': 'data.csv',
        'chunksize': 10000
    }
    
    try:
        import_csv_to_mysql(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database'],
            csv_file=config['csv_file'],
            chunksize=config['chunksize']
        )
    except Exception as e:
        logger.error(f"Error during import: {e}")
```

Key features of the implementation:
- Efficient memory usage through chunk-based processing
- Comprehensive error handling and logging
- Optimized database operations with batch inserts
- Transaction management for data integrity
- Performance monitoring and reporting
- UTF-8 support for international characters
- Automated table creation with optimized indexes

### SQL Analysis
The project includes several analytical views developed in MySQL Workbench 8.0 to understand user behavior and customer journey. These views use MySQL-specific features and syntax - please note that adjustments may be needed if you're using a different database system:

#### Customer Journey Analysis View
```sql
CREATE VIEW vw_customer_journey AS
WITH session_start AS (
    -- Identifies first page of each session
    SELECT 
        session,
        user,
        MIN(page_type) as first_page_type,
        MIN(event_date) as session_start_time
    FROM user_events
    GROUP BY session, user
),
journey_steps AS (
    -- Complete journey analysis
    SELECT 
        d.session,
        d.user,
        ss.first_page_type,
        COUNT(DISTINCT CASE WHEN d.page_type = 'listing_page' THEN d.event_date END) as listing_views,
        COUNT(DISTINCT CASE WHEN d.page_type = 'search_listing_page' THEN d.event_date END) as search_views,
        COUNT(DISTINCT CASE WHEN d.page_type = 'product_page' THEN d.event_date END) as product_views,
        COUNT(DISTINCT d.product) as unique_products_viewed,
        -- Session duration in minutes
        TIMESTAMPDIFF(MINUTE, MIN(d.event_date), MAX(d.event_date)) as session_duration_minutes
    FROM user_events d
    JOIN session_start ss ON d.session = ss.session
    GROUP BY d.session, d.user, ss.first_page_type
)
SELECT 
    first_page_type,
    COUNT(DISTINCT session) as total_sessions,
    COUNT(DISTINCT user) as unique_users,
    -- Funnel metrics
    SUM(listing_views) as total_listing_views,
    SUM(search_views) as total_search_views,
    SUM(product_views) as total_product_views,
    -- Averages per session
    ROUND(AVG(unique_products_viewed), 2) as avg_products_per_session,
    ROUND(AVG(session_duration_minutes), 2) as avg_session_duration,
    -- Funnel conversion rates
    ROUND(SUM(CASE WHEN product_views > 0 THEN 1 ELSE 0 END) / 
          COUNT(DISTINCT session) * 100, 2) as product_view_rate,
    ROUND(SUM(CASE WHEN search_views > 0 THEN 1 ELSE 0 END) / 
          COUNT(DISTINCT session) * 100, 2) as search_view_rate
FROM journey_steps
GROUP BY first_page_type;
```

This view provides comprehensive metrics about the customer journey:
- Session analysis by entry point (first_page_type)
- User engagement metrics (views, duration)
- Funnel conversion rates
- Product interaction patterns

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

1. Clone the repository
```bash
git clone [your-repository]
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure MySQL connection
Update the MySQL configuration in the script:
```python
mysql_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'autodoc'
}
```

4. Run the data ingestion script
```bash
python src/data_ingestion.py
```

## 📊 Key Features
- Chunk-based processing for handling large datasets
- Robust error handling and logging
- Optimized database schema with appropriate indexing
- Transaction management for data integrity
- Performance monitoring and execution timing
- Memory-efficient data processing

## 📝 Additional Notes
- The script includes comprehensive logging for monitoring and debugging
- Batch size can be adjusted through the `chunksize` parameter
- Database indexes are optimized for common query patterns
- Error handling includes automatic rollback for failed transactions

## 🔄 Future Improvements
- Implement parallel processing for faster data ingestion
- Add data validation and cleaning steps
- Create automated tests
- Implement incremental loading strategy
- Add configuration file support

## 👤 Author
Vítor Marques
Senior Data Analyst

## 📫 Contact
- LinkedIn: [Vítor Marques](https://www.linkedin.com/in/vitormarquesds/)
- Email: vitormarques0328@gmail.com

## 🙏 Acknowledgments
Thanks to the Autodoc team for the opportunity to develop this project.

---

# Data Analysis Project - Autodoc

## 📊 About the Project
This project was developed as part of an Autodoc task, implementing a robust data pipeline for processing and analyzing user events data. The solution includes a scalable ETL process using Python for data ingestion into MySQL, followed by SQL analysis and Power BI visualizations.

## 🛠️ Technologies Used
- **Python 3.x** - Data processing and MySQL integration
  - pandas - Data manipulation and CSV processing
  - mysql-connector-python - Database connection and operations
  - typing - Type hints for better code maintenance
  - logging - Comprehensive error tracking and operation logging
- **MySQL** - Data storage and querying
- **Power BI** - Data visualization and dashboards

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
```python
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
    cursor.execute(create_table_query)
```

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
[Your Name]

## 📫 Contact
- LinkedIn: [your profile]
- Email: [your email]

## 🙏 Acknowledgments
Thanks to the Autodoc team for the opportunity to develop this project.

---
⭐ If this project was helpful to you, consider giving it a star!
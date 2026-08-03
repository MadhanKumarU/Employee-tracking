# Employee Workforce Analytics Platform

## Overview

The Employee Workforce Analytics Platform is an end-to-end application designed to monitor employee attendance, analyze workforce productivity, and generate automated HR reports.

The project integrates frontend, backend, database management, and data engineering workflows to automate employee tracking and reporting.

It demonstrates full-stack development along with data engineering concepts such as ETL pipelines, business rule validation, workflow scheduling, and report generation.

---

## Features

- Employee attendance tracking
- Employee record management
- Attendance data storage in database
- Automated ETL pipeline using PySpark
- Business rule validation using SQL
- Daily HR report generation
- Apache Airflow workflow scheduling
- Weekly cleanup of historical attendance records
- REST API for backend services
- Simple and responsive web interface

---

## Business Rules

The ETL pipeline automatically validates employee attendance data based on the following rules:

- Employees working **less than 7 hours**
- Employees having **idle time greater than 2 hours**
- Missing or invalid attendance records
- Duplicate employee entries

Employees matching these conditions are included in the HR report for further review.

---

## Workflow

```
Employee
    │
    ▼
Frontend (HTML, CSS, JavaScript)
    │
    ▼
Backend API (Python / FastAPI)
    │
    ▼
MySQL Database
    │
    ▼
PySpark ETL Pipeline
    │
    ▼
Business Rule Validation
    │
    ├── Working Hours < 7 Hours
    ├── Idle Time > 2 Hours
    ▼
HR Report Generation
    │
    ▼
Apache Airflow Scheduler
    │
    ▼
Weekly Cleanup Process
```

---

## Technology Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- FastAPI
- SQLAlchemy

### Database
- MySQL

### Data Engineering
- PySpark
- Apache Airflow
- SQL

### Libraries
- Pandas
- Pydantic
- Uvicorn
- Snowflake Connector

---

## Repository Structure

```
Employee-tracking/

├── README.md
├── employee_pipeline.py
├── Airflow Dag.py
├── create_tables.sql
├── business_rules.sql
├── Sample_employee_attendance.csv
├── main.py
├── agent.py
├── app.js
├── index.html
├── style.css
├── requirements.txt
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/MadhanKumarU/Employee-tracking.git
```

### Navigate to the project

```bash
cd Employee-tracking
```

### Install the required dependencies

```bash
pip install -r requirements.txt
```

### Run the backend

```bash
python main.py
```

---

## Future Enhancements

- Azure Data Lake Storage (ADLS) Integration
- Snowflake Data Warehouse
- Streamlit Dashboard
- Power BI Dashboard
- Kafka-based Real-Time Data Streaming
- Email Notification Service
- Role-Based Access Control
- Predictive Workforce Analytics

---

## Project Highlights

- Developed an end-to-end employee tracking application.
- Designed backend APIs using FastAPI.
- Stored employee attendance data in MySQL.
- Built PySpark ETL pipelines for processing attendance data.
- Implemented SQL business rules to identify employees with low working hours and high idle time.
- Automated workflow scheduling using Apache Airflow.
- Generated HR reports for workforce analytics.
- Implemented weekly cleanup of historical attendance data.

---

## Author

**Madhan Kumar U**

GitHub: https://github.com/MadhanKumarU

---

## License

This project is created for learning and demonstration purposes.


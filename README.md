# bcancerportal

A web application for exploring cancer genomics databases, built with Flask and React.js.

## Features

- Browse multiple cancer databases organized by cancer type
- View summary statistics and visualizations for each database
- Explore clinical patient data
- Analyze mutation profiles
- Examine gene expression, methylation, and protein data
- Interactive data visualization using Plotly and D3.js

## Project Structure

```
cancer-db-explorer/
├── backend/              # Flask backend
│   ├── app.py            # Main Flask application
│   ├── models.py         # Database models
│   ├── database.py       # Database connection
│   ├── config.py         # Configuration
│   └── routes/           # API endpoints
├── frontend/             # React frontend
│   ├── public/           # Static files
│   └── src/              # React source code
└── requirements.txt      # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- MySQL 5.7+

### Backend Setup

1. Create a MySQL database:

```sql
CREATE DATABASE cancer_db;
```

2. Set up a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required Python packages:

```bash
pip install -r requirements.txt
```

4. Configure your database connection in `backend/config.py` or use environment variables:

```bash
export MYSQL_HOST=localhost
export MYSQL_USER=yourusername
export MYSQL_PASSWORD=yourpassword
export MYSQL_DB=cancer_db
```

5. Run the Flask backend:

```bash
cd backend
python app.py
```

The Flask API will be available at http://localhost:5000.

### Frontend Setup

1. Install the required Node.js packages:

```bash
cd frontend
npm install
```

2. Start the React development server:

```bash
npm start
```

The React application will be available at http://localhost:3000.

## API Endpoints

### Database Endpoints

- `GET /api/databases/` - Get all databases grouped by type
- `GET /api/databases/:database_name` - Get information about a specific database
- `GET /api/databases/tables/:database_name` - Get all tables for a specific database

### Data Endpoints

- `GET /api/data/summary/:database_name` - Get summary statistics and graphs for a database
- `GET /api/data/clinical/:database_name` - Get clinical data for a database
- `GET /api/data/mutations/:database_name` - Get mutation data for a database

## Technologies Used

### Backend
- Flask - Web framework
- SQLAlchemy - ORM for database interactions
- Pandas - Data manipulation
- Plotly - Data visualization
- PyMySQL - MySQL connector

### Frontend
- React - UI library
- React Router - Navigation
- React Bootstrap - UI components
- Axios - HTTP client
- Plotly.js - Interactive charts
- D3.js - Data visualization

## License

MIT
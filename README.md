# QLib Web Analytics

A comprehensive web application for quantitative investment analysis using Microsoft's QLib framework. Upload custom trade data and price series to generate detailed analytics, portfolio performance metrics, and model analysis visualizations.

## 🚀 Features

- **Data Upload**: Upload CSV files with trade series and OHLCV price data
- **Portfolio Analysis**: Interactive cumulative returns visualization with Plotly
- **Model Performance**: Information Coefficient analysis and prediction accuracy metrics
- **Real-time Statistics**: Live data summaries showing records, instruments, and date ranges
- **QLib Integration**: Full Microsoft QLib quantitative analysis capabilities
- **Responsive Design**: Modern React interface with Tailwind CSS

## 📋 Prerequisites

- Python 3.8+ with Poetry
- Node.js 16+ with npm
- Git

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/qlib-web-analytics.git
cd qlib-web-analytics
```

### 2. Backend Setup (FastAPI + QLib)

```bash
# Install Python dependencies
cd qlib-web-analytics
poetry install

# Install QLib (if not already installed)
poetry add pyqlib plotly pandas numpy

# Start the backend server
poetry run fastapi dev app/main.py
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup (React + TypeScript)

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📊 Usage

### Data Upload

1. **Trade Data**: Upload CSV files with columns:
   - `instrument`: Stock symbol (e.g., AAPL, MSFT)
   - `datetime`: Date in YYYY-MM-DD format
   - `return`: Return value for the trade

2. **Price Data**: Upload CSV files with columns:
   - `instrument`: Stock symbol
   - `datetime`: Date in YYYY-MM-DD format
   - `open`, `high`, `low`, `close`: OHLC price data
   - `volume`: Trading volume

### Sample Data

The application includes sample data for AAPL, MSFT, and GOOGL to test functionality immediately.

### Analysis Features

- **Portfolio Analysis**: View cumulative returns and performance metrics
- **Model Performance**: Analyze Information Coefficient and prediction accuracy
- **Complete Analysis**: Run comprehensive analysis combining all metrics

## 🏗️ Project Structure

```
qlib-web-analytics/
├── app/                          # FastAPI backend
│   ├── main.py                   # Main FastAPI application
│   └── data_processor.py         # QLib data processing logic
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.tsx    # File upload component
│   │   │   ├── AnalysisDisplay.tsx # Analysis visualization
│   │   │   └── ui/               # UI components
│   │   └── App.tsx               # Main application
│   ├── package.json
│   └── .env                      # Environment variables
├── sample_trade_data.csv         # Sample trade data
├── sample_price_data.csv         # Sample price data
└── README.md
```

## 🔧 API Endpoints

- `POST /upload/trades` - Upload trade data CSV
- `POST /upload/prices` - Upload price data CSV
- `GET /data/summary` - Get data availability summary
- `GET /analyze/portfolio` - Run portfolio analysis
- `GET /analyze/model` - Run model performance analysis
- `GET /analyze/all` - Run comprehensive analysis

## 🧪 Testing

### Backend Testing

```bash
# Test data upload
curl -X POST "http://localhost:8000/upload/trades" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample_trade_data.csv"

# Test analysis
curl "http://localhost:8000/analyze/portfolio"
```

### Frontend Testing

1. Open `http://localhost:5173` in your browser
2. Upload the provided sample CSV files
3. Click analysis buttons to view interactive charts
4. Verify all visualizations render correctly

## 📈 QLib Integration

This application leverages Microsoft QLib's powerful quantitative analysis capabilities:

- **Alpha Factor Generation**: 300+ built-in alpha factors
- **Portfolio Optimization**: Risk-adjusted return analysis
- **Backtesting Framework**: Historical performance evaluation
- **Model Performance Metrics**: IC analysis, group returns, auto-correlation

## 🔒 Data Storage

The application uses in-memory data storage for this proof of concept. Data will be lost when the backend server restarts. For production use, consider integrating with a persistent database.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Microsoft QLib](https://github.com/microsoft/qlib) - AI-oriented quantitative investment platform
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - Frontend JavaScript library
- [Plotly](https://plotly.com/) - Interactive visualization library

## 🐛 Troubleshooting

### Common Issues

1. **QLib Installation**: If QLib installation fails, try:
   ```bash
   pip install pyqlib --no-cache-dir
   ```

2. **Port Conflicts**: If ports 8000 or 5173 are in use, modify the configuration:
   - Backend: Change port in `poetry run fastapi dev app/main.py --port 8001`
   - Frontend: Change port in `package.json` scripts

3. **CORS Issues**: Ensure the backend CORS configuration in `app/main.py` includes your frontend URL

### Support

For issues and questions, please open an issue on the GitHub repository.

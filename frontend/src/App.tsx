import { useState, useEffect } from 'react';
import { FileUpload } from './components/FileUpload';
import { AnalysisDisplay } from './components/AnalysisDisplay';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { TrendingUp, Database } from 'lucide-react';

function App() {
  const [dataSummary, setDataSummary] = useState<any>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const fetchDataSummary = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/data/summary`);
      const data = await response.json();
      setDataSummary(data);
    } catch (error) {
      console.error('Failed to fetch data summary:', error);
    }
  };

  useEffect(() => {
    fetchDataSummary();
  }, [refreshTrigger]);

  const handleUploadSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const dataAvailable = dataSummary?.trade_data_available && dataSummary?.price_data_available;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <header className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900 flex items-center justify-center gap-3">
            <TrendingUp className="h-10 w-10 text-blue-600" />
            QLib Web Analytics v2.0
          </h1>
          <p className="text-xl text-gray-600">
            Quantitative Investment Analysis Platform - Updated {new Date().toISOString().split('T')[0]}
          </p>
        </header>

        {dataSummary && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Data Status
              </CardTitle>
              <CardDescription>Current data availability and summary</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h3 className="font-semibold">Trade Data</h3>
                  {dataSummary.trade_data_available ? (
                    <div className="text-sm text-green-700 bg-green-50 p-2 rounded">
                      <p>✓ {dataSummary.trade_data_info?.records} records</p>
                      <p>✓ {dataSummary.trade_data_info?.instruments} instruments</p>
                      <p>✓ {dataSummary.trade_data_info?.date_range}</p>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No trade data uploaded</p>
                  )}
                </div>
                <div className="space-y-2">
                  <h3 className="font-semibold">Price Data</h3>
                  {dataSummary.price_data_available ? (
                    <div className="text-sm text-green-700 bg-green-50 p-2 rounded">
                      <p>✓ {dataSummary.price_data_info?.records} records</p>
                      <p>✓ {dataSummary.price_data_info?.instruments} instruments</p>
                      <p>✓ {dataSummary.price_data_info?.date_range}</p>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No price data uploaded</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <FileUpload
            endpoint="/upload/trades"
            title="Upload Trade Data"
            description="Upload CSV file with trade data. Supports: (instrument, datetime, return) or (DateTime, Instrument, PnL) formats"
            onUploadSuccess={handleUploadSuccess}
          />
          <FileUpload
            endpoint="/upload/prices"
            title="Upload Price Data"
            description="Upload CSV file with price data. Supports: (instrument, datetime, open, high, low, close, volume) or (dates, Open, High, Low, Close, Volume) formats"
            onUploadSuccess={handleUploadSuccess}
          />
        </div>

        <AnalysisDisplay dataAvailable={dataAvailable} />

        <footer className="text-center text-gray-500 text-sm">
          <p>Powered by Microsoft QLib - AI-oriented Quantitative Investment Platform</p>
        </footer>
      </div>
    </div>
  );
}

export default App;

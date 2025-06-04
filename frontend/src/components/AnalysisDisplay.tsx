import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { BarChart3, TrendingUp, Activity, Loader2 } from 'lucide-react';
import Plot from 'react-plotly.js';

interface AnalysisDisplayProps {
  dataAvailable: boolean;
}

export const AnalysisDisplay: React.FC<AnalysisDisplayProps> = ({ dataAvailable }) => {
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (type: 'portfolio' | 'model' | 'all') => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/analyze/${type}`);
      const data = await response.json();

      if (response.ok) {
        setAnalysisData(data);
      } else {
        setError(data.detail || 'Analysis failed');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const renderPlotlyFigure = (figureJson: string, index: number) => {
    try {
      const figure = JSON.parse(figureJson);
      return (
        <div key={index} className="mb-6">
          <Plot
            data={figure.data}
            layout={{
              ...figure.layout,
              autosize: true,
              responsive: true,
            }}
            style={{ width: '100%', height: '400px' }}
            useResizeHandler={true}
          />
        </div>
      );
    } catch (err) {
      return (
        <div key={index} className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">Error rendering chart {index + 1}</p>
        </div>
      );
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          QLib Analysis
        </CardTitle>
        <CardDescription>
          Run comprehensive quantitative analysis on your uploaded data
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2 flex-wrap">
          <Button
            onClick={() => runAnalysis('portfolio')}
            disabled={!dataAvailable || loading}
            variant="outline"
            className="flex items-center gap-2"
          >
            <TrendingUp className="h-4 w-4" />
            Portfolio Analysis
          </Button>
          <Button
            onClick={() => runAnalysis('model')}
            disabled={!dataAvailable || loading}
            variant="outline"
            className="flex items-center gap-2"
          >
            <Activity className="h-4 w-4" />
            Model Performance
          </Button>
          <Button
            onClick={() => runAnalysis('all')}
            disabled={!dataAvailable || loading}
            className="flex items-center gap-2"
          >
            <BarChart3 className="h-4 w-4" />
            Complete Analysis
          </Button>
        </div>

        {loading && (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="h-8 w-8 animate-spin" />
            <span className="ml-2">Running analysis...</span>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {analysisData && (
          <div className="space-y-6">
            {analysisData.analysis_type && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                <h3 className="font-semibold text-blue-800 mb-2">
                  {analysisData.analysis_type === 'portfolio' ? 'Portfolio Analysis' : 'Model Performance Analysis'}
                </h3>
                {analysisData.summary && (
                  <div className="text-sm text-blue-700">
                    {Object.entries(analysisData.summary).map(([key, value]) => (
                      <p key={key}>
                        <span className="font-medium">{key.replace(/_/g, ' ')}:</span> {String(value)}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            )}

            {analysisData.figures && (
              <div>
                <h3 className="text-lg font-semibold mb-4">Visualizations</h3>
                {analysisData.figures.map((figure: string, index: number) =>
                  renderPlotlyFigure(figure, index)
                )}
              </div>
            )}

            {analysisData.portfolio_analysis && (
              <div>
                <h3 className="text-lg font-semibold mb-4">Portfolio Analysis</h3>
                {analysisData.portfolio_analysis.figures?.map((figure: string, index: number) =>
                  renderPlotlyFigure(figure, index)
                )}
              </div>
            )}

            {analysisData.model_analysis && (
              <div>
                <h3 className="text-lg font-semibold mb-4">Model Performance</h3>
                {analysisData.model_analysis.figures?.map((figure: string, index: number) =>
                  renderPlotlyFigure(figure, index)
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

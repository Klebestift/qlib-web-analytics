from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import pandas as pd
import numpy as np
from typing import Dict, Any

from .data_processor import QLibDataProcessor

app = FastAPI(title="QLib Web Analytics", description="Web interface for QLib quantitative analysis")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

data_processor = QLibDataProcessor()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/upload/trades")
async def upload_trades(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        content = await file.read()
        result = data_processor.process_trade_data(content, file.filename)
        
        if result["success"]:
            return JSONResponse(content=result, status_code=200)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/upload/prices")
async def upload_prices(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        content = await file.read()
        result = data_processor.process_price_data(content, file.filename)
        
        if result["success"]:
            return JSONResponse(content=result, status_code=200)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/data/summary")
async def get_data_summary():
    return data_processor.get_data_summary()

@app.get("/analyze/portfolio")
async def analyze_portfolio():
    try:
        dataset_result = data_processor.prepare_qlib_dataset()
        if not dataset_result["success"]:
            raise HTTPException(status_code=400, detail=dataset_result["error"])
        
        pred_label_df = dataset_result["pred_label_data"]
        
        
        dates = pred_label_df.index.get_level_values('datetime').unique()
        returns = []
        for date in dates:
            date_data = pred_label_df[pred_label_df.index.get_level_values('datetime') == date]
            avg_return = date_data['label'].mean()
            returns.append(avg_return)
        
        cumulative_returns = np.cumsum(returns)
        
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(cumulative_returns))),
            y=cumulative_returns,
            mode='lines',
            name='Cumulative Returns'
        ))
        fig.update_layout(
            title='Portfolio Cumulative Returns',
            xaxis_title='Time Period',
            yaxis_title='Cumulative Return'
        )
        
        figures = [fig]
        
        figure_json = [fig.to_json() for fig in figures]
        
        return {
            "success": True,
            "analysis_type": "portfolio",
            "figures": figure_json,
            "summary": {
                "total_return": sum(returns),
                "avg_return": np.mean(returns),
                "periods": len(returns)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/analyze/model")
async def analyze_model():
    try:
        dataset_result = data_processor.prepare_qlib_dataset()
        if not dataset_result["success"]:
            raise HTTPException(status_code=400, detail=dataset_result["error"])
        
        pred_label_df = dataset_result["pred_label_data"]
        
        
        import plotly.graph_objects as go
        
        ic_values = []
        dates = pred_label_df.index.get_level_values('datetime').unique()
        for date in dates:
            date_data = pred_label_df[pred_label_df.index.get_level_values('datetime') == date]
            if len(date_data) > 1:
                ic = np.corrcoef(date_data['score'], date_data['label'])[0, 1]
                ic_values.append(ic if not np.isnan(ic) else 0)
            else:
                ic_values.append(0)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(ic_values))),
            y=ic_values,
            mode='lines+markers',
            name='Information Coefficient'
        ))
        fig.update_layout(
            title='Model Information Coefficient Over Time',
            xaxis_title='Time Period',
            yaxis_title='IC Value'
        )
        
        figures = [fig]
        
        figure_json = [fig.to_json() for fig in figures]
        
        return {
            "success": True,
            "analysis_type": "model",
            "figures": figure_json,
            "summary": {
                "data_points": len(pred_label_df),
                "instruments": len(pred_label_df.index.get_level_values('instrument').unique()),
                "date_range": f"{pred_label_df.index.get_level_values('datetime').min()} to {pred_label_df.index.get_level_values('datetime').max()}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/analyze/all")
async def analyze_all():
    try:
        portfolio_result = await analyze_portfolio()
        model_result = await analyze_model()
        
        return {
            "success": True,
            "portfolio_analysis": portfolio_result,
            "model_analysis": model_result,
            "data_summary": data_processor.get_data_summary()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis error: {str(e)}")

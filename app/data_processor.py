import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import io


class QLibDataProcessor:
    def __init__(self):
        self.data_storage = {}
        self.is_initialized = True
                
    def process_trade_data(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            
            if 'DateTime' in df.columns and 'PnL' in df.columns and 'Instrument' in df.columns:
                df = df.rename(columns={
                    'DateTime': 'datetime',
                    'Instrument': 'instrument', 
                    'PnL': 'return'
                })
                df = df[['instrument', 'datetime', 'return']]
            else:
                required_columns = ['instrument', 'datetime', 'return']
                if not all(col in df.columns for col in required_columns):
                    return {
                        "success": False, 
                        "error": f"Missing required columns. Expected: {required_columns} or DateTime,Instrument,PnL format. Got: {list(df.columns)}"
                    }
            
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            
            df = df.dropna(subset=['datetime'])
            
            if len(df) == 0:
                return {"success": False, "error": "No valid data rows after date parsing"}
            
            df = df.set_index(['instrument', 'datetime'])
            
            self.data_storage['trade_data'] = df
            
            return {
                "success": True,
                "message": f"Successfully processed {len(df)} trade records",
                "columns": list(df.columns),
                "date_range": f"{df.index.get_level_values('datetime').min()} to {df.index.get_level_values('datetime').max()}",
                "instruments": df.index.get_level_values('instrument').unique().tolist()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_price_data(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            
            if 'dates' in df.columns and 'Open' in df.columns:
                df = df.rename(columns={
                    'dates': 'datetime',
                    'Open': 'open',
                    'High': 'high', 
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                })
                if 'instrument' not in df.columns:
                    df['instrument'] = 'DEFAULT'
            else:
                required_columns = ['instrument', 'datetime', 'open', 'high', 'low', 'close', 'volume']
                if not all(col in df.columns for col in required_columns):
                    return {
                        "success": False,
                        "error": f"Missing required columns. Expected: {required_columns} or dates,Open,High,Low,Close,Volume format. Got: {list(df.columns)}"
                    }
            
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            
            df = df.dropna(subset=['datetime'])
            
            if len(df) == 0:
                return {"success": False, "error": "No valid data rows after date parsing"}
            
            df = df.set_index(['instrument', 'datetime'])
            
            self.data_storage['price_data'] = df
            
            return {
                "success": True,
                "message": f"Successfully processed {len(df)} price records",
                "columns": list(df.columns),
                "date_range": f"{df.index.get_level_values('datetime').min()} to {df.index.get_level_values('datetime').max()}",
                "instruments": df.index.get_level_values('instrument').unique().tolist()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_data_summary(self) -> Dict[str, Any]:
        summary = {
            "trade_data_available": "trade_data" in self.data_storage,
            "price_data_available": "price_data" in self.data_storage,
            "qlib_initialized": self.is_initialized
        }
        
        if "trade_data" in self.data_storage:
            trade_df = self.data_storage["trade_data"]
            summary["trade_data_info"] = {
                "records": len(trade_df),
                "instruments": len(trade_df.index.get_level_values('instrument').unique()),
                "date_range": f"{trade_df.index.get_level_values('datetime').min()} to {trade_df.index.get_level_values('datetime').max()}"
            }
            
        if "price_data" in self.data_storage:
            price_df = self.data_storage["price_data"]
            summary["price_data_info"] = {
                "records": len(price_df),
                "instruments": len(price_df.index.get_level_values('instrument').unique()),
                "date_range": f"{price_df.index.get_level_values('datetime').min()} to {price_df.index.get_level_values('datetime').max()}"
            }
            
        return summary
    
    def prepare_analysis_dataset(self) -> Optional[Dict[str, Any]]:
        if "trade_data" not in self.data_storage:
            return {"success": False, "error": "No trade data available"}
            
        try:
            trade_df = self.data_storage["trade_data"]
            
            dates = trade_df.index.get_level_values('datetime').unique()
            instruments = trade_df.index.get_level_values('instrument').unique()
            
            analysis_data = []
            for date in dates:
                for instrument in instruments:
                    if (instrument, date) in trade_df.index:
                        return_val = trade_df.loc[(instrument, date), 'return']
                        analysis_data.append({
                            'datetime': date,
                            'instrument': instrument,
                            'return': return_val,
                            'score': np.random.randn()
                        })
            
            analysis_df = pd.DataFrame(analysis_data)
            analysis_df = analysis_df.set_index(['instrument', 'datetime'])
            
            return {
                "success": True,
                "analysis_data": analysis_df,
                "message": "Dataset prepared for analysis"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

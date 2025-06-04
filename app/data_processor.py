import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import io
import qlib
from qlib.data.dataset.handler import DataHandlerLP
from qlib.data.dataset.loader import QlibDataLoader
from qlib.data.dataset.processor import ZScoreNorm, Fillna
from qlib.contrib.data.handler import Alpha158


class QLibDataProcessor:
    def __init__(self):
        self.data_storage = {}
        self.is_initialized = False
        
    def initialize_qlib(self):
        if not self.is_initialized:
            try:
                qlib.init()
                self.is_initialized = True
            except Exception as e:
                print(f"QLib initialization failed: {e}")
                
    def process_trade_data(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            
            required_columns = ['instrument', 'datetime', 'return']
            if not all(col in df.columns for col in required_columns):
                return {
                    "success": False, 
                    "error": f"Missing required columns. Expected: {required_columns}, Got: {list(df.columns)}"
                }
            
            df['datetime'] = pd.to_datetime(df['datetime'])
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
            
            required_columns = ['instrument', 'datetime', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                return {
                    "success": False,
                    "error": f"Missing required columns. Expected: {required_columns}, Got: {list(df.columns)}"
                }
            
            df['datetime'] = pd.to_datetime(df['datetime'])
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
    
    def prepare_qlib_dataset(self) -> Optional[Dict[str, Any]]:
        if "trade_data" not in self.data_storage:
            return {"success": False, "error": "No trade data available"}
            
        try:
            self.initialize_qlib()
            
            trade_df = self.data_storage["trade_data"]
            
            dates = trade_df.index.get_level_values('datetime').unique()
            instruments = trade_df.index.get_level_values('instrument').unique()
            
            pred_label_data = []
            for date in dates:
                for instrument in instruments:
                    if (instrument, date) in trade_df.index:
                        return_val = trade_df.loc[(instrument, date), 'return']
                        pred_label_data.append({
                            'datetime': date,
                            'instrument': instrument,
                            'label': return_val,
                            'score': np.random.randn()
                        })
            
            pred_label_df = pd.DataFrame(pred_label_data)
            pred_label_df = pred_label_df.set_index(['instrument', 'datetime'])
            
            return {
                "success": True,
                "pred_label_data": pred_label_df,
                "message": "Dataset prepared for QLib analysis"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

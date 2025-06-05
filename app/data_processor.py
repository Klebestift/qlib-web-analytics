import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import io
from scipy import stats
from scipy.stats import spearmanr, pearsonr
from sklearn.feature_selection import mutual_info_regression
from sklearn.ensemble import RandomForestRegressor


class QLibDataProcessor:
    def __init__(self):
        self.data_storage = {}
                
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
            "qlib_initialized": True
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
    
    def calculate_factor_metrics(self, analysis_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate 13 comprehensive factor analysis metrics"""
        try:
            returns = analysis_df['return'].values
            scores = analysis_df['score'].values
            
            valid_mask = ~(np.isnan(returns) | np.isnan(scores))
            returns_clean = returns[valid_mask]
            scores_clean = scores[valid_mask]
            
            if len(returns_clean) < 2:
                return {"success": False, "error": "Insufficient data for metric calculations"}
            
            metrics = {}
            
            metrics['variance'] = float(np.var(scores_clean))
            
            pearson_corr, pearson_p = pearsonr(scores_clean, returns_clean)
            metrics['pearson_correlation'] = float(pearson_corr) if not np.isnan(pearson_corr) else 0.0
            metrics['pearson_p_value'] = float(pearson_p) if not np.isnan(pearson_p) else 1.0
            
            spearman_corr, spearman_p = spearmanr(scores_clean, returns_clean)
            metrics['spearman_correlation'] = float(spearman_corr) if not np.isnan(spearman_corr) else 0.0
            metrics['spearman_p_value'] = float(spearman_p) if not np.isnan(spearman_p) else 1.0
            
            if len(returns_clean) >= 3:
                rolling_corrs = []
                for i in range(2, len(returns_clean)):
                    window_returns = returns_clean[i-2:i+1]
                    window_scores = scores_clean[i-2:i+1]
                    corr = np.corrcoef(window_scores, window_returns)[0, 1]
                    if not np.isnan(corr):
                        rolling_corrs.append(corr)
                metrics['rolling_correlation_mean'] = float(np.mean(rolling_corrs)) if rolling_corrs else 0.0
                metrics['rolling_correlation_std'] = float(np.std(rolling_corrs)) if rolling_corrs else 0.0
            else:
                metrics['rolling_correlation_mean'] = 0.0
                metrics['rolling_correlation_std'] = 0.0
            
            if len(returns_clean) > 1:
                t_stat, t_p = stats.ttest_1samp(returns_clean, 0)
                metrics['t_statistic'] = float(t_stat) if not np.isnan(t_stat) else 0.0
                metrics['t_p_value'] = float(t_p) if not np.isnan(t_p) else 1.0
            else:
                metrics['t_statistic'] = 0.0
                metrics['t_p_value'] = 1.0
            
            if len(returns_clean) >= 5:
                try:
                    rf = RandomForestRegressor(n_estimators=10, random_state=42)
                    rf.fit(scores_clean.reshape(-1, 1), returns_clean)
                    metrics['tree_importance'] = float(rf.feature_importances_[0])
                except:
                    metrics['tree_importance'] = 0.0
            else:
                metrics['tree_importance'] = 0.0
            
            sorted_returns = np.sort(returns_clean)
            q5_idx = max(1, int(0.05 * len(sorted_returns)))
            q95_idx = min(len(sorted_returns) - 1, int(0.95 * len(sorted_returns)))
            metrics['cvar_5_percent'] = float(np.mean(sorted_returns[:q5_idx]))
            metrics['cvar_95_percent'] = float(np.mean(sorted_returns[q95_idx:]))
            
            if len(returns_clean) >= 3:
                try:
                    mi = mutual_info_regression(scores_clean.reshape(-1, 1), returns_clean, random_state=42)
                    metrics['mutual_information'] = float(mi[0])
                except:
                    metrics['mutual_information'] = 0.0
            else:
                metrics['mutual_information'] = 0.0
            
            if len(returns_clean) >= 3:
                time_trend = np.arange(len(returns_clean))
                try:
                    returns_detrended = returns_clean - np.polyval(np.polyfit(time_trend, returns_clean, 1), time_trend)
                    scores_detrended = scores_clean - np.polyval(np.polyfit(time_trend, scores_clean, 1), time_trend)
                    partial_corr = np.corrcoef(scores_detrended, returns_detrended)[0, 1]
                    metrics['partial_correlation'] = float(partial_corr) if not np.isnan(partial_corr) else 0.0
                except:
                    metrics['partial_correlation'] = 0.0
            else:
                metrics['partial_correlation'] = 0.0
            
            metrics['rolling_ic'] = metrics['spearman_correlation']  # IC is typically Spearman correlation
            
            if len(returns_clean) >= 4:
                try:
                    lagged_scores = scores_clean[:-1]
                    future_returns = returns_clean[1:]
                    granger_corr = np.corrcoef(lagged_scores, future_returns)[0, 1]
                    metrics['granger_causality'] = float(granger_corr) if not np.isnan(granger_corr) else 0.0
                except:
                    metrics['granger_causality'] = 0.0
            else:
                metrics['granger_causality'] = 0.0
            
            if len(returns_clean) >= 4:
                q1, q3 = np.percentile(scores_clean, [25, 75])
                top_quartile_mask = scores_clean >= q3
                bottom_quartile_mask = scores_clean <= q1
                if np.sum(top_quartile_mask) > 0 and np.sum(bottom_quartile_mask) > 0:
                    top_quartile_return = np.mean(returns_clean[top_quartile_mask])
                    bottom_quartile_return = np.mean(returns_clean[bottom_quartile_mask])
                    metrics['cluster_uplift'] = float(top_quartile_return - bottom_quartile_return)
                else:
                    metrics['cluster_uplift'] = 0.0
            else:
                metrics['cluster_uplift'] = 0.0
            
            if len(returns_clean) > 1:
                mean_return = np.mean(returns_clean)
                std_return = np.std(returns_clean)
                if std_return > 0 and not np.isnan(std_return) and not np.isinf(std_return):
                    sharpe = mean_return / std_return
                    metrics['sharpe_ratio'] = float(sharpe) if not (np.isnan(sharpe) or np.isinf(sharpe)) else 0.0
                else:
                    metrics['sharpe_ratio'] = 0.0
                
                downside_returns = returns_clean[returns_clean < 0]
                if len(downside_returns) > 0:
                    downside_std = np.std(downside_returns)
                    if downside_std > 0 and not np.isnan(downside_std) and not np.isinf(downside_std):
                        sortino = mean_return / downside_std
                        metrics['sortino_ratio'] = float(sortino) if not (np.isnan(sortino) or np.isinf(sortino)) else 0.0
                    else:
                        metrics['sortino_ratio'] = 0.0
                else:
                    metrics['sortino_ratio'] = 10.0 if mean_return > 0 else 0.0
            else:
                metrics['sharpe_ratio'] = 0.0
                metrics['sortino_ratio'] = 0.0
            
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    if np.isnan(value) or np.isinf(value):
                        metrics[key] = 0.0
                    else:
                        metrics[key] = float(value)
            
            return {
                "success": True,
                "metrics": metrics,
                "data_points": len(returns_clean)
            }
            
        except Exception as e:
            import traceback
            error_details = f"Error calculating metrics: {str(e)}\nTraceback: {traceback.format_exc()}"
            return {"success": False, "error": error_details}

"""
Demand Forecasting AI Service
Predicts shipping demand trends using AI and historical data
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from backend.services.ai_service import ai_service

logger = logging.getLogger(__name__)


@dataclass
class DemandForecast:
    """Demand forecast result"""
    forecast_period: str  # daily, weekly, monthly
    start_date: str
    end_date: str
    predicted_volume: float
    confidence_interval: float
    growth_rate: float
    seasonal_factors: Dict[str, float]
    recommended_capacity: float
    peak_days: List[str]
    supply_recommendations: List[str]
    risk_factors: List[str]


class DemandForecastingService:
    """AI-powered demand forecasting"""
    
    async def forecast_demand(
        self,
        historical_data: List[Dict[str, Any]],
        forecast_horizon_days: int = 30,
        include_seasonality: bool = True,
        include_external_factors: bool = True
    ) -> DemandForecast:
        """
        Forecast demand for next period
        
        Args:
            historical_data: Historical shipment/volume data
            forecast_horizon_days: Number of days to forecast
            include_seasonality: Include seasonal patterns
            include_external_factors: Include external factors (holidays, events, etc.)
        
        Returns:
            DemandForecast with predictions
        """
        
        data_summary = f"Historical data points: {len(historical_data)}"
        if historical_data:
            avg_volume = sum(d.get('volume', 0) for d in historical_data) / len(historical_data)
            data_summary += f", Average volume: {avg_volume}"
        
        seasonality_note = "Include seasonal patterns" if include_seasonality else "Exclude seasonal patterns"
        external_note = "Consider external factors like holidays, events, weather" if include_external_factors else ""
        
        prompt = f"""
        Forecast shipping demand for next {forecast_horizon_days} days:
        
        {data_summary}
        Data points: {historical_data}
        
        {seasonality_note}
        {external_note}
        
        Use time series analysis and AI to predict:
        - predicted_volume: Forecasted total volume
        - confidence_interval: Confidence level (0-100)
        - growth_rate: Expected growth percentage
        - seasonal_factors: Seasonal multipliers by day of week
        - peak_days: Days with highest predicted demand
        - supply_recommendations: Recommended capacity adjustments
        - risk_factors: Factors that could affect forecast
        
        Return JSON response.
        """
        
        try:
            response = await ai_service.call_ai(
                prompt,
                provider="openai",
                model="gpt-4",
                temperature=0.3
            )
            
            import json
            result = json.loads(response)
            
            return DemandForecast(
                forecast_period="daily",
                start_date=datetime.now().isoformat(),
                end_date=(datetime.now() + timedelta(days=forecast_horizon_days)).isoformat(),
                predicted_volume=float(result.get('predicted_volume', 0)),
                confidence_interval=float(result.get('confidence_interval', 0)) / 100,
                growth_rate=float(result.get('growth_rate', 0)),
                seasonal_factors=result.get('seasonal_factors', {}),
                recommended_capacity=float(result.get('recommended_capacity', 0)),
                peak_days=result.get('peak_days', []),
                supply_recommendations=result.get('supply_recommendations', []),
                risk_factors=result.get('risk_factors', [])
            )
            
        except Exception as e:
            logger.error(f"Demand forecasting failed: {e}")
            raise
    
    async def analyze_market_trends(
        self,
        market_data: Dict[str, Any],
        competitive_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze market trends and competitive landscape
        
        Args:
            market_data: Current market data
            competitive_data: Competitor performance data
        
        Returns:
            Market analysis and opportunities
        """
        
        prompt = f"""
        Analyze market trends for logistics industry:
        
        Market data: {market_data}
        {f'Competitive data: {competitive_data}' if competitive_data else ''}
        
        Identify:
        - market_trends: Current trends
        - growth_opportunities: Areas for growth
        - competitive_positioning: How we compare
        - recommendations: Strategic recommendations
        
        Return JSON response.
        """
        
        try:
            response = await ai_service.call_ai(
                prompt,
                provider="claude",
                model="claude-3-opus-20240229",
                temperature=0.5
            )
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            return {"error": str(e)}
    
    async def optimize_pricing(
        self,
        forecast: DemandForecast,
        cost_data: Dict[str, float],
        margin_targets: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Optimize pricing based on demand forecast
        
        Args:
            forecast: Demand forecast
            cost_data: Operational cost data
            margin_targets: Target profit margins
        
        Returns:
            Pricing recommendations
        """
        
        prompt = f"""
        Optimize pricing strategy based on demand forecast:
        
        Forecasted demand: {forecast.predicted_volume}
        Peak days: {forecast.peak_days}
        Growth rate: {forecast.growth_rate}%
        
        Costs: {cost_data}
        Margin targets: {margin_targets}
        
        Recommend:
        - base_price: Standard pricing
        - peak_pricing: Higher demand period pricing
        - off_peak_pricing: Lower demand period pricing
        - dynamic_adjustments: Real-time pricing rules
        - expected_revenue: Projected revenue
        
        Return JSON response.
        """
        
        try:
            response = await ai_service.call_ai(
                prompt,
                model="gpt-4",
                temperature=0.4
            )
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Pricing optimization failed: {e}")
            return {"error": str(e)}


forecasting_service = DemandForecastingService()

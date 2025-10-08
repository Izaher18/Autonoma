"""Data analyst agent for data processing and analysis."""

import logging
from typing import Dict, Any, List
import json

from core.base_agent import BaseAgent
from core.tool_registry import tool

logger = logging.getLogger(__name__)


class DataAnalystAgent(BaseAgent):
    """Agent specialized in data analysis and insights."""
    
    def __init__(self, name: str = "DataAnalyst"):
        """Initialize the data analyst agent.
        
        Args:
            name: Name of the agent
        """
        system_prompt = """You are a data analyst specialized in processing, analyzing, and visualizing data.

Your capabilities include:
1. Data cleaning and preprocessing
2. Statistical analysis
3. Pattern recognition
4. Generating insights and recommendations
5. Creating data visualizations

Always provide clear, actionable insights based on data."""
        
        super().__init__(name=name, system_prompt=system_prompt)
    
    @tool(description="Analyze dataset statistics")
    def analyze_statistics(self, data: List[float]) -> Dict[str, Any]:
        """Calculate basic statistics for a dataset.
        
        Args:
            data: List of numeric values
            
        Returns:
            Statistical analysis
        """
        logger.info("Calculating statistics")
        
        if not data:
            return {"error": "Empty dataset"}
        
        sorted_data = sorted(data)
        n = len(data)
        
        stats = {
            "count": n,
            "mean": sum(data) / n,
            "min": min(data),
            "max": max(data),
            "median": sorted_data[n // 2] if n % 2 != 0 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2,
            "range": max(data) - min(data)
        }
        
        # Calculate standard deviation
        mean = stats["mean"]
        variance = sum((x - mean) ** 2 for x in data) / n
        stats["std_dev"] = variance ** 0.5
        
        return stats
    
    @tool(description="Identify trends in data")
    def identify_trends(self, data: List[float]) -> Dict[str, Any]:
        """Identify trends in time series data.
        
        Args:
            data: List of numeric values
            
        Returns:
            Trend analysis
        """
        logger.info("Identifying trends")
        
        if len(data) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Simple trend detection
        increases = sum(1 for i in range(1, len(data)) if data[i] > data[i-1])
        decreases = sum(1 for i in range(1, len(data)) if data[i] < data[i-1])
        
        if increases > decreases * 1.5:
            trend = "upward"
        elif decreases > increases * 1.5:
            trend = "downward"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "increases": increases,
            "decreases": decreases,
            "stability": decreases / increases if increases > 0 else 0
        }
    
    @tool(description="Generate data insights")
    def generate_insights(self, analysis: Dict[str, Any]) -> str:
        """Generate insights from analysis results.
        
        Args:
            analysis: Analysis results
            
        Returns:
            Generated insights
        """
        logger.info("Generating insights")
        
        insights = f"""Data Insights:

Key Findings:
{json.dumps(analysis, indent=2)}

Recommendations:
1. Monitor key metrics regularly
2. Investigate outliers or anomalies
3. Consider seasonal patterns
4. Track changes over time
5. Compare with benchmarks

Next Steps:
- Collect more data for deeper analysis
- Validate findings with stakeholders
- Implement recommended actions
"""
        return insights
    
    @tool(description="Clean and preprocess data")
    def clean_data(self, data: List[Any]) -> Dict[str, Any]:
        """Clean and preprocess data.
        
        Args:
            data: Raw data
            
        Returns:
            Cleaned data and report
        """
        logger.info("Cleaning data")
        
        original_count = len(data)
        
        # Remove None values
        cleaned = [x for x in data if x is not None]
        
        # Remove duplicates
        seen = set()
        unique_data = []
        for item in cleaned:
            if item not in seen:
                seen.add(item)
                unique_data.append(item)
        
        return {
            "original_count": original_count,
            "cleaned_count": len(cleaned),
            "unique_count": len(unique_data),
            "removed_nulls": original_count - len(cleaned),
            "removed_duplicates": len(cleaned) - len(unique_data),
            "cleaned_data": unique_data
        }
    
    async def process(self, user_input: str) -> str:
        """Process data analysis request.
        
        Args:
            user_input: User's request
            
        Returns:
            Analysis results
        """
        self.add_message("user", user_input)
        
        try:
            # Sample data for demonstration
            sample_data = [10, 15, 13, 17, 20, 25, 23, 28, 30, 35]
            
            # Perform analysis workflow
            stats = self.call_tool("analyze_statistics", {"data": sample_data})
            trends = self.call_tool("identify_trends", {"data": sample_data})
            
            combined_analysis = {**stats, **trends}
            insights = self.call_tool("generate_insights", {"analysis": combined_analysis})
            
            response = f"""Data Analysis Results:

Dataset: {sample_data}

Statistical Analysis:
{json.dumps(stats, indent=2)}

Trend Analysis:
{json.dumps(trends, indent=2)}

{insights}
"""
            
            self.add_message("assistant", response)
            return response
            
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            logger.error(error_msg)
            return error_msg

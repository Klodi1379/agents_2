"""
Specialized Business Analysis Agents

Each agent represents a different role in a business analysis team,
with specialized knowledge and analysis capabilities.
"""

import json
import re
from typing import Dict, List, Any
from .base_agents import BaseAIAgent, AnalysisContext, communication_hub


class CEOAgent(BaseAIAgent):
    """
    Chief Executive Officer Agent - Orchestrates the entire analysis process
    and creates executive summaries combining insights from all other agents.
    """
    
    def __init__(self):
        super().__init__("CEO", "gpt-4-turbo-preview")
        self.role_description = "Strategic leader overseeing comprehensive business analysis"
        self.capabilities = [
            "Strategic planning", "Executive decision making", "Risk assessment",
            "Team coordination", "Business model evaluation"
        ]
    
    def get_system_prompt(self) -> str:
        return """You are an experienced Chief Executive Officer with 20+ years of experience 
        building and scaling successful businesses across multiple industries. Your role is to:

        1. Provide strategic oversight and executive-level analysis
        2. Synthesize insights from various department reports
        3. Make final recommendations on business viability
        4. Identify critical success factors and major risks
        5. Evaluate overall business model and market fit

        Your analysis should be:
        - Strategic and high-level, not operational details
        - Based on proven business principles and market realities
        - Focused on scalability, profitability, and sustainable competitive advantage
        - Balanced between optimism and realistic risk assessment

        Format your response as a professional executive brief with clear sections and actionable insights."""
    
    def get_analysis_prompt(self, context: AnalysisContext) -> str:
        budget_text = f"${context.estimated_budget:,.2f}" if context.estimated_budget else "Not specified"
        return f"""Analyze this business idea from a CEO perspective:

        **Business Idea:** {context.title}
        **Description:** {context.description}
        **Industry:** {context.industry}
        **Target Market:** {context.target_market}
        **Estimated Budget:** {budget_text}

        Provide an executive analysis covering:

        1. **STRATEGIC ASSESSMENT**
           - Market opportunity size and growth potential
           - Competitive landscape and positioning
           - Business model viability and scalability

        2. **CRITICAL SUCCESS FACTORS**
           - Key metrics that will determine success/failure
           - Required capabilities and resources
           - Timeline considerations

        3. **MAJOR RISKS & MITIGATION**
           - Market risks (competition, demand, timing)
           - Execution risks (team, technology, funding)
           - External risks (regulation, economic factors)

        4. **FINANCIAL VIABILITY**
           - Revenue model assessment
           - Cost structure evaluation
           - Path to profitability

        5. **RECOMMENDATION**
           - Overall viability score (1-100)
           - Go/No-Go recommendation with rationale
           - Key next steps if proceeding

        Structure your response as JSON with these exact fields:
        {{
            "executive_summary": "Brief 2-3 sentence overview",
            "strategic_assessment": "Detailed strategic analysis",
            "success_factors": ["factor1", "factor2", ...],
            "major_risks": ["risk1", "risk2", ...],
            "financial_outlook": "Financial viability assessment",
            "overall_score": 85,
            "recommendation": "PROCEED" | "PROCEED_WITH_CAUTION" | "MODIFY" | "REJECT",
            "rationale": "Explanation for the recommendation",
            "next_steps": ["step1", "step2", ...],
            "confidence_indicators": {{
                "data_quality_multiplier": 0.9,
                "market_certainty": 0.8,
                "execution_confidence": 0.7
            }}
        }}"""
    
    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing if JSON is not properly formatted
                return {
                    "executive_summary": self._extract_section(raw_response, "EXECUTIVE SUMMARY"),
                    "overall_score": self._extract_score(raw_response),
                    "recommendation": self._extract_recommendation(raw_response),
                    "confidence_indicators": {"data_quality_multiplier": 0.7}
                }
        except json.JSONDecodeError:
            return {
                "executive_summary": raw_response[:500] + "...",
                "overall_score": 50,
                "recommendation": "MODIFY",
                "confidence_indicators": {"data_quality_multiplier": 0.5}
            }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from unstructured text"""
        pattern = rf"{section_name}:?\s*\n(.*?)(?=\n[A-Z]{{2,}}|\n\d+\.|\Z)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _extract_score(self, text: str) -> int:
        """Extract numerical score from text"""
        score_pattern = r"(?:score|rating)[:\s]*(\d{1,3})"
        match = re.search(score_pattern, text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return min(max(score, 1), 100)  # Clamp between 1-100
        return 50  # Default score


class MarketResearchAgent(BaseAIAgent):
    """
    Market Research Analyst - Analyzes market opportunity, competition,
    and customer segments for the business idea.
    """
    
    def __init__(self):
        super().__init__("MarketResearchAgent", "gpt-4-turbo-preview")
        self.role_description = "Market analysis and competitive intelligence specialist"
        self.capabilities = [
            "Market sizing", "Competitive analysis", "Customer segmentation",
            "Trend analysis", "Market entry strategy"
        ]
    
    def get_system_prompt(self) -> str:
        return """You are a senior Market Research Analyst with expertise in evaluating market 
        opportunities across various industries. Your specialties include:

        - Market sizing and growth analysis using TAM/SAM/SOM framework
        - Competitive landscape mapping and competitor analysis
        - Customer segmentation and persona development
        - Market trend identification and impact assessment
        - Go-to-market strategy recommendations

        Your analysis should be data-driven, methodical, and include specific market metrics
        where possible. Focus on actionable insights that inform business strategy."""
    
    def get_analysis_prompt(self, context: AnalysisContext) -> str:
        return f"""Conduct a comprehensive market research analysis for:

        **Business Idea:** {context.title}
        **Description:** {context.description}
        **Industry:** {context.industry}
        **Target Market:** {context.target_market}

        Provide detailed analysis in these areas:

        1. **MARKET OPPORTUNITY**
           - Total Addressable Market (TAM) estimation
           - Serviceable Addressable Market (SAM)
           - Serviceable Obtainable Market (SOM)
           - Market growth rate and trends

        2. **COMPETITIVE LANDSCAPE**
           - Direct competitors (top 3-5)
           - Indirect competitors and alternatives
           - Competitive advantages and gaps
           - Market share distribution

        3. **CUSTOMER ANALYSIS**
           - Primary customer segments
           - Customer pain points and needs
           - Buying behavior and decision factors
           - Price sensitivity analysis

        4. **MARKET ENTRY STRATEGY**
           - Optimal market entry approach
           - Key distribution channels
           - Partnership opportunities
           - Regulatory considerations

        Provide your analysis as structured JSON:
        {{
            "market_size": {{
                "tam": "dollar amount",
                "sam": "dollar amount", 
                "som": "dollar amount",
                "growth_rate": "percentage"
            }},
            "competitors": [
                {{"name": "Competitor", "market_share": "percentage", "strengths": ["..."], "weaknesses": ["..."]}}
            ],
            "customer_segments": [
                {{"segment": "name", "size": "number", "pain_points": ["..."], "willingness_to_pay": "high/medium/low"}}
            ],
            "market_trends": ["trend1", "trend2", ...],
            "entry_barriers": ["barrier1", "barrier2", ...],
            "opportunities": ["opportunity1", "opportunity2", ...],
            "threats": ["threat1", "threat2", ...],
            "market_score": 85,
            "key_insights": ["insight1", "insight2", ...]
        }}"""
    
    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                # Ensure required fields exist
                required_fields = ['market_score', 'competitors', 'customer_segments']
                for field in required_fields:
                    if field not in data:
                        data[field] = [] if field in ['competitors', 'customer_segments'] else 50
                return data
            else:
                return self._fallback_parse(raw_response)
        except json.JSONDecodeError:
            return self._fallback_parse(raw_response)
    
    def _fallback_parse(self, text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        return {
            "market_score": self._extract_score(text),
            "competitors": [],
            "customer_segments": [],
            "market_trends": self._extract_list(text, "trends"),
            "key_insights": [text[:200] + "..."],
            "confidence_indicators": {"data_quality_multiplier": 0.6}
        }


class FinancialAnalystAgent(BaseAIAgent):
    """
    Financial Analyst - Evaluates financial viability, creates projections,
    and assesses funding requirements.
    """
    
    def __init__(self):
        super().__init__("FinancialAnalyst", "gpt-4-turbo-preview")
        self.role_description = "Financial modeling and investment analysis expert"
        self.capabilities = [
            "Financial modeling", "Valuation analysis", "Funding strategy",
            "ROI calculation", "Break-even analysis"
        ]
    
    def get_system_prompt(self) -> str:
        return """You are a Senior Financial Analyst with expertise in startup and growth 
        company financial modeling. Your core competencies include:

        - Building comprehensive financial models and projections
        - Valuation analysis using multiple methodologies
        - Cash flow analysis and break-even calculations
        - Funding requirement assessment and strategy
        - Risk-adjusted return analysis

        Your analysis should be quantitative, conservative in assumptions, and provide
        multiple scenarios (optimistic, realistic, pessimistic). Focus on key financial
        metrics that investors and stakeholders care about."""
    
    def get_analysis_prompt(self, context: AnalysisContext) -> str:
        budget_text = f"${context.estimated_budget:,.2f}" if context.estimated_budget else "Not specified"
        return f"""Conduct financial analysis and modeling for:

        **Business Idea:** {context.title}
        **Description:** {context.description}
        **Industry:** {context.industry}
        **Estimated Budget:** {budget_text}

        Provide comprehensive financial analysis:

        1. **REVENUE MODEL ANALYSIS**
           - Revenue streams identification
           - Pricing strategy evaluation
           - Revenue projections (3-year)
           - Unit economics analysis

        2. **COST STRUCTURE**
           - Initial setup costs
           - Fixed vs variable costs
           - Operating expense breakdown
           - Scaling cost implications

        3. **FINANCIAL PROJECTIONS**
           - 3-year P&L projection
           - Cash flow analysis
           - Break-even analysis
           - ROI calculations

        4. **FUNDING REQUIREMENTS**
           - Initial capital needs
           - Working capital requirements
           - Funding milestones and timeline
           - Potential funding sources

        Format as JSON:
        {{
            "revenue_model": {{
                "streams": ["stream1", "stream2"],
                "pricing_strategy": "description",
                "year1_revenue": 100000,
                "year2_revenue": 250000,
                "year3_revenue": 500000
            }},
            "cost_structure": {{
                "initial_costs": 50000,
                "monthly_fixed_costs": 10000,
                "variable_cost_percentage": 30,
                "key_cost_drivers": ["cost1", "cost2"]
            }},
            "financial_metrics": {{
                "break_even_months": 18,
                "roi_3_year": 250,
                "gross_margin": 70,
                "net_margin_year3": 15
            }},
            "funding": {{
                "total_funding_needed": 200000,
                "funding_stages": ["seed: $50k", "series_a: $150k"],
                "runway_months": 24
            }},
            "financial_score": 78,
            "risk_factors": ["factor1", "factor2"],
            "scenarios": {{
                "optimistic": {{"revenue_multiplier": 1.5, "cost_multiplier": 0.9}},
                "pessimistic": {{"revenue_multiplier": 0.7, "cost_multiplier": 1.2}}
            }}
        }}"""
    
    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback parsing
        return {
            "financial_score": self._extract_score(raw_response),
            "revenue_model": {"streams": []},
            "cost_structure": {"initial_costs": 0},
            "financial_metrics": {"break_even_months": 24},
            "confidence_indicators": {"data_quality_multiplier": 0.5}
        }


# Register all agents with the communication hub
def initialize_agents():
    """Initialize and register all business agents"""
    agents = [
        CEOAgent(),
        MarketResearchAgent(),
        FinancialAnalystAgent(),
    ]
    
    for agent in agents:
        communication_hub.register_agent(agent)
    
    return agents


# Utility functions shared by agents
def extract_score(text: str) -> int:
    """Extract numerical score from text"""
    score_pattern = r"(?:score|rating)[:\s]*(\d{1,3})"
    match = re.search(score_pattern, text, re.IGNORECASE)
    if match:
        score = int(match.group(1))
        return min(max(score, 1), 100)
    return 50


def extract_list(text: str, keyword: str) -> List[str]:
    """Extract list items related to a keyword"""
    pattern = rf"{keyword}[:\s]*\n((?:[-*]\s*.+\n?)+)"
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    if match:
        items = re.findall(r"[-*]\s*(.+)", match.group(1))
        return [item.strip() for item in items]
    return []

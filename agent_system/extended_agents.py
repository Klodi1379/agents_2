"""
Additional Specialized Business Analysis Agents

This module contains more specialized agents for comprehensive business analysis.
"""

import json
import re
from typing import Dict, List, Any
from .base_agents import BaseAIAgent, AnalysisContext, communication_hub


class TechnicalLeadAgent(BaseAIAgent):
    """
    Technical Lead Agent - Evaluates technical feasibility, architecture,
    and implementation requirements for the business idea.
    """
    
    def __init__(self):
        super().__init__("TechnicalLead", "gpt-4-turbo-preview")
        self.role_description = "Technical architecture and feasibility expert"
        self.capabilities = [
            "Technical feasibility analysis", "Architecture design", 
            "Technology stack evaluation", "Development timeline estimation",
            "Scalability assessment"
        ]
    
    def get_system_prompt(self) -> str:
        return """You are a Senior Technical Lead with 15+ years of experience in software 
        architecture, system design, and technology implementation across various industries. 
        Your expertise includes:

        - Technical feasibility assessment and risk analysis
        - System architecture design and scalability planning
        - Technology stack selection and evaluation
        - Development timeline and resource estimation
        - Integration challenges and solution design

        Your analysis should be technically sound, realistic about implementation 
        challenges, and focused on practical solutions. Consider both current 
        technology capabilities and emerging trends."""
    
    def get_analysis_prompt(self, context: AnalysisContext) -> str:
        budget_text = f"${context.estimated_budget:,.2f}" if context.estimated_budget else "Not specified"
        return f"""Conduct a comprehensive technical analysis for:

        **Business Idea:** {context.title}
        **Description:** {context.description}
        **Industry:** {context.industry}
        **Estimated Budget:** {budget_text}

        Provide detailed technical evaluation:

        1. **TECHNICAL FEASIBILITY**
           - Core technical requirements analysis
           - Implementation complexity assessment
           - Technical risks and challenges
           - Alternative technical approaches

        2. **SYSTEM ARCHITECTURE**
           - Recommended system architecture
           - Technology stack suggestions
           - Integration requirements
           - Scalability considerations

        3. **DEVELOPMENT ESTIMATION**
           - Development phases and milestones
           - Resource requirements (team size, skills)
           - Timeline estimation (MVP to full product)
           - Infrastructure and operational needs

        4. **TECHNOLOGY ASSESSMENT**
           - Required technologies and frameworks
           - Third-party integrations needed
           - Security and compliance requirements
           - Performance and reliability factors

        Format as JSON:
        {{
            "technical_feasibility": {{
                "complexity_level": "LOW/MEDIUM/HIGH",
                "implementation_risk": "LOW/MEDIUM/HIGH",
                "technical_challenges": ["challenge1", "challenge2", ...],
                "feasibility_score": 85
            }},
            "recommended_architecture": {{
                "architecture_type": "description",
                "core_technologies": ["tech1", "tech2", ...],
                "infrastructure_needs": ["need1", "need2", ...],
                "integration_points": ["integration1", "integration2", ...]
            }},
            "development_plan": {{
                "mvp_timeline_months": 6,
                "full_product_timeline_months": 12,
                "team_size": 5,
                "required_skills": ["skill1", "skill2", ...],
                "development_phases": ["phase1", "phase2", ...]
            }},
            "technical_requirements": {{
                "performance_requirements": ["req1", "req2", ...],
                "security_requirements": ["req1", "req2", ...],
                "compliance_needs": ["need1", "need2", ...],
                "scalability_targets": "description"
            }},
            "cost_estimates": {{
                "development_cost_range": "50k-100k",
                "infrastructure_monthly_cost": "500-2000",
                "third_party_services_cost": "100-500"
            }},
            "technical_score": 78,
            "recommendations": ["rec1", "rec2", ...],
            "potential_roadblocks": ["roadblock1", "roadblock2", ...]
        }}"""
    
    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        return {
            "technical_score": self._extract_score(raw_response),
            "technical_feasibility": {"feasibility_score": 50},
            "confidence_indicators": {"data_quality_multiplier": 0.6}
        }


class RiskAnalystAgent(BaseAIAgent):
    """
    Risk Analyst Agent - Identifies and evaluates potential risks
    across all business dimensions.
    """
    
    def __init__(self):
        super().__init__("RiskAnalyst", "gpt-4-turbo-preview")
        self.role_description = "Comprehensive business risk assessment specialist"
        self.capabilities = [
            "Risk identification", "Risk quantification", "Mitigation planning",
            "Scenario analysis", "Regulatory compliance assessment"
        ]
    
    def get_system_prompt(self) -> str:
        return """You are a Senior Risk Analyst with expertise in identifying, 
        quantifying, and mitigating business risks across multiple industries. 
        Your core competencies include:

        - Comprehensive risk identification across all business dimensions
        - Quantitative and qualitative risk assessment methodologies
        - Risk mitigation strategy development
        - Regulatory and compliance risk evaluation
        - Scenario planning and stress testing

        Your analysis should be thorough, conservative where appropriate, and 
        include actionable mitigation strategies for identified risks."""
    
    def get_analysis_prompt(self, context: AnalysisContext) -> str:
        return f"""Conduct comprehensive risk analysis for:

        **Business Idea:** {context.title}
        **Description:** {context.description}
        **Industry:** {context.industry}
        **Target Market:** {context.target_market}

        Analyze risks across all dimensions:

        1. **MARKET RISKS**
           - Demand uncertainty and market timing
           - Competitive threats and market saturation
           - Customer acquisition and retention risks
           - Market size and growth assumptions

        2. **OPERATIONAL RISKS**
           - Execution and delivery risks
           - Key person dependencies
           - Supply chain and vendor risks
           - Quality and reputation risks

        3. **FINANCIAL RISKS**
           - Funding and cash flow risks
           - Revenue model viability
           - Cost overrun risks
           - Economic sensitivity analysis

        4. **REGULATORY & LEGAL RISKS**
           - Compliance requirements and changes
           - Intellectual property risks
           - Data privacy and security regulations
           - Licensing and permit requirements

        5. **TECHNOLOGY RISKS**
           - Technical implementation risks
           - Cybersecurity and data risks
           - Technology obsolescence
           - Integration and scalability risks

        Format as JSON:
        {{
            "risk_assessment": {{
                "overall_risk_level": "LOW/MEDIUM/HIGH",
                "risk_score": 65,
                "confidence_level": 0.8
            }},
            "risk_categories": {{
                "market_risks": [
                    {{"risk": "description", "probability": 0.3, "impact": "HIGH", "severity_score": 7}}
                ],
                "operational_risks": [
                    {{"risk": "description", "probability": 0.4, "impact": "MEDIUM", "severity_score": 5}}
                ],
                "financial_risks": [
                    {{"risk": "description", "probability": 0.2, "impact": "HIGH", "severity_score": 8}}
                ],
                "regulatory_risks": [
                    {{"risk": "description", "probability": 0.1, "impact": "MEDIUM", "severity_score": 4}}
                ],
                "technology_risks": [
                    {{"risk": "description", "probability": 0.3, "impact": "MEDIUM", "severity_score": 6}}
                ]
            }},
            "mitigation_strategies": {{
                "immediate_actions": ["action1", "action2", ...],
                "medium_term_plans": ["plan1", "plan2", ...],
                "contingency_plans": ["plan1", "plan2", ...]
            }},
            "scenario_analysis": {{
                "best_case": {{"probability": 0.2, "description": "...", "risk_score": 30}},
                "most_likely": {{"probability": 0.6, "description": "...", "risk_score": 65}},
                "worst_case": {{"probability": 0.2, "description": "...", "risk_score": 90}}
            }},
            "critical_success_factors": ["factor1", "factor2", ...],
            "red_flags": ["flag1", "flag2", ...],
            "monitoring_indicators": ["indicator1", "indicator2", ...]
        }}"""
    
    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        return {
            "risk_score": self._extract_score(raw_response),
            "risk_assessment": {"overall_risk_level": "MEDIUM"},
            "confidence_indicators": {"data_quality_multiplier": 0.7}
        }


class MarketingStrategistAgent(BaseAIAgent):
    """
    Marketing Strategist Agent - Develops comprehensive marketing
    and customer acquisition strategies.
    """
    
    def __init__(self):
        super().__init__("MarketingStrategist", "gpt-4-turbo-preview")
        self.role_description = "Marketing strategy and customer acquisition expert"
        self.capabilities = [
            "Marketing strategy development", "Customer acquisition planning",
            "Brand positioning", "Channel strategy", "Digital marketing optimization"
        ]
    
    def get_system_prompt(self) -> str:
        return """You are a Senior Marketing Strategist with expertise in developing 
        comprehensive marketing strategies for businesses across various industries. 
        Your specializations include:

        - Marketing strategy development and brand positioning
        - Customer acquisition and retention strategy
        - Multi-channel marketing campaign design
        - Digital marketing and growth hacking techniques
        - Market segmentation and targeting

        Your analysis should be practical, data-driven, and focused on measurable 
        outcomes with clear ROI projections."""
    
    def get_analysis_prompt(self, context: AnalysisContext) -> str:
        budget_text = f"${context.estimated_budget:,.2f}" if context.estimated_budget else "Not specified"
        return f"""Develop comprehensive marketing strategy for:

        **Business Idea:** {context.title}
        **Description:** {context.description}
        **Industry:** {context.industry}
        **Target Market:** {context.target_market}
        **Budget:** {budget_text}

        Create detailed marketing analysis:

        1. **BRAND POSITIONING & MESSAGING**
           - Unique value proposition
           - Brand positioning strategy
           - Key messaging framework
           - Competitive differentiation

        2. **TARGET AUDIENCE STRATEGY**
           - Primary and secondary target segments
           - Customer personas and journey mapping
           - Pain points and messaging alignment
           - Behavioral and demographic insights

        3. **MARKETING CHANNELS & TACTICS**
           - Recommended marketing channels
           - Channel-specific strategies
           - Content marketing approach
           - Digital and traditional mix

        4. **CUSTOMER ACQUISITION PLAN**
           - Acquisition funnel design
           - Customer acquisition cost (CAC) estimates
           - Lifetime value (LTV) projections
           - Conversion optimization strategy

        5. **BUDGET ALLOCATION & ROI**
           - Marketing budget recommendations
           - Channel budget allocation
           - Expected ROI by channel
           - Key performance indicators (KPIs)

        Format as JSON:
        {{
            "brand_strategy": {{
                "value_proposition": "clear statement",
                "positioning": "positioning statement",
                "key_messages": ["message1", "message2", ...],
                "brand_personality": ["trait1", "trait2", ...]
            }},
            "target_segments": [
                {{
                    "segment_name": "Primary Segment",
                    "size": "market size",
                    "characteristics": ["char1", "char2", ...],
                    "pain_points": ["pain1", "pain2", ...],
                    "preferred_channels": ["channel1", "channel2", ...]
                }}
            ],
            "marketing_channels": {{
                "digital_channels": [
                    {{"channel": "Social Media", "strategy": "...", "budget_allocation": 25, "expected_roi": 300}}
                ],
                "traditional_channels": [
                    {{"channel": "Print", "strategy": "...", "budget_allocation": 10, "expected_roi": 150}}
                ],
                "emerging_channels": [
                    {{"channel": "Influencer", "strategy": "...", "budget_allocation": 15, "expected_roi": 250}}
                ]
            }},
            "acquisition_metrics": {{
                "estimated_cac": 50,
                "projected_ltv": 300,
                "ltv_cac_ratio": 6,
                "payback_period_months": 8
            }},
            "marketing_budget": {{
                "total_budget_needed": 100000,
                "monthly_budget": 8333,
                "channel_allocation": {{"digital": 60, "traditional": 25, "events": 15}},
                "expected_customers_year1": 1000
            }},
            "marketing_score": 82,
            "success_metrics": ["metric1", "metric2", ...],
            "potential_challenges": ["challenge1", "challenge2", ...],
            "recommendations": ["rec1", "rec2", ...]
        }}"""
    
    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        return {
            "marketing_score": self._extract_score(raw_response),
            "brand_strategy": {"value_proposition": ""},
            "confidence_indicators": {"data_quality_multiplier": 0.6}
        }


class IdeaGeneratorAgent(BaseAIAgent):
    """
    Idea Generator Agent - Generates new business ideas based on
    specified criteria and market analysis.
    """
    
    def __init__(self):
        super().__init__("IdeaGenerator", "gpt-4-turbo-preview")
        self.role_description = "Creative business idea generation specialist"
        self.capabilities = [
            "Business idea generation", "Market opportunity identification",
            "Trend analysis", "Innovation framework application", "Ideation facilitation"
        ]
    
    def get_system_prompt(self) -> str:
        return """You are a Creative Business Strategist specialized in generating 
        innovative business ideas based on market trends, technological capabilities, 
        and emerging opportunities. Your expertise includes:

        - Systematic idea generation using proven frameworks
        - Market gap identification and opportunity analysis
        - Trend synthesis and future scenario planning
        - Innovation methodology application
        - Cross-industry insight application

        Generate practical, viable business ideas that address real market needs 
        and have clear paths to implementation and profitability."""
    
    def get_analysis_prompt(self, context: AnalysisContext) -> str:
        # For idea generation, we use the additional_data to get generation criteria
        criteria = context.additional_data
        
        return f"""Generate innovative business ideas based on these criteria:

        **Industry Focus:** {criteria.get('industry_focus', 'Any')}
        **Budget Range:** {criteria.get('budget_range', 'Not specified')}
        **Target Audience:** {criteria.get('target_audience', 'General')}
        **Innovation Level:** {criteria.get('innovation_level', 'Medium')}
        **Geographic Focus:** {criteria.get('geographic_focus', 'Global')}
        **Technology Preferences:** {criteria.get('technology_preferences', 'None specified')}
        **Avoid Sectors:** {criteria.get('avoid_sectors', 'None')}

        Generate 5-10 unique business ideas that meet these criteria:

        For each idea, provide:
        1. **BUSINESS CONCEPT**
           - Clear, compelling business idea title
           - Detailed description (2-3 paragraphs)
           - Target customer and market
           - Core value proposition

        2. **BUSINESS MODEL**
           - Revenue model and pricing strategy
           - Key resources and partnerships
           - Distribution channels
           - Cost structure overview

        3. **MARKET OPPORTUNITY**
           - Market size and growth potential
           - Competitive landscape assessment
           - Unique differentiators
           - Market entry strategy

        4. **IMPLEMENTATION OVERVIEW**
           - Key milestones and timeline
           - Resource requirements
           - Initial funding needs
           - Risk factors and mitigation

        Format as JSON:
        {{
            "generated_ideas": [
                {{
                    "title": "Business Idea Title",
                    "description": "Detailed description...",
                    "industry": "Technology",
                    "target_market": "Small businesses",
                    "value_proposition": "Clear value prop",
                    "business_model": {{
                        "revenue_streams": ["stream1", "stream2"],
                        "pricing_model": "subscription",
                        "key_resources": ["resource1", "resource2"],
                        "distribution_channels": ["channel1", "channel2"]
                    }},
                    "market_opportunity": {{
                        "market_size": "$50M",
                        "growth_rate": "15% annually",
                        "competition_level": "Medium",
                        "differentiators": ["diff1", "diff2"]
                    }},
                    "implementation": {{
                        "initial_investment": "$25,000",
                        "time_to_market": "6 months",
                        "key_milestones": ["milestone1", "milestone2"],
                        "major_risks": ["risk1", "risk2"]
                    }},
                    "viability_score": 78,
                    "innovation_level": "Medium",
                    "feasibility_rating": "High"
                }}
            ],
            "generation_summary": {{
                "total_ideas_generated": 8,
                "criteria_match_score": 85,
                "average_viability_score": 74,
                "innovation_distribution": {{"low": 2, "medium": 4, "high": 2}}
            }},
            "market_insights": ["insight1", "insight2", ...],
            "emerging_trends": ["trend1", "trend2", ...],
            "recommendations": ["rec1", "rec2", ...]
        }}"""
    
    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        return {
            "generated_ideas": [],
            "generation_summary": {"total_ideas_generated": 0},
            "confidence_indicators": {"data_quality_multiplier": 0.5}
        }


# Update the initialization function to include new agents
def initialize_all_agents():
    """Initialize and register all business agents including new ones"""
    agents = [
        CEOAgent(),
        MarketResearchAgent(), 
        FinancialAnalystAgent(),
        TechnicalLeadAgent(),
        RiskAnalystAgent(),
        MarketingStrategistAgent(),
        IdeaGeneratorAgent(),
    ]
    
    for agent in agents:
        communication_hub.register_agent(agent)
    
    return agents


# Import the base agents to make them available
from .business_agents import CEOAgent, MarketResearchAgent, FinancialAnalystAgent

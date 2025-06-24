"""
Celery Tasks for AI Agent Orchestration

This module contains the background tasks that coordinate the AI agents
to perform comprehensive business analysis.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from celery import shared_task, group, chain, chord
from django.utils import timezone
from django.db import transaction

from analysis_engine.models import (
    BusinessIdea, AgentReport, FinalAnalysisReport, 
    AnalysisTask, IdeaGenerationRequest
)
from agent_system.base_agents import AnalysisContext, communication_hub
from agent_system.business_agents import initialize_agents

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def orchestrate_business_analysis(self, business_idea_id: str):
    """
    Main orchestration task that coordinates all agents to analyze a business idea.
    This is the "CEO" of our task system.
    """
    try:
        # Get the business idea
        business_idea = BusinessIdea.objects.get(id=business_idea_id)
        business_idea.status = 'ANALYZING'
        business_idea.save()
        
        logger.info(f"Starting analysis orchestration for: {business_idea.title}")
        
        # Create analysis context
        context = AnalysisContext(
            business_idea_id=str(business_idea.id),
            title=business_idea.title,
            description=business_idea.description,
            industry=business_idea.industry,
            target_market=business_idea.target_market or "",
            estimated_budget=float(business_idea.estimated_budget) if business_idea.estimated_budget else None,
            additional_data={}
        )
        
        # Create parallel tasks for each agent type
        agent_tasks = group([
            analyze_with_agent.s(business_idea_id, 'MARKET_RESEARCH', context.__dict__),
            analyze_with_agent.s(business_idea_id, 'FINANCIAL', context.__dict__),
            analyze_with_agent.s(business_idea_id, 'MARKETING', context.__dict__),
            analyze_with_agent.s(business_idea_id, 'TECH_LEAD', context.__dict__),
            analyze_with_agent.s(business_idea_id, 'RISK_ANALYST', context.__dict__),
        ])
        
        # Chain: run all agent analyses, then create final report
        analysis_workflow = chord(agent_tasks)(
            create_final_analysis_report.s(business_idea_id)
        )
        
        # Track the workflow
        AnalysisTask.objects.create(
            business_idea=business_idea,
            task_id=analysis_workflow.id,
            agent_type='',  # This is the orchestrator
            status='STARTED'
        )
        
        logger.info(f"Analysis workflow {analysis_workflow.id} started for {business_idea.title}")
        return f"Analysis orchestration started for {business_idea.title}"
        
    except BusinessIdea.DoesNotExist:
        logger.error(f"Business idea {business_idea_id} not found")
        raise
    except Exception as e:
        logger.error(f"Failed to orchestrate analysis for {business_idea_id}: {str(e)}")
        if business_idea_id:
            try:
                business_idea = BusinessIdea.objects.get(id=business_idea_id)
                business_idea.status = 'FAILED'
                business_idea.save()
            except:
                pass
        raise self.retry(countdown=60, exc=e)


@shared_task(bind=True, max_retries=2)
def analyze_with_agent(self, business_idea_id: str, agent_type: str, context_dict: Dict[str, Any]):
    """
    Task that runs analysis with a specific agent type.
    """
    try:
        logger.info(f"Starting {agent_type} analysis for {business_idea_id}")
        
        # Get business idea and create/update agent report
        business_idea = BusinessIdea.objects.get(id=business_idea_id)
        
        agent_report, created = AgentReport.objects.get_or_create(
            business_idea=business_idea,
            agent_type=agent_type,
            defaults={'status': 'IN_PROGRESS'}
        )
        
        if not created:
            agent_report.status = 'IN_PROGRESS'
            agent_report.save()
        
        # Track the task
        AnalysisTask.objects.create(
            business_idea=business_idea,
            task_id=self.request.id,
            agent_type=agent_type,
            status='STARTED'
        )
        
        # Initialize agents if not already done
        initialize_agents()
        
        # Create analysis context
        context = AnalysisContext(**context_dict)
        
        # Get the appropriate agent
        agent = _get_agent_by_type(agent_type)
        if not agent:
            raise ValueError(f"No agent found for type: {agent_type}")
        
        # Run the analysis (this is async, so we need to handle it properly)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(agent.analyze(context))
        finally:
            loop.close()
        
        # Update the agent report with results
        if result.success:
            agent_report.report_content = result.content
            agent_report.structured_data = result.structured_data
            agent_report.agent_score = result.structured_data.get('score', 
                                      result.structured_data.get('market_score',
                                      result.structured_data.get('financial_score', 50)))
            agent_report.confidence = result.confidence
            agent_report.llm_model_used = result.model_used
            agent_report.token_usage = result.token_usage
            agent_report.status = 'COMPLETED'
            
            # Calculate cost estimate (rough estimation)
            agent_report.cost_estimate = _estimate_cost(result.model_used, result.token_usage)
            
        else:
            agent_report.status = 'FAILED'
            agent_report.error_message = result.error_message
        
        agent_report.execution_time = timedelta(seconds=result.execution_time)
        agent_report.save()
        
        # Update task status
        AnalysisTask.objects.filter(task_id=self.request.id).update(
            status='SUCCESS' if result.success else 'FAILURE',
            completed_at=timezone.now()
        )
        
        logger.info(f"Completed {agent_type} analysis for {business_idea_id}")
        return {
            'agent_type': agent_type,
            'success': result.success,
            'score': agent_report.agent_score,
            'report_id': str(agent_report.id)
        }
        
    except Exception as e:
        logger.error(f"Failed {agent_type} analysis for {business_idea_id}: {str(e)}")
        
        # Update agent report status
        try:
            agent_report = AgentReport.objects.get(
                business_idea_id=business_idea_id,
                agent_type=agent_type
            )
            agent_report.status = 'FAILED'
            agent_report.error_message = str(e)
            agent_report.save()
        except:
            pass
        
        # Update task status
        AnalysisTask.objects.filter(task_id=self.request.id).update(
            status='FAILURE',
            error_message=str(e),
            completed_at=timezone.now()
        )
        
        raise self.retry(countdown=30, exc=e)


@shared_task(bind=True)
def create_final_analysis_report(self, agent_results: List[Dict], business_idea_id: str):
    """
    Creates the final comprehensive analysis report by combining all agent reports.
    This is executed after all individual agent analyses are complete.
    """
    try:
        logger.info(f"Creating final analysis report for {business_idea_id}")
        
        business_idea = BusinessIdea.objects.get(id=business_idea_id)
        
        # Get all completed agent reports
        agent_reports = AgentReport.objects.filter(
            business_idea=business_idea,
            status='COMPLETED'
        )
        
        if agent_reports.count() == 0:
            raise ValueError("No completed agent reports found")
        
        # Initialize agents to get CEO agent
        initialize_agents()
        ceo_agent = communication_hub.agents.get('CEO')
        
        if not ceo_agent:
            raise ValueError("CEO agent not available")
        
        # Prepare context with all agent insights
        context = AnalysisContext(
            business_idea_id=str(business_idea.id),
            title=business_idea.title,
            description=business_idea.description,
            industry=business_idea.industry,
            target_market=business_idea.target_market or "",
            estimated_budget=float(business_idea.estimated_budget) if business_idea.estimated_budget else None,
            additional_data={
                'agent_reports': [
                    {
                        'agent_type': report.agent_type,
                        'content': report.report_content,
                        'structured_data': report.structured_data,
                        'score': report.agent_score
                    }
                    for report in agent_reports
                ]
            }
        )
        
        # Generate final summary using CEO agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(ceo_agent.analyze(context))
        finally:
            loop.close()
        
        if not result.success:
            raise ValueError(f"CEO analysis failed: {result.error_message}")
        
        # Extract structured data
        structured_data = result.structured_data
        
        # Create or update final analysis report
        final_report, created = FinalAnalysisReport.objects.get_or_create(
            business_idea=business_idea,
            defaults={
                'executive_summary': structured_data.get('executive_summary', ''),
                'key_findings': structured_data.get('success_factors', []),
                'recommendations': structured_data.get('next_steps', []),
                'overall_score': structured_data.get('overall_score', 50),
                'final_recommendation': _map_recommendation(structured_data.get('recommendation', 'MODIFY')),
                'confidence_level': str(result.confidence),
                'generated_by_agent': 'CEO',
                'total_cost': sum(float(r.cost_estimate or 0) for r in agent_reports)
            }
        )
        
        if not created:
            # Update existing report
            final_report.executive_summary = structured_data.get('executive_summary', '')
            final_report.key_findings = structured_data.get('success_factors', [])
            final_report.recommendations = structured_data.get('next_steps', [])
            final_report.overall_score = structured_data.get('overall_score', 50)
            final_report.final_recommendation = _map_recommendation(structured_data.get('recommendation', 'MODIFY'))
            final_report.confidence_level = str(result.confidence)
            final_report.save()
        
        # Update business idea with final results
        business_idea.status = 'COMPLETED'
        business_idea.overall_score = final_report.overall_score
        business_idea.recommendation = final_report.final_recommendation
        business_idea.confidence_level = final_report.confidence_level
        business_idea.save()
        
        logger.info(f"Final analysis report created for {business_idea.title}")
        
        return {
            'business_idea_id': business_idea_id,
            'overall_score': final_report.overall_score,
            'recommendation': final_report.final_recommendation,
            'report_id': str(final_report.id)
        }
        
    except Exception as e:
        logger.error(f"Failed to create final analysis report for {business_idea_id}: {str(e)}")
        
        # Mark business idea as failed
        try:
            business_idea = BusinessIdea.objects.get(id=business_idea_id)
            business_idea.status = 'FAILED'
            business_idea.save()
        except:
            pass
        
        raise


@shared_task
def generate_business_ideas(request_id: str):
    """
    Task to generate new business ideas based on specified criteria.
    """
    try:
        generation_request = IdeaGenerationRequest.objects.get(id=request_id)
        generation_request.status = 'GENERATING'
        generation_request.save()
        
        # TODO: Implement idea generation agent
        # This would use a specialized agent to generate business ideas
        # based on the criteria in the generation_request
        
        logger.info(f"Business idea generation completed for request {request_id}")
        
    except Exception as e:
        logger.error(f"Failed to generate business ideas for request {request_id}: {str(e)}")
        raise


def _get_agent_by_type(agent_type: str):
    """Get agent instance by type"""
    agent_mapping = {
        'MARKET_RESEARCH': 'MarketResearchAgent',
        'FINANCIAL': 'FinancialAnalyst',
        'CEO': 'CEO',
        # Add more mappings as needed
    }
    
    agent_name = agent_mapping.get(agent_type)
    if agent_name:
        return communication_hub.agents.get(agent_name)
    return None


def _estimate_cost(model_name: str, token_usage: int) -> float:
    """Estimate cost based on model and token usage"""
    # Rough cost estimates (update with actual pricing)
    cost_per_token = {
        'gpt-4-turbo-preview': 0.00003,
        'gpt-4': 0.00006,
        'gpt-3.5-turbo': 0.000002,
        'claude-3-sonnet': 0.000015,
        'claude-3-opus': 0.000075,
    }
    
    rate = cost_per_token.get(model_name, 0.00003)
    return token_usage * rate


def _map_recommendation(recommendation: str) -> str:
    """Map agent recommendation to model choices"""
    mapping = {
        'PROCEED': 'PROCEED',
        'PROCEED_WITH_CAUTION': 'PROCEED_CAUTION',
        'MODIFY': 'MODIFY',
        'REJECT': 'REJECT',
        'DELAY': 'DELAY'
    }
    return mapping.get(recommendation, 'MODIFY')

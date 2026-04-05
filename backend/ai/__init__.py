"""
AI Module — updated for function-based query_parser and insight_generator
"""

from .query_parser import parse_query
from .insight_generator import generate_insight
from .predictor import OceanPredictor

__all__ = ['parse_query', 'generate_insight', 'OceanPredictor']

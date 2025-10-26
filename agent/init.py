"""Agents package for simplified trading system."""

from .market_analyst_v2 import create_market_analyst
from .fundamentals_analyst_v2 import create_fundamentals_analyst
from .bull_debater_v2 import create_bull_debater
from .bear_debater_v2 import create_bear_debater
from .supervisor_v2 import create_supervisor

__all__ = [
    'create_market_analyst',
    'create_fundamentals_analyst',
    'create_bull_debater',
    'create_bear_debater',
    'create_supervisor'
]
"""
Unit test configuration and mocking setup.

Mocks all external dependencies to allow unit tests to run in isolation.
This file is loaded BEFORE test modules, so mocks are in place early.
"""

import sys
from unittest.mock import MagicMock

# Mock external dependencies
sys.modules['llm'] = MagicMock()
sys.modules['events'] = MagicMock()
sys.modules['tools'] = MagicMock()
sys.modules['tools.pdf'] = MagicMock()
sys.modules['heading_detector'] = MagicMock()
sys.modules['prompts'] = MagicMock()
sys.modules['prompts.function_summarizer_prompt'] = MagicMock()

# Mock agent modules
sys.modules['agents.extractor_agent'] = MagicMock()
sys.modules['agents.validator_agent'] = MagicMock()
sys.modules['agents.corrector_agent'] = MagicMock()
sys.modules['agents.text_summarizer'] = MagicMock()
sys.modules['agents.function_summarizer_agent'] = MagicMock()
sys.modules['agents.gap_analysis_tools'] = MagicMock()

# Import real models module and make it available as 'models' for relative imports
import src.models
sys.modules['models'] = src.models

# Import real agents.schemas and make it available
import src.agents.schemas
sys.modules['agents.schemas'] = src.agents.schemas

# Import real agents.nist_gap_agents and make it available
import src.agents.nist_gap_agents
sys.modules['agents.nist_gap_agents'] = src.agents.nist_gap_agents


import sys
import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.utils.log import logger

load_dotenv()

project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)


def get_model_for_provider(model_name: str):
   
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    logger.info(f"Initializing Gemini model {model_name} with API key")
    return Gemini(
        id=model_name,
        api_key=api_key  
    )


def get_chess_teams(
    white_model: str = "gemini-2.0-pro-exp-02-05",
    black_model: str = "gemini-2.0-pro-exp-02-05",
    master_model: str = "gemini-2.0-pro-exp-02-05",
    debug_mode: bool = True,
) -> Dict[str, Agent]:
    """
    Returns a dictionary of chess agents with specific roles.

    Args:
        white_model: Gemini model to use for white player
        black_model: Gemini model to use for black player
        master_model: Gemini model to use for game master
        debug_mode: Enable logging and debug features

    Returns:
        Dictionary of configured agents
    """
    try:
        # Create model instances (using different models for each agent)
        white_model_instance = get_model_for_provider(white_model)
        black_model_instance = get_model_for_provider(black_model)
        master_model_instance = get_model_for_provider(master_model)

        # Create agents
        white_piece_agent = Agent(
            name="white_piece_agent",
            description="""You are a chess strategist for white pieces. Given a list of legal moves,
                    analyze them and choose the best one based on standard chess strategy.
                    Consider piece development, center control, and king safety.
                    Respond ONLY with your chosen move in UCI notation (e.g., 'e2e4').""",
            model=white_model_instance,
            debug_mode=debug_mode,
        )

        black_piece_agent = Agent(
            name="black_piece_agent",
            description="""You are a chess strategist for black pieces. Given a list of legal moves,
                    analyze them and choose the best one based on standard chess strategy.
                    Consider piece development, center control, and king safety.
                    Respond ONLY with your chosen move in UCI notation (e.g., 'e7e5').""",
            model=black_model_instance,
            debug_mode=debug_mode,
        )

        master_agent = Agent(
            name="master_agent",
            description="""You are a chess master overseeing the game. Your responsibilities:
                    1. Analyze the current board state to determine if the game has ended
                    2. Check for checkmate, stalemate, draw by repetition, or insufficient material
                    3. Provide commentary on the current state of the game
                    4. Evaluate the position and suggest who has an advantage
                    
                    Respond with a JSON object containing:
                    {
                        "game_over": true/false,
                        "result": "white_win"/"black_win"/"draw"/null,
                        "reason": "explanation if game is over",
                        "commentary": "brief analysis of the position",
                        "advantage": "white"/"black"/"equal"
                    }""",
            model=master_model_instance,
            debug_mode=debug_mode,
        )

        return {
            "white_piece_agent": white_piece_agent,
            "black_piece_agent": black_piece_agent,
            "master_agent": master_agent,
        }
    except Exception as e:
        logger.error(f"Error initializing agents: {str(e)}")
        raise
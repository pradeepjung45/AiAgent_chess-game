import os
from dotenv import load_dotenv
import logging
from typing import Dict, List
import sys

# Load environment variables
load_dotenv()

# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import chess
import nest_asyncio
import streamlit as st
from agents import get_chess_teams
from agno.utils.log import logger

from utils import (
    CUSTOM_CSS,
    WHITE,
    BLACK,
    ChessBoard,
    display_board,
    display_move_history,
    parse_move,
    show_agent_status,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

nest_asyncio.apply()

# Page configuration
st.set_page_config(
    page_title="Chess Team Battle",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS with dark mode support
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_legal_moves_with_descriptions(board: ChessBoard) -> List[Dict]:
    """
    Get all legal moves with descriptions for the current player.

    Args:
        board: ChessBoard instance

    Returns:
        List of dictionaries with move information
    """
    legal_moves = []

    # Get python-chess board
    chess_board = board.board

    # Get all legal moves
    for move in chess_board.legal_moves:
        # Get source and destination squares
        from_square = chess.square_name(move.from_square)
        to_square = chess.square_name(move.to_square)

        # Get piece type
        piece = chess_board.piece_at(move.from_square)
        piece_type = piece.symbol().upper() if piece else "?"

        # Check if it's a capture
        is_capture = chess_board.is_capture(move)

        # Check if it's a promotion
        promotion = None
        if move.promotion:
            promotion = chess.piece_name(move.promotion)

        # Check if it's a castling move
        is_kingside_castle = chess_board.is_kingside_castling(move)
        is_queenside_castle = chess_board.is_queenside_castling(move)

        # Create move description
        if is_kingside_castle:
            description = "Kingside castle (O-O)"
        elif is_queenside_castle:
            description = "Queenside castle (O-O-O)"
        elif promotion:
            description = f"Pawn {from_square} to {to_square}, promote to {promotion}"
        elif is_capture:
            captured_piece = chess_board.piece_at(move.to_square)
            captured_type = captured_piece.symbol().upper() if captured_piece else "?"
            description = f"{piece_type} from {from_square} captures {captured_type} at {to_square}"
        else:
            description = f"{piece_type} from {from_square} to {to_square}"

        # Add move to list
        legal_moves.append(
            {
                "uci": move.uci(),
                "san": chess_board.san(move),
                "description": description,
                "is_capture": is_capture,
                "is_castle": is_kingside_castle or is_queenside_castle,
                "promotion": promotion,
            }
        )

    return legal_moves


def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Google API Key not found! Please check your .env file.")
        return

    ####################################################################
    # App header
    ####################################################################
    st.markdown(
        "<h1 class='main-title'>Chess Team Battle</h1>",
        unsafe_allow_html=True,
    )

    ####################################################################
    # Initialize session state
    ####################################################################
    if "game_started" not in st.session_state:
        st.session_state.game_started = False
        st.session_state.game_paused = False
        st.session_state.move_history = []

    with st.sidebar:
        st.markdown("### Game Controls")
        model_options = {
            "gemini-flash": "gemini-2.0-flash",
            "gemini-pro": "gemini-2.0-pro-exp-02-05",
        }
        ################################################################
        # Model selection
        ################################################################
        st.markdown("#### White Player")
        selected_white = st.selectbox(
            "Select White Player",
            list(model_options.keys()),
            index=0,
            key="model_white",
        )

        st.markdown("#### Black Player")
        selected_black = st.selectbox(
            "Select Black Player",
            list(model_options.keys()),
            index=1,
            key="model_black",
        )

        st.markdown("#### Game Master")
        selected_master = st.selectbox(
            "Select Game Master",
            list(model_options.keys()),
            index=0,
            key="model_master",
        )

        ################################################################
        # Game controls
        ################################################################
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.game_started:
                if st.button("▶️ Start Game"):
                    st.session_state.agents = get_chess_teams(
                        white_model=model_options[selected_white],
                        black_model=model_options[selected_black],
                        master_model=model_options[selected_master],
                        debug_mode=True,
                    )
                    st.session_state.game_board = ChessBoard()
                    st.session_state.game_started = True
                    st.session_state.game_paused = False
                    st.session_state.move_history = []
                    st.rerun()
            else:
                game_over, _ = st.session_state.game_board.get_game_state()
                if not game_over:
                    if st.button(
                        "⏸️ Pause" if not st.session_state.game_paused else "▶️ Resume"
                    ):
                        st.session_state.game_paused = not st.session_state.game_paused
                        st.rerun()
        with col2:
            if st.session_state.game_started:
                if st.button("🔄 New Game"):
                    st.session_state.agents = get_chess_teams(
                        white_model=model_options[selected_white],
                        black_model=model_options[selected_black],
                        master_model=model_options[selected_master],
                        debug_mode=True,
                    )
                    st.session_state.game_board = ChessBoard()
                    st.session_state.game_paused = False
                    st.session_state.move_history = []
                    st.rerun()

    ####################################################################
    # Header showing current models
    ####################################################################
    if st.session_state.game_started:
        st.markdown(
            f"<h3 style='color:#87CEEB; text-align:center;'>{selected_white} vs {selected_black}</h3>",
            unsafe_allow_html=True,
        )

    ####################################################################
    # Main game area
    ####################################################################
    if st.session_state.game_started:
        game_over, state_info = st.session_state.game_board.get_game_state()

        display_board(st.session_state.game_board)

        # Show game status (winner/draw/current player)
        if game_over:
            result = state_info.get("result", "")
            reason = state_info.get("reason", "")

            if "white_win" in result:
                st.success(f"🏆 Game Over! White ({selected_white}) wins by {reason}!")
            elif "black_win" in result:
                st.success(f"🏆 Game Over! Black ({selected_black}) wins by {reason}!")
            else:
                st.info(f"🤝 Game Over! It's a draw by {reason}!")
        else:
            # Show current player status
            current_color = st.session_state.game_board.current_color
            current_model_name = (
                selected_white if current_color == WHITE else selected_black
            )

            show_agent_status(
                f"{current_color.capitalize()} Player ({current_model_name})",
                "It's your turn",
                is_white=(current_color == WHITE),
            )

        display_move_history(st.session_state.move_history)

        if not st.session_state.game_paused and not game_over:
            # Thinking indicator
            st.markdown(
                f"""<div class="thinking-container">
                    <div class="agent-thinking">
                        <div style="margin-right: 10px; display: inline-block;">🔄</div>
                        {current_color.capitalize()} Player ({current_model_name}) is thinking...
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

            # Get legal moves using python-chess directly
            legal_moves = get_legal_moves_with_descriptions(st.session_state.game_board)

            # Format legal moves for the agent
            legal_moves_descriptions = "\n".join(
                [
                    f"- {move['san']} ({move['uci']}): {move['description']}"
                    for move in legal_moves
                ]
            )

            # Get board state
            board_state = st.session_state.game_board.get_board_state()
            fen = st.session_state.game_board.get_fen()

            # Get move from current player agent
            current_agent = (
                st.session_state.agents["white_piece_agent"]
                if current_color == WHITE
                else st.session_state.agents["black_piece_agent"]
            )

            kwargs = {"stream": False}
            response = current_agent.run(
                f"""\
Current board state (FEN): {fen}
Board visualization:
{board_state}

Legal moves available:
{legal_moves_descriptions}

Choose your next move from the legal moves above.
Respond with ONLY your chosen move in UCI notation (e.g., 'e2e4').
Do not include any other text in your response.""",
                **kwargs,
            )

            try:
                # Parse the move from the response
                move_str = parse_move(response.content if response else "")

                # Verify the move is in the list of legal moves
                legal_move_ucis = [move["uci"] for move in legal_moves]

                if move_str not in legal_move_ucis:
                    # Try to find a matching move
                    for move in legal_moves:
                        if move["san"].lower() == move_str.lower():
                            move_str = move["uci"]
                            break

                # Make the move
                success, message = st.session_state.game_board.make_move(move_str)

                if success:
                    # Find the move description
                    move_description = next(
                        (
                            move["description"]
                            for move in legal_moves
                            if move["uci"] == move_str
                        ),
                        "",
                    )

                    move_number = len(st.session_state.move_history) + 1
                    st.session_state.move_history.append(
                        {
                            "number": move_number,
                            "player": f"{current_color.capitalize()} ({current_model_name})",
                            "move": move_str,
                            "description": move_description,
                        }
                    )

                    logger.info(
                        f"Move {move_number}: {current_color.capitalize()} ({current_model_name}) played {move_str} - {move_description}"
                    )
                    logger.info(
                        f"Board state:\n{st.session_state.game_board.get_board_state()}"
                    )

                    # Check game state after move
                    game_over, state_info = st.session_state.game_board.get_game_state()

                    # If game is not over, get analysis from master agent
                    if not game_over and move_number % 2 == 0:  # After black's move
                        master_agent = st.session_state.agents["master_agent"]
                        kwargs = {"stream": False}
                        response = master_agent.run(
                            f"""\
Current board state (FEN): {fen}
Board visualization:
{board_state}

Analyze the current position and provide your assessment.
""",
                            **kwargs,
                        )

                    if game_over:
                        result = state_info.get("result", "")
                        reason = state_info.get("reason", "")

                        if "white_win" in result:
                            logger.info(f"Game Over - White wins by {reason}")
                            st.success(
                                f"🏆 Game Over! White ({selected_white}) wins by {reason}!"
                            )
                        elif "black_win" in result:
                            logger.info(f"Game Over - Black wins by {reason}")
                            st.success(
                                f"🏆 Game Over! Black ({selected_black}) wins by {reason}!"
                            )
                        else:
                            logger.info(f"Game Over - Draw by {reason}")
                            st.info(f"🤝 Game Over! It's a draw by {reason}!")

                        st.session_state.game_paused = True

                    st.rerun()
                else:
                    logger.error(f"Invalid move attempt: {message}")
                    response = current_agent.run(
                        f"""\
Invalid move: {message}

Current board state (FEN): {fen}
Board visualization:
{board_state}

Legal moves available:
{legal_moves_descriptions}

Please choose a valid move from the list above.
Respond with ONLY your chosen move in UCI notation (e.g., 'e2e4').
Do not include any other text in your response.""",
                        stream=False,
                    )
                    st.rerun()

            except Exception as e:
                logger.error(f"Error processing move: {str(e)}")
                st.error(f"Error processing move: {str(e)}")
                st.rerun()
    else:
        st.info("👈 Press 'Start Game' to begin!")

    ####################################################################
    # About section
    ####################################################################
    st.sidebar.markdown(f"""
    ### ♟️ Chess Team Battle
    Watch AI agents play chess with specialized roles!

    **Current Teams:**
    * ♔ White: `{selected_white}`
    * ♚ Black: `{selected_black}`
    * 🧠 Game Master: `{selected_master}`

    **How it Works:**
    1. Python-chess validates all legal moves
    2. The White/Black Player agents choose the best move
    3. The Game Master analyzes the position
    4. The process repeats until the game ends
    """)


if __name__ == "__main__":
    main()
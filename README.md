 AI Chess Game with Streamlit

An interactive chess game where you can play against or watch AI agents play against each other, powered by Google's Gemini AI model and Streamlit.

## Features

- Play chess against an AI opponent
- Watch AI agents play against each other
- Interactive chess board interface
- Move validation and game state tracking
- Real-time AI move explanations
- Support for multiple AI agents (Gemini Pro)

## Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)
- Google API key for Gemini Pro

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd chess_game
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the provided URL (typically http://localhost:8501)

3. Choose your game mode:
   - Play against AI
   - Watch AI vs AI match

## Game Controls

- Use the interactive chess board to make moves
- Click on a piece to see valid moves
- The AI's thoughts and move explanations are displayed in real-time
- Game status and move history are shown on the sidebar

## Project Structure

```
chess_game/
├── app.py              # Main Streamlit application
├── agents.py           # AI agent configurations
├── requirements.txt    # Project dependencies
├── .env               # Environment variables
└── .venv/             # Virtual environment
```

## Configuration

You can modify AI behavior and game settings in `agents.py`:
- Adjust AI models (default: gemini-pro)
- Configure thinking time
- Modify AI personality and behavior

## Troubleshooting

1. API Key Issues:
   - Ensure your Google API key is valid
   - Check if the key has the necessary permissions
   - Verify the key is correctly set in `.env`

2. Installation Issues:
   - Make sure virtual environment is activated
   - Update pip: `pip install --upgrade pip`
   - Install dependencies: `pip install -r requirements.txt`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]

## Acknowledgments

- Chess engine powered by Python-chess
- UI built with Streamlit
- AI capabilities provided by Google's Gemini Pro

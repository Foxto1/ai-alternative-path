# AI What If – Terminal

**AI What If** is an interactive terminal application designed to explore hypothetical “what if” scenarios. Users enter questions in a terminal-like interface, and the AI provides concise, structured, and professional responses.

## Key Features

- **AI-powered scenario analysis** for “what if” questions
- **Terminal-style user interface** with full scroll, selection, and command history support
- **Structured responses** adapted to scenario type:
  - History → timeline of events
  - Science / Technology → consequences and implications
  - Society / Culture → changes in daily life
- Command history navigation using Up/Down arrows
- Save conversation history to a file (`Ctrl+S`)
- Copy selected text (`Ctrl+C`)
- Clear terminal using the `cls` command

## Requirements

- Python 3.7 or higher
- Google Gemini API key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Foxto1/ai-alternative-path.git
cd ai-alternative-path
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

Run the application:

```bash
python main.py
```

## Example Questions

- "What if gravity suddenly stopped working?"
- "What if the internet was never invented?"
- "What if dinosaurs never went extinct?"
- "What if humans could photosynthesize like plants?"

## Terminal Commands

- Type your question and press **Enter**
- `cls` – clear the terminal
- Up/Down arrows – navigate command history
- **Ctrl+C** – copy selected text
- **Ctrl+S** – save conversation history

## How It Works

The application uses the Google Gemini AI model to analyze hypothetical scenarios. The AI is prompted to:

1. Identify the scenario type (historical, scientific, social, etc.)
2. Generate concise, professional responses
3. Adjust the format according to the scenario
4. Maintain logical consistency and factual accuracy

## API Key Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## License

This project is licensed under the MIT License – see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome. Please submit a Pull Request to propose changes.

## Acknowledgments

- AI model: Google Gemini
- GUI implemented with tkinter
- Inspired by classic terminal interfaces

## Screenshot

![Terminal app screenshot](screenshots/Example%20Usage.png)



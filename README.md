# The Investment Committee

**A Multi-Agent System (MAS) for Stock Analysis**

The Investment Committee is a sophisticated Python application that simulates a debate between three AI agents to analyze stocks and make investment decisions. Using real-time financial data, the system showcases advanced agent-to-agent protocol design.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER INPUT (Ticker)                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Data Layer (yfinance)│
         │   - Price Data         │
         │   - P/E Ratio          │
         │   - 52-Week High/Low   │
         │   - News Headlines     │
         └───────────┬────────────┘
                     │
         ┌───────────┴────────────┐
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌─────────────────┐
│  🐂 BULL AGENT  │      │  🐻 BEAR AGENT  │
│  (Optimistic)   │      │  (Skeptical)    │
└────────┬────────┘      └────────┬────────┘
         │                        │
         └────────┬───────────────┘
                  │ (Rebuttal Phase)
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
    Bull Rebuttal     Bear Rebuttal
         │                 │
         └────────┬────────┘
                  │
                  ▼
      ┌─────────────────────────┐
      │  ⚖️ PORTFOLIO MANAGER   │
      │  (Final Decision)       │
      │  Output: BUY/SELL/HOLD  │
      └─────────────────────────┘
```

## Features

- **Real-time Financial Data**: Fetches live stock data using `yfinance`
- **Three AI Agents**:
  - **The Bull**: Growth-focused, optimistic investor
  - **The Bear**: Risk-averse, skeptical investor
  - **Portfolio Manager**: Objective decision-maker
- **Debate Protocol**: Agents debate with rebuttals
- **Beautiful Terminal UI**: Powered by `rich` library
- **Flexible LLM Support**: Works with OpenAI or Anthropic
- **Structured Output**: Uses Pydantic for data validation

## Tech Stack

- Python 3.10+
- `yfinance` - Financial data retrieval
- `rich` - Terminal UI
- `openai` / `anthropic` - LLM API clients
- `pydantic` - Data validation
- `python-dotenv` - Environment management

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd InvestmentCommitte
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
# Choose your LLM provider: "openai" or "anthropic"
LLM_PROVIDER=anthropic

# Add your API key (only one is needed)
ANTHROPIC_API_KEY=sk-ant-xxxxx
# OR
OPENAI_API_KEY=sk-xxxxx

# Optional: Customize models
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4-turbo-preview
```

## Usage

### Basic Usage

```bash
python main.py
```

The application will:
1. Prompt you for a stock ticker (e.g., "NVDA", "AAPL", "TSLA")
2. Fetch real-time financial data
3. Run the Bull and Bear agents in parallel
4. Execute a rebuttal phase where agents counter each other
5. Have the Portfolio Manager make a final decision
6. Display everything in a beautiful terminal dashboard

### Example Session

```
Enter stock ticker (or 'quit' to exit): NVDA

🔍 Analyzing NVDA...

┌─────────────────────────────────────┐
│   Financial Data: NVDA              │
├──────────────────┬──────────────────┤
│ Current Price    │ $875.45          │
│ P/E Ratio        │ 71.23            │
│ 52-Week High     │ $974.00          │
│ 52-Week Low      │ $108.13          │
└──────────────────┴──────────────────┘

📡 Phase 1: Initial Analysis (Parallel)
🟢 Bull Agent analyzing...
🔴 Bear Agent analyzing...

🔄 REBUTTAL PHASE
🟢 Bull countering Bear's thesis...
🔴 Bear countering Bull's thesis...

📊 THE DEBATE
╔═══════════════════════════╦═══════════════════════════╗
║   🐂 THE BULL THESIS      ║   🐻 THE BEAR THESIS      ║
║                           ║                           ║
║ NVIDIA is the leader...   ║ P/E of 71 is excessive... ║
╚═══════════════════════════╩═══════════════════════════╝

⚖️ PORTFOLIO MANAGER'S DECISION
╔═══════════════╗
║   📈 BUY 📈   ║
╚═══════════════╝
```

## Project Structure

```
InvestmentCommitte/
│
├── main.py              # Orchestrator and Rich UI
├── agents.py            # Bull, Bear, Portfolio Manager agents
├── tools.py             # Financial data fetching (yfinance)
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .env                 # Your local config (gitignored)
└── README.md            # This file
```

## Key Components

### Data Layer (`tools.py`)

```python
from tools import get_financial_metrics, format_metrics_for_agent

metrics = get_financial_metrics("NVDA")
formatted = format_metrics_for_agent(metrics)
```

### Agents (`agents.py`)

```python
from agents import BullAgent, BearAgent, PortfolioManagerAgent

bull = BullAgent(llm_provider="anthropic")
bear = BearAgent(llm_provider="anthropic")
pm = PortfolioManagerAgent(llm_provider="anthropic")

bull_response = bull.analyze(financial_data)
bear_response = bear.analyze(financial_data)
decision = pm.make_decision(financial_data, bull_thesis, bear_thesis)
```

### Configuration (`config.py`)

```python
from config import AppConfig

config = AppConfig.from_env()
print(config.llm.provider)  # "anthropic" or "openai"
```

## Agent Protocol Design

The system implements a sophisticated multi-turn protocol:

1. **Data Acquisition Phase**
   - Fetch real-time financial data from Yahoo Finance
   - Structure data using Pydantic models

2. **Initial Analysis Phase** (Parallel)
   - Bull Agent analyzes from growth perspective
   - Bear Agent analyzes from risk perspective
   - Both run simultaneously for efficiency

3. **Rebuttal Phase** (Cross-examination)
   - Bull receives Bear's thesis and counters
   - Bear receives Bull's thesis and counters
   - Creates a more nuanced debate

4. **Decision Phase**
   - Portfolio Manager receives all arguments
   - Weighs evidence objectively
   - Outputs structured decision: BUY/SELL/HOLD

## Customization

### Modify Agent Behavior

Edit system prompts in `agents.py`:

```python
SYSTEM_PROMPTS = {
    AgentRole.BULL: "Your custom bull prompt...",
    AgentRole.BEAR: "Your custom bear prompt...",
    AgentRole.PORTFOLIO_MANAGER: "Your custom PM prompt..."
}
```

### Add New Financial Metrics

Extend `tools.py`:

```python
class FinancialMetrics(BaseModel):
    # Add new fields
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
```

### Change UI Styling

Modify `main.py` with Rich components:

```python
from rich.console import Console
from rich.panel import Panel

console = Console()
console.print(Panel("Your content", style="bold blue"))
```

## LLM Provider Notes

### Anthropic (Claude)
- Recommended for nuanced financial analysis
- Excellent at structured output
- Default model: `claude-3-5-sonnet-20241022`

### OpenAI (GPT)
- Fast and reliable
- Good at following instructions
- Default model: `gpt-4-turbo-preview`

Switch providers by changing `LLM_PROVIDER` in `.env`.

## Troubleshooting

### API Key Errors
```
ERROR: ANTHROPIC_API_KEY not found in .env file
```
**Solution**: Ensure your `.env` file exists and contains valid API keys.

### yfinance Errors
```
Failed to fetch data for XYZ: No data found
```
**Solution**: Verify the ticker symbol is correct and the stock is publicly traded.

### Import Errors
```
ModuleNotFoundError: No module named 'rich'
```
**Solution**: Run `pip install -r requirements.txt` in your virtual environment.

## Future Enhancements

- [ ] Add async/concurrent agent execution
- [ ] Implement caching for financial data
- [ ] Add historical backtesting mode
- [ ] Support for multiple tickers in batch
- [ ] Export reports to PDF/HTML
- [ ] Web interface with FastAPI
- [ ] Add sentiment analysis from news
- [ ] Implement risk scoring system

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - feel free to use this for learning, teaching, or commercial projects.

## Disclaimer

**This is an educational tool only.** The Investment Committee does not provide financial advice. All investment decisions should be made after proper research and consultation with licensed financial advisors. Past performance does not guarantee future results.

## Acknowledgments

- Built with [Claude](https://anthropic.com) and [OpenAI](https://openai.com)
- Financial data from [yfinance](https://github.com/ranaroussi/yfinance)
- Terminal UI powered by [Rich](https://github.com/Textualize/rich)

---

**Happy Investing!** 📈🐂🐻⚖️

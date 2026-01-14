"""
The Investment Committee - Main Orchestrator
Multi-Agent System for Stock Analysis
"""
import os
import sys
from typing import Tuple
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.layout import Layout
from rich import box
from rich.text import Text
import re

from tools import get_financial_metrics, format_metrics_for_agent
from agents import BullAgent, BearAgent, PortfolioManagerAgent, AgentResponse


console = Console()


def load_environment():
    """Load environment variables and validate configuration"""
    load_dotenv()

    # Get per-agent provider configuration
    bull_provider = os.getenv("BULL_PROVIDER", "anthropic").lower()
    bear_provider = os.getenv("BEAR_PROVIDER", "anthropic").lower()
    pm_provider = os.getenv("PM_PROVIDER", "openai").lower()

    providers = {bull_provider, bear_provider, pm_provider}

    # Validate API keys for providers in use
    if "openai" in providers:
        if not os.getenv("OPENAI_API_KEY"):
            console.print("[red]ERROR: OPENAI_API_KEY not found in .env file[/red]")
            sys.exit(1)

    if "anthropic" in providers:
        if not os.getenv("ANTHROPIC_API_KEY"):
            console.print("[red]ERROR: ANTHROPIC_API_KEY not found in .env file[/red]")
            sys.exit(1)

    return {
        "bull": bull_provider,
        "bear": bear_provider,
        "pm": pm_provider
    }


def display_header():
    """Display application header"""
    header_text = """
    ╔═══════════════════════════════════════════════════════════╗
    ║     THE INVESTMENT COMMITTEE                              ║
    ║     Multi-Agent Stock Analysis System                     ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(header_text, style="bold cyan")


def display_financial_data(metrics):
    """Display financial metrics in a clean table"""
    table = Table(title=f"Financial Data: {metrics.ticker}", box=box.ROUNDED, title_style="bold magenta")

    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    if metrics.error:
        table.add_row("ERROR", metrics.error)
        console.print(table)
        return

    table.add_row("Current Price", f"${metrics.current_price:.2f}" if metrics.current_price else "N/A")
    table.add_row("P/E Ratio", f"{metrics.pe_ratio:.2f}" if metrics.pe_ratio else "N/A")
    table.add_row("52-Week High", f"${metrics.week_52_high:.2f}" if metrics.week_52_high else "N/A")
    table.add_row("52-Week Low", f"${metrics.week_52_low:.2f}" if metrics.week_52_low else "N/A")
    table.add_row("Market Cap", f"${metrics.market_cap:,.0f}" if metrics.market_cap else "N/A")
    table.add_row("Volume", f"{metrics.volume:,}" if metrics.volume else "N/A")

    console.print(table)

    if metrics.news_headlines:
        news_panel = Panel(
            "\n".join([f"• {headline}" for headline in metrics.news_headlines]),
            title="Recent News",
            border_style="blue",
            box=box.ROUNDED
        )
        console.print(news_panel)


def extract_thesis(response: AgentResponse, tag: str) -> str:
    """Extract thesis from XML tags"""
    content = response.content
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return content


def run_parallel_analysis(
    financial_data: str,
    bull_agent: BullAgent,
    bear_agent: BearAgent
) -> Tuple[AgentResponse, AgentResponse]:
    """
    Run Bull and Bear analysis in parallel (simulated).

    Args:
        financial_data: Formatted financial metrics
        bull_agent: The Bull agent
        bear_agent: The Bear agent

    Returns:
        Tuple of (bull_response, bear_response)
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task1 = progress.add_task("[green]Bull Agent analyzing...", total=None)
        task2 = progress.add_task("[red]Bear Agent analyzing...", total=None)

        # In a real parallel system, these would run concurrently
        # For simplicity, we run them sequentially here
        bull_response = bull_agent.analyze(financial_data)
        progress.update(task1, completed=True)

        bear_response = bear_agent.analyze(financial_data)
        progress.update(task2, completed=True)

    return bull_response, bear_response


def run_rebuttal_phase(
    financial_data: str,
    bull_agent: BullAgent,
    bear_agent: BearAgent,
    initial_bull: AgentResponse,
    initial_bear: AgentResponse
) -> Tuple[AgentResponse, AgentResponse]:
    """
    Run rebuttal phase where agents counter each other's arguments.

    Args:
        financial_data: Formatted financial metrics
        bull_agent: The Bull agent
        bear_agent: The Bear agent
        initial_bull: Initial bull thesis
        initial_bear: Initial bear thesis

    Returns:
        Tuple of (bull_rebuttal, bear_rebuttal)
    """
    console.print("\n[bold yellow]🔄 REBUTTAL PHASE: Agents counter each other's arguments[/bold yellow]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task1 = progress.add_task("[green]Bull countering Bear's thesis...", total=None)
        task2 = progress.add_task("[red]Bear countering Bull's thesis...", total=None)

        bull_rebuttal = bull_agent.analyze(financial_data, bear_thesis=initial_bear.content)
        progress.update(task1, completed=True)

        bear_rebuttal = bear_agent.analyze(financial_data, bull_thesis=initial_bull.content)
        progress.update(task2, completed=True)

    return bull_rebuttal, bear_rebuttal


def display_debate(bull_response: AgentResponse, bear_response: AgentResponse):
    """Display Bull and Bear theses side-by-side"""
    console.print("\n[bold]📊 THE DEBATE[/bold]\n")

    bull_thesis = extract_thesis(bull_response, "bull_thesis")
    bear_thesis = extract_thesis(bear_response, "bear_thesis")

    bull_panel = Panel(
        bull_thesis,
        title="🐂 THE BULL THESIS",
        border_style="green",
        box=box.DOUBLE,
        padding=(1, 2)
    )

    bear_panel = Panel(
        bear_thesis,
        title="🐻 THE BEAR THESIS",
        border_style="red",
        box=box.DOUBLE,
        padding=(1, 2)
    )

    columns = Columns([bull_panel, bear_panel], equal=True, expand=True)
    console.print(columns)


def display_final_decision(decision):
    """Display the Portfolio Manager's final decision"""
    console.print("\n[bold]⚖️  PORTFOLIO MANAGER'S DECISION[/bold]\n")

    # Color code the decision
    if decision.decision.value == "BUY":
        decision_style = "bold green on black"
        emoji = "📈"
    elif decision.decision.value == "SELL":
        decision_style = "bold red on black"
        emoji = "📉"
    else:
        decision_style = "bold yellow on black"
        emoji = "⏸️"

    decision_text = Text(f"\n  {emoji}  {decision.decision.value}  {emoji}  \n", style=decision_style)
    console.print(Panel(decision_text, border_style="magenta", box=box.DOUBLE))

    justification_panel = Panel(
        decision.justification,
        title="Justification",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(justification_panel)


def run_investment_committee(ticker: str, providers: dict):
    """
    Main orchestrator for the Investment Committee.

    The Protocol:
    1. Fetch financial data
    2. Bull and Bear analyze in parallel
    3. Rebuttal phase (agents counter each other)
    4. Portfolio Manager makes final decision

    Args:
        ticker: Stock ticker symbol
        providers: Dict with 'bull', 'bear', 'pm' provider settings
    """
    console.print(f"\n[bold cyan]🔍 Analyzing {ticker.upper()}...[/bold cyan]\n")

    # STEP 1: Fetch financial data
    with console.status("[bold green]Fetching financial data from yfinance..."):
        metrics = get_financial_metrics(ticker)

    if metrics.error:
        console.print(f"[red]Failed to fetch data for {ticker}: {metrics.error}[/red]")
        return

    display_financial_data(metrics)
    financial_data = format_metrics_for_agent(metrics)

    # STEP 2: Initialize agents with different providers
    console.print("\n[bold]🤖 Initializing AI Agents...[/bold]")
    console.print(f"[dim]  🐂 Bull: {providers['bull'].upper()}[/dim]")
    console.print(f"[dim]  🐻 Bear: {providers['bear'].upper()}[/dim]")
    console.print(f"[dim]  ⚖️  PM: {providers['pm'].upper()}[/dim]\n")

    bull_agent = BullAgent(llm_provider=providers['bull'])
    bear_agent = BearAgent(llm_provider=providers['bear'])
    pm_agent = PortfolioManagerAgent(llm_provider=providers['pm'])

    # STEP 3: Parallel analysis (initial theses)
    console.print("\n[bold yellow]📡 Phase 1: Initial Analysis (Parallel)[/bold yellow]\n")
    bull_response, bear_response = run_parallel_analysis(financial_data, bull_agent, bear_agent)

    # STEP 4: Rebuttal phase
    bull_rebuttal, bear_rebuttal = run_rebuttal_phase(
        financial_data, bull_agent, bear_agent, bull_response, bear_response
    )

    # Display the debate (using rebuttals)
    display_debate(bull_rebuttal, bear_rebuttal)

    # STEP 5: Portfolio Manager decision
    console.print("\n[bold yellow]⚖️  Portfolio Manager deliberating...[/bold yellow]\n")
    with console.status("[bold magenta]Making final decision..."):
        pm_response = pm_agent.make_decision(
            financial_data,
            bull_rebuttal.content,
            bear_rebuttal.content
        )

    decision = PortfolioManagerAgent.parse_decision(pm_response)
    display_final_decision(decision)


def main():
    """Main entry point"""
    display_header()

    # Load configuration
    providers = load_environment()
    console.print("[dim]Multi-LLM Configuration Loaded[/dim]\n")

    while True:
        ticker = Prompt.ask("\n[bold cyan]Enter stock ticker (or 'quit' to exit)[/bold cyan]").strip()

        if ticker.lower() in ['quit', 'exit', 'q']:
            console.print("\n[bold green]Thank you for using The Investment Committee![/bold green]")
            break

        if not ticker:
            console.print("[yellow]Please enter a valid ticker symbol.[/yellow]")
            continue

        try:
            run_investment_committee(ticker, providers)
        except KeyboardInterrupt:
            console.print("\n[yellow]Analysis interrupted by user.[/yellow]")
        except Exception as e:
            console.print(f"\n[red]Error during analysis: {str(e)}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")

        console.print("\n" + "─" * 60)


if __name__ == "__main__":
    main()

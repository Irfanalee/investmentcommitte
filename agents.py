"""
Agent Layer: Bull, Bear, and Portfolio Manager AI Agents
"""
from typing import Optional, Literal
from pydantic import BaseModel
import os
from enum import Enum


class AgentRole(str, Enum):
    """Agent role definitions"""
    BULL = "bull"
    BEAR = "bear"
    PORTFOLIO_MANAGER = "portfolio_manager"


class AgentResponse(BaseModel):
    """Structured response from an agent"""
    role: AgentRole
    content: str
    raw_response: str


class Decision(str, Enum):
    """Portfolio Manager decision options"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class PortfolioDecision(BaseModel):
    """Final decision from Portfolio Manager"""
    decision: Decision
    justification: str
    confidence: Optional[str] = None


class Agent:
    """Base Agent class for Investment Committee"""

    SYSTEM_PROMPTS = {
        AgentRole.BULL: """You are a growth-focused aggressive investor known as "The Bull".

Your mandate:
- Look for potential, innovation, and market expansion opportunities
- Focus on long-term growth catalysts and competitive advantages
- Ignore short-term risks and market noise
- Be optimistic about future earnings potential
- Highlight technological breakthroughs and market disruptions

You must output your analysis wrapped in <bull_thesis> XML tags. Structure your thesis with:
1. Key growth drivers
2. Competitive advantages
3. Market opportunity size
4. Why current concerns are overblown

Be persuasive and confident in your bullish stance.""",

        AgentRole.BEAR: """You are a risk-averse, skeptical investor known as "The Bear".

Your mandate:
- Look for overvaluation, excessive hype, and unsustainable growth
- Identify regulatory hurdles, competitive threats, and macroeconomic headwinds
- Focus on downside risks and what could go wrong
- Challenge optimistic assumptions with hard data
- Highlight valuation concerns and market saturation

You must output your analysis wrapped in <bear_thesis> XML tags. Structure your thesis with:
1. Valuation concerns
2. Competitive threats and market risks
3. Regulatory or macroeconomic headwinds
4. Why the bulls are wrong

Be critical and rigorous in your bearish stance.""",

        AgentRole.PORTFOLIO_MANAGER: """You are an experienced Portfolio Manager and the final decision maker.

Your mandate:
- Read and analyze both the Bull Thesis and Bear Thesis carefully
- Weigh the evidence objectively without bias
- Consider both upside potential and downside risks
- Make a clear, decisive recommendation

You MUST output your decision in this exact format:
<decision>BUY</decision> or <decision>SELL</decision> or <decision>HOLD</decision>

Followed by:
<justification>
Your reasoning here (2-3 paragraphs explaining why you chose this decision,
which arguments were most compelling, and what factors tipped the scale)
</justification>

Be balanced but decisive. Don't hedge excessively."""
    }

    def __init__(self, role: AgentRole, llm_provider: str = "anthropic"):
        """
        Initialize an agent with a specific role.

        Args:
            role: The agent's role (BULL, BEAR, or PORTFOLIO_MANAGER)
            llm_provider: "openai" or "anthropic"
        """
        self.role = role
        self.system_prompt = self.SYSTEM_PROMPTS[role]
        self.llm_provider = llm_provider
        self._client = None

    def _get_client(self):
        """Lazy load the LLM client"""
        if self._client is None:
            if self.llm_provider == "openai":
                from openai import OpenAI
                self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            elif self.llm_provider == "anthropic":
                from anthropic import Anthropic
                self._client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            else:
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")
        return self._client

    def _call_openai(self, user_message: str) -> str:
        """Call OpenAI API"""
        client = self._get_client()
        model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content

    def _call_anthropic(self, user_message: str) -> str:
        """Call Anthropic API"""
        client = self._get_client()
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        response = client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0.7,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        return response.content[0].text

    def invoke(self, user_message: str) -> AgentResponse:
        """
        Invoke the agent with a message.

        Args:
            user_message: The prompt/data to send to the agent

        Returns:
            AgentResponse with structured output
        """
        if self.llm_provider == "openai":
            raw_response = self._call_openai(user_message)
        else:
            raw_response = self._call_anthropic(user_message)

        return AgentResponse(
            role=self.role,
            content=raw_response,
            raw_response=raw_response
        )


class BullAgent(Agent):
    """The Bull - Growth-focused aggressive investor"""

    def __init__(self, llm_provider: str = "anthropic"):
        super().__init__(AgentRole.BULL, llm_provider)

    def analyze(self, financial_data: str, bear_thesis: Optional[str] = None) -> AgentResponse:
        """
        Analyze stock data from a bullish perspective.

        Args:
            financial_data: Formatted financial metrics
            bear_thesis: Optional bear thesis to counter

        Returns:
            AgentResponse with bull thesis
        """
        if bear_thesis:
            prompt = f"""{financial_data}

---
BEAR'S COUNTERARGUMENT TO ADDRESS:
{bear_thesis}

---
Now provide your REBUTTAL and reinforced bull thesis, addressing the bear's concerns."""
        else:
            prompt = f"""{financial_data}

---
Analyze this stock and provide your bullish investment thesis."""

        return self.invoke(prompt)


class BearAgent(Agent):
    """The Bear - Risk-averse skeptical investor"""

    def __init__(self, llm_provider: str = "anthropic"):
        super().__init__(AgentRole.BEAR, llm_provider)

    def analyze(self, financial_data: str, bull_thesis: Optional[str] = None) -> AgentResponse:
        """
        Analyze stock data from a bearish perspective.

        Args:
            financial_data: Formatted financial metrics
            bull_thesis: Optional bull thesis to counter

        Returns:
            AgentResponse with bear thesis
        """
        if bull_thesis:
            prompt = f"""{financial_data}

---
BULL'S COUNTERARGUMENT TO ADDRESS:
{bull_thesis}

---
Now provide your REBUTTAL and reinforced bear thesis, addressing the bull's overoptimism."""
        else:
            prompt = f"""{financial_data}

---
Analyze this stock and provide your bearish investment thesis."""

        return self.invoke(prompt)


class PortfolioManagerAgent(Agent):
    """The Portfolio Manager - Final decision maker"""

    def __init__(self, llm_provider: str = "anthropic"):
        super().__init__(AgentRole.PORTFOLIO_MANAGER, llm_provider)

    def make_decision(
        self,
        financial_data: str,
        bull_thesis: str,
        bear_thesis: str
    ) -> AgentResponse:
        """
        Make final investment decision based on both theses.

        Args:
            financial_data: Formatted financial metrics
            bull_thesis: The bull's argument
            bear_thesis: The bear's argument

        Returns:
            AgentResponse with final decision
        """
        prompt = f"""{financial_data}

---
BULL THESIS:
{bull_thesis}

---
BEAR THESIS:
{bear_thesis}

---
As Portfolio Manager, weigh both arguments and make your final decision: BUY, SELL, or HOLD.
Provide clear justification for your choice."""

        return self.invoke(prompt)

    @staticmethod
    def parse_decision(response: AgentResponse) -> PortfolioDecision:
        """
        Parse the Portfolio Manager's response into structured decision.

        Args:
            response: AgentResponse from Portfolio Manager

        Returns:
            PortfolioDecision object
        """
        content = response.content

        # Extract decision
        decision_str = "HOLD"  # default
        if "<decision>" in content and "</decision>" in content:
            start = content.find("<decision>") + len("<decision>")
            end = content.find("</decision>")
            decision_str = content[start:end].strip().upper()

        # Extract justification
        justification = content
        if "<justification>" in content and "</justification>" in content:
            start = content.find("<justification>") + len("<justification>")
            end = content.find("</justification>")
            justification = content[start:end].strip()

        try:
            decision = Decision[decision_str]
        except KeyError:
            decision = Decision.HOLD

        return PortfolioDecision(
            decision=decision,
            justification=justification
        )

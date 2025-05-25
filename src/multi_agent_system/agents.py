import random
import re
from typing import Callable, Tuple, List, Optional
from dataclasses import dataclass

from multi_agent_system.providers import LLM
from haystack.dataclasses import ChatMessage
from haystack.tools import create_tool_from_function
from haystack.components.tools import ToolInvoker

HANDOFF_PATTERN = r"Transferred to: (.*?)(?:\.|$)"


# This implementation is based on https://haystack.deepset.ai/cookbook/swarm
@dataclass
class SwarmAgent:
    name: str
    llm: LLM
    instructions: str
    functions: Optional[List[Callable]] = None

    def __post_init__(self):
        # General description of the agent's tasks and capabilities
        self._system_message = ChatMessage.from_system(self.instructions)
        # Tools (functions) that the agent can call to accomplish a request
        self.tools = (
            [create_tool_from_function(fun) for fun in self.functions]
            if self.functions
            else None
        )
        self._tool_invoker = (
            ToolInvoker(tools=self.tools, raise_on_failure=False)
            if self.tools
            else None
        )

    def run(self, messages: List[ChatMessage]) -> Tuple[str, List[ChatMessage]]:
        # Generate response
        agent_message = self.llm.run(
            messages=[self._system_message] + messages, tools=self.tools
        )["replies"][0]
        new_messages = [agent_message]

        if agent_message.text:
            print(f"\n{self.name}: {agent_message.text}")

        if not agent_message.tool_calls:
            return self.name, new_messages

        # Handle tool calls
        for tc in agent_message.tool_calls:
            # Trick: Ollama does not produce IDs, but OpenAI and Anthropic require them.
            if tc.id is None:
                tc.id = str(random.randint(0, 1000000))
        tool_results = self._tool_invoker.run(messages=[agent_message])["tool_messages"]
        new_messages.extend(tool_results)

        # Handoff (handing over to another agent)
        last_result = tool_results[-1].tool_call_result.result
        match = re.search(HANDOFF_PATTERN, last_result)
        new_agent_name = match.group(1) if match else self.name

        return new_agent_name, new_messages

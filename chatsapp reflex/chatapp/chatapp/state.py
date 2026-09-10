import reflex as rx
import asyncio
from openai import AsyncOpenAI
import os


class State(rx.State):
    question: str
    chat_history: list[tuple[str, str]]

    @rx.event
    def set_question(self, value: str):
        self.question = value

    @rx.event
    async def answer(self):
        client = AsyncOpenAI(base_url="https://router.huggingface.co/v1", api_key=os.environ.get("HF_TOKEN", "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"))
        response = await client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[{"role": "user", "content": self.question}],
                stream=True,
                max_tokens=750,
        )
        
        answer = ""
        self.chat_history.append((self.question, answer))
        self.question = ""
        yield

        async for item in response:
            if hasattr(item.choices[0].delta, "content"):
                if item.choices[0].delta.content is None:
                    break
                answer += item.choices[0].delta.content
                self.chat_history[-1] = (self.chat_history[-1][0], answer)
                yield

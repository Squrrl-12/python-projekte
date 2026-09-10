import os
import re
import reflex as rx
from reflex.style import color_mode, set_color_mode
from rxconfig import config
import dataclasses
import asyncio
from openai import AsyncOpenAI
from self_app import style
#for calculator:
import ast
import operator

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,   # unäres Minus, z. B. -5
    ast.UAdd: operator.pos,
}
def safe_eval(expr: str) -> float:
    """Wertet einen einfachen arithmetischen Ausdruck sicher aus."""
    tree = ast.parse(expr, mode="eval")
    return _eval_node(tree.body)

def _eval_node(node):
    if isinstance(node, ast.Constant):  # Zahl, z. B. 5
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Nur Zahlen sind erlaubt.")
    if isinstance(node, ast.BinOp):  # z. B. 2 + 3
        op_type = type(node.op)
        if op_type not in _OPERATORS:
            raise ValueError(f"Operator nicht erlaubt: {op_type}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _OPERATORS[op_type](left, right)
    if isinstance(node, ast.UnaryOp):  # z. B. -5
        op_type = type(node.op)
        if op_type not in _OPERATORS:
            raise ValueError(f"Operator nicht erlaubt: {op_type}")
        return _OPERATORS[op_type](_eval_node(node.operand))
    raise ValueError(f"Nicht erlaubter Ausdruck: {ast.dump(node)}")

@dataclasses.dataclass
class Task:
    text: str
    done: bool = False

#for chatbot
class ThinkTagFilter:
    """Strips <think>...</think> blocks from a streamed text feed,
    correctly handling tags split across multiple chunks."""
    def __init__(self):
        self.buffer = ""
        self.in_think = False
    def feed(self, chunk: str) -> str:
        self.buffer += chunk
        visible = ""
        while True:
            if not self.in_think:
                start = self.buffer.find("<think>")
                if start == -1:
                    safe_len = self._safe_flush_length(self.buffer, "<think>")
                    visible += self.buffer[:safe_len]
                    self.buffer = self.buffer[safe_len:]
                    break
                visible += self.buffer[:start]
                self.buffer = self.buffer[start + len("<think>"):]
                self.in_think = True
            else:
                end = self.buffer.find("</think>")
                if end == -1:
                    safe_len = self._safe_flush_length(self.buffer, "</think>")
                    self.buffer = self.buffer[safe_len:]
                    break
                self.buffer = self.buffer[end + len("</think>"):]
                self.in_think = False
        return visible
    @staticmethod
    def _safe_flush_length(text: str, tag: str) -> int:
        max_check = min(len(tag) - 1, len(text))
        for i in range(max_check, 0, -1):
            if tag.startswith(text[-i:]):
                return len(text) - i
        return len(text)
    
    
class State(rx.State):
    colors: list[str] = [
        "red", "blue", "green"
    ]
    change: bool = True
    list_websites: dict[str, str] = {
        "Playground ->": "http://localhost:3000/playground",
        "Calculator ->": "http://localhost:3000/calculator",
        "Chatbot ->": "http://localhost:3000/chatbot",
        "Customization ->": "http://localhost:3000/customize",
    }
    #yield
    count: int = 0
    show_progress: bool = False
    #task list
    tasks: list[Task] = [
        Task(text="Doing dishes"),
        Task(text="Vacuuming"),
        Task(text="Laundry"),
    ]
    new_task_text: str = ""
    expr: str = ""
    result: str = ""
    #for theme customization: shared across every page
    accent_color: str = "purple"
    radius: str = "full"

    @rx.event
    def add_colors(self, form_data: dict[str, str]):
        self.colors.append(form_data["colors"])

    @rx.event
    def set_accent_color(self, value: str):
        self.accent_color = value

    @rx.event
    def set_radius(self, value: str):
        self.radius = value

    @rx.event
    def set_expr(self, expr: str):
        self.expr = expr

    @rx.event
    def use_calc(self):
        try:
            value = safe_eval(self.expr)
            self.result = str(value)
        except (ValueError, ZeroDivisionError, SyntaxError, TypeError) as e:
            self.result = f"Error: {e}"

    @rx.event
    def wipe_calc_clean(self):
        self.expr = ""
        self.result = ""
    #task list functions:
    @rx.event
    async def add_num(self):
        self.show_progress = True
        yield
        await asyncio.sleep(0.5)
        self.count += 5
        self.show_progress = False

    @rx.event
    async def increment(self):
        yield State.add_num
        yield State.add_num
        yield State.add_num
    #other playground features

    @rx.event
    def change_t(self):
        self.change = not (self.change)

    #Task list features
    @rx.event
    def toggle_task(self, index: int):
        self.tasks[index].done = not self.tasks[index].done
    @rx.event
    def set_new_task(self, new_task_text: str):
        self.new_task_text = new_task_text
    @rx.event
    def submit_task(self):
        if self.new_task_text == "":
            return
        self.tasks.append(Task(text=self.new_task_text, done=False))
        self.new_task_text = ""
    @rx.event
    def clear_completed_tasks(self):
        self.tasks = [task for task in self.tasks if not task.done]

    #chatbot features
    question: str
    chat_history: list[tuple[str, str]]
    @rx.event
    def set_question(self, question: str):
        self.question = question
    @rx.event
    async def answer(self):
        client = AsyncOpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=os.environ.get("HF_TOKEN"),
        )
        response = await client.chat.completions.create(
            model="Qwen/Qwen3-8B",
            messages=[{"role": "user", "content": self.question}],
            stream=True,
            max_tokens=2048,
        )
        answer = ""
        self.chat_history.append((self.question, answer))
        self.question = ""
        yield
        tag_filter = ThinkTagFilter()
        async for item in response:
            if not item.choices:
                continue
            delta = item.choices[0].delta
            if getattr(delta, "reasoning_content", None):
                continue
            content = getattr(delta, "content", None)
            if content is None:
                continue
            visible_text = tag_filter.feed(content)
            if visible_text:
                answer += visible_text
                self.chat_history[-1] = (self.chat_history[-1][0], answer)
                yield
#for theme customization: shared layout wrapper used by every page
ACCENT_COLORS = [
    "tomato", "red", "ruby", "crimson", "pink", "purple", "violet",
    "indigo", "blue", "cyan", "teal", "green", "grass", "orange",
    "brown", "sky", "mint", "yellow", "amber", "gray",
]
RADIUS_OPTIONS = ["none", "small", "medium", "large", "full"]
def themed_layout(*children) -> rx.Component:
    return rx.theme(
        rx.box(*children, width="100%"),
        appearance="inherit",
        accent_color=State.accent_color,
        radius=State.radius,
        has_background=True,
        width="100%",
        min_height="100vh",
    )

def theme_controls() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("Appearance", width="120px"),
            rx.segmented_control.root(
                rx.segmented_control.item("Light", value="light"),
                rx.segmented_control.item("Dark", value="dark"),
                value=color_mode,
                on_change=set_color_mode,
            ),
        ),
        rx.hstack(
            rx.text("Accent Color", width="120px"),
            rx.select(
                ACCENT_COLORS,
                value=State.accent_color,
                on_change=State.set_accent_color,
            ),
        ),
        rx.hstack(
            rx.text("Radius", width="120px"),
            rx.select(
                RADIUS_OPTIONS,
                value=State.radius,
                on_change=State.set_radius,
            ),
        ),
        spacing="3",
        align="start",
    )
def colored_box(colors: str):
    return rx.button(colors, background_color=colors)

def display_website(web: list):
    return rx.box(
        rx.hstack(
            rx.text(web[0]),
            rx.text(web[1]),
            padding_x="1.5em",
            spacing="4",
        ),
    )

def get_image():
    pic_path = rx.asset("frog_2.jpg")
    return rx.image(src=pic_path, alt="frog", width="250px", height="auto")
#task list

def task_row(task: Task, index: int):
    return rx.hstack(
        rx.text(task.text, width="100%"),
        rx.checkbox(checked=task.done, on_change=lambda checked: State.toggle_task(index)),
        padding_x="0.5em",
    )
def show_tasks():
    return rx.vstack(
        rx.foreach(State.tasks, lambda task, index: task_row(task, index)),
        align="start",
        width="100%",
    )
def title():
    return rx.vstack(
        rx.heading(
            "Chat with our Chatbot!",
            size="8",
            color=rx.color("accent", 12),
            _hover={"color": "teal"},
        ),
        rx.text(
            "Ask any question and get an answer from our chatbot.",
            color=rx.color("accent", 6),
        ),
        spacing="3",
        align="center",
    )
def qa(question: str, answer: str):
    return rx.hstack(
        rx.box(
            rx.box(
                question,
                style=style.question_style,
                text_align="right",
                padding="0.5em 1em",
                border_radius="10px",
                display="inline-block",
                max_width="80%",
            ),
            width="80%",
            display="flex",
            justify_content="flex-end",
        ),
        rx.box(
            rx.box(
                answer,
                style=style.answer_style,
                text_align="left",
                padding="0.5em 1em",
                border_radius="10px",
                display="inline-block",
                max_width="80%",
            ),
            width="80%",
            display="flex",
            justify_content="flex-start",
            margin_top="0.3em",
        ),
        margin_y="1em",
        width="100%",
    )
def chat():
    return rx.vstack(
        rx.foreach(State.chat_history, lambda messages: qa(messages[0], messages[1])),
        spacing="6",
        width="90%",
    )
def action_bar():
    return rx.hstack(
        rx.input(
            value=State.question,
            placeholder="Ask a question",
            on_change=State.set_question,
            style=style.input_style,
        ),
        rx.button("Submit", on_click=State.answer, style=style.button_style)
    )
def chatbot():
    return themed_layout(
        rx.center(
            rx.vstack(
                title(),
                chat(),
                action_bar(),
                spacing="2",
                width="100%",
                align="center",
            )
        )
    )
def calculator():
    return themed_layout(
        rx.center(
            rx.vstack(
                rx.heading(
                    "Calculator",
                    size="8",
                    weight="bold",
                    color=rx.color("purple", 12),
                    align="center",
                    margin_y="0.5em",
                    _hover={"color": "teal"},
                ),
                rx.text("Calculate what you want!", size="6", weight="bold"),
                rx.input(
                    placeholder="2+3",
                    value=State.expr,
                    on_change=State.set_expr,
                    width="100%",
                    id="calc-input",
                ),
                rx.hstack(
                    rx.button("Calculate Result:", on_click=State.use_calc, color_scheme="grass"),
                    rx.button("Delete Output", on_click=State.wipe_calc_clean, color_scheme="red")
                ),
                rx.text(f"The Result: {State.result}"),
            ),
            width="100%",
            spacing="4",
            flex="1",
        )
    )
def playground():
    return themed_layout(
        rx.box(
            rx.heading(
                "Playground",
                size="8",
                weight="bold",
                color=rx.color("accent", 12),
                align="center",
                margin_y="0.5em",
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("Add colored buttons", size="6", weight="bold"),
                    rx.foreach(State.colors, colored_box),
                    rx.form(
                        rx.input(name="colors", placeholder="Add color"),
                        rx.button("Add", border="4px"),
                        on_submit=State.add_colors,
                    ),
                ),
                rx.vstack(
                    rx.text("Change color text", size="6", weight="bold"),
                    rx.button("Toggle", on_click=State.change_t),
                    rx.cond(
                        State.change,
                        rx.text("True", color="blue"),
                        rx.text("False", color="red"),
                    ),
                ),
                rx.vstack(
                    rx.text("Increment number", size="6", weight="bold"),
                    rx.text(State.count),
                    rx.button(
                        "Add 3*15",
                        on_click=State.increment,
                        loading=State.show_progress
                    )
                ),
                rx.vstack(
                    rx.text("Task List", size="6", weight="bold"),
                    show_tasks(),
                    rx.input(
                        placeholder="Input new task",
                        value=State.new_task_text,
                        on_change=State.set_new_task,
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button("Add Task", on_click=State.submit_task),
                        rx.button("Delete completed tasks", on_click=State.clear_completed_tasks, color_scheme="red"),
                    ),
                ),
            ),
            width="100%",
            spacing="8",
            flex="1",
            padding_x="2em",
            margin_y="1.5em"
        )
    )
def customize():
    return themed_layout(
        rx.center(
            rx.vstack(
                rx.heading("Theme Settings", color=rx.color("accent", 12), align="left"),
                rx.text(
                    "Change the appearance, accent color, and radius — applies to every page.",
                    align="left",
                ),
                theme_controls(),
                rx.divider(),
                rx.hstack(
                    rx.button("Preview Button", color_scheme=State.accent_color),
                    rx.badge("Preview Badge"),
                ),
                spacing="4",
                align="start",
            ),
            width="100%",
            margin_y="1.5em",
            padding_x="1.5em",
        )
    )

def homepage():
    return themed_layout(
        rx.center(
            rx.vstack(
                rx.heading("Welcome to the Website", as_="h2", width="100%", weight="bold", padding="1em", color=rx.color("accent", 12)),
                rx.text("Try out the features (Copy the links):", size="5", width="100%", padding="1.5em", class_name="highlight-text",),
                rx.foreach(State.list_websites, display_website),
                width="100%",
            ),
        )
    )

app = rx.App(theme=rx.theme(appearance="inherit", accent_color="purple", radius="full"), style=style.st)
app.add_page(homepage, route="/")
app.add_page(playground, route="/playground")
app.add_page(chatbot, route="/chatbot")
app.add_page(calculator, route="/calculator")
app.add_page(customize, route="/customize")

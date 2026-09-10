# chatapp.py
import reflex as rx
from chatapp import style
from chatapp.state import State


def qa(question: str, answer: str):
    return rx.box(
        # Frage - rechtsbündig als Box
        rx.box(
            rx.box(
                question,
                style=style.question_style,
                text_align="right",
                padding="0.5em 1em",
                border_radius="10px",
                display="inline-block",
            ),
            width="80%",
            display="flex",
            justify_content="flex-end",  # Box nach rechts schieben
        ),
        # Antwort - linksbündig als Box
        rx.box(
            rx.box(
                answer,
                style=style.answer_style,
                text_align="left",
                padding="0.5em 1em",
                border_radius="10px",
                display="inline-block",
            ),
            width="80%",
            display="flex",
            justify_content="flex-start",  # Box nach links schieben
            margin_top="0.3em",
        ),
        margin_y="1em",
        width="100%",
    )

def title():
    return rx.vstack(
        rx.heading("Chat with LLaMA 3.1",color=rx.color("accent", 8)),
        rx.text(
            "Ask questions and get answers from the LLaMA 3.1 model.",
            color=rx.color("mint", 6),
        ),
        spacing="2",
        align="center",
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
            placeholder="Ask your question",
            on_change=State.set_question,
            style=style.input_style,
        ),
        rx.button("Ask", on_click=State.answer, style=style.button_style),
    )


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            title(),
            chat(),
            action_bar(),
            spacing="2",
            width="100%",
            align="center",
        )
    )


# Add state and page to the app.
app = rx.App(theme=rx.theme(radius="full", accent_color="teal"))
app.add_page(index, route="/")

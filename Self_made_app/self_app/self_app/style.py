import reflex as rx

shadow = "rgba(0, 0, 0.5, 0.15) 0px 2px 8px"
chat_margin = "15%"
message_style = dict(
    padding="1em",
    border_radius="10px",
    box_shadow = shadow,
    max_width= "10em",
    display="inline-block",
)

question_style = message_style | dict(
    margin_left=chat_margin,
    background_color=rx.color("gray", 4),
    max_width="80%",
)

answer_style = message_style | dict(
    margin_right=chat_margin,
    background_color=rx.color("accent", 8),
    max_width="80%",
)

input_style = dict(
    border_width="1px", padding="0.5em", box_shadow=shadow, width="350px",
)

button_style = dict(
    background_color=rx.color("accent", 10), box_shadow=shadow,
)

st = {
    "font_family": "Comic Sans MS",
    "font_size": "16px",

    # Text-selection highlight follows whatever accent color is
    # currently active — no manual sync needed.
    "::selection": {
        "background_color": rx.color("accent", 9),
    },

    # Utility class: add class_name="highlight-text" to any rx.text
    # to underline it (used on the homepage call-to-action below).
    ".highlight-text": {
        "text_decoration": "underline",
    },

    # Targets the calculator's expression input specifically
    # (see id="calc-input" added in calculator() below).
    "#calc-input": {"width": "10vw"},

    rx.text: {
        "font_family": "Comic Sans MS",
    },
    rx.divider: {
        "margin_bottom": "1em",
        "margin_top": "0.5em",
    },
    rx.heading: {
        "font_weight": "500",
    },
    rx.code: {
        "color": "purple",
    },
}

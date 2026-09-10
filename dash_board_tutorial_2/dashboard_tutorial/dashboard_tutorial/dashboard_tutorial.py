from collections import Counter
import dataclasses
import reflex as rx

#for dashboard
@dataclasses.dataclass
class User:
    name: str
    email: str
    gender: str


class State(rx.State):
    #for dashboard
    users: list[User] = [
        User(name="Danilo Sousa", email="danilo@example.com", gender="Male"),
        User(name="Zahra Ambessa", email="zahra@example.com", gender="Female"),
    ]
    users_for_graph: list[dict] = []
    
    #for playground
    count: int = 0
    amount_to_add: str = "0"
    
    increment_num: int = 0

    items: list[str] = ["Example1", "Example2"]
    item_to_add : str

    #for dashboard
    def add_user(self, form_data: dict):
        self.users.append(User(**form_data))
        self.transform_data()

    #for playground
    def increment_count(self):
        try:
            self.count += int(self.amount_to_add)
        except ValueError:
            pass

    # Reflex 0.9+ no longer auto-generates set_<var> setters.
    # on_change on rx.input sends a str, so this explicit handler
    # accepts str and assigns it directly — no type mismatch.
    #for playground
    def set_amount_to_add(self, value: str):
        self.amount_to_add = value

    #for dashboard
    def transform_data(self):
        """Transform user gender group data into a format suitable for visualization in graphs."""
        # Count users of each gender group
        gender_counts = Counter(user.gender for user in self.users)

        # Transform into list of dict so it can be used in the graph
        self.users_for_graph = [
            {"name": gender_group, "value": count}
            for gender_group, count in gender_counts.items()
        ]
    
    #for playground
    # for playground
    def add_to_list(self, form_data: dict):
        # Wir extrahieren den Text aus dem Dictionary anhand des 'name' Attributs aus dem Input
        new_item = form_data.get("item_to_add", "")
        
        # Nur hinzufügen, wenn das Feld nicht leer ist
        if new_item.strip():
            self.items.append(new_item)

    @rx.event
    def increment(self, amount: int):
        self.increment_num += amount

    @rx.event
    def decrement(self, amount: int):
        self.increment_num -= amount


#for dashboard
def show_user(user: User):
    return rx.table.row(
        rx.table.cell(user.name),
        rx.table.cell(user.email),
        rx.table.cell(user.gender),
        style={"_hover": {"bg": rx.color("gray", 3)}},
        align="center",
    )

#for playground
def render_item(item: rx.Var[str]):
    return rx.list.item(item)


#for dashboard
def add_customer_button() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=26),
                rx.text("Add User", size="4"),
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Add New User",
            ),
            rx.dialog.description(
                "Fill the form with the user's info",
            ),
            rx.form(
                rx.flex(
                    rx.input(placeholder="User Name", name="name", required=True),
                    rx.input(
                        placeholder="user@reflex.dev",
                        name="email",
                    ),
                    rx.select(
                        ["Male", "Female"],
                        placeholder="Male",
                        name="gender",
                    ),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="soft",
                                color_scheme="gray",
                            ),
                        ),
                        rx.dialog.close(
                            rx.button("Submit", type="submit"),
                        ),
                        spacing="3",
                        justify="end",
                    ),
                    direction="column",
                    spacing="4",
                ),
                on_submit=State.add_user,
                reset_on_submit=False,
            ),
            max_width="450px",
        ),
    )

#for dashboard
def graph():
    return rx.recharts.bar_chart(
        rx.recharts.bar(
            data_key="value",
            fill=rx.color("accent", 9),
            radius=6,
            bar_size=48,
        ),
        rx.recharts.x_axis(
            data_key="name",
            tick_line=False,
            axis_line=False,
            padding={"left": 24, "right": 24},
        ),
        rx.recharts.y_axis(
            tick_line=False,
            axis_line=False,
            allow_decimals=False,
        ),
        rx.recharts.cartesian_grid(
            stroke_dasharray="3 3",
            vertical=False,
            stroke=rx.color("slate", 4),
        ),
        data=State.users_for_graph,
        width="100%",
        height=200,
        margin={"top": 8, "right": 8, "bottom": 0, "left": 0},
    )

#for playground
# for playground
def button_add_item():
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=16),
                rx.text("Add item", size="2"),
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Add new item to list"),
            rx.form(
                rx.flex(
                    # Input-Feld (name="item_to_add" ist der Schlüssel für das Dictionary)
                    rx.input(placeholder="New item", name="item_to_add", required=True),
                    
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="soft",
                                color_scheme="gray",
                            ),
                        ),
                        rx.dialog.close(
                            rx.button("Submit", type="submit"),
                        ),
                        spacing="3",
                        justify="end",
                    ),
                    direction="column",
                    spacing="4",
                ),
                on_submit=State.add_to_list,
                reset_on_submit=True,  # Setze dies auf True, damit das Feld danach wieder leer ist
            ),
            max_width="450px",
        ),
    )

#for dashboard
def index() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Users",
                        size="4",
                        weight="bold",
                        color=rx.color("slate", 12),
                        text_align="left",
                        width="100%",
                    ),
                    rx.text(
                        "Add customers and watch the chart update.",
                        size="2",
                        color=rx.color("slate", 10),
                        text_align="left",
                        width="100%",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                add_customer_button(),
                align="center",
                width="100%",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Name"),
                        rx.table.column_header_cell("Email"),
                        rx.table.column_header_cell("Gender"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(State.users, show_user),
                ),
                variant="surface",
                size="2",
                width="100%",
            ),
            graph(),
            align="stretch",
            width="100%",
            spacing="4",
            padding="1.75em 2em",
        ),
        border=f"1px solid {rx.color('slate', 5)}",
        border_radius="12px",
        margin_y="1em",
        background=rx.color("slate", 1),
    )


#for playground
def playground():
    return rx.box(
        rx.heading(
            "Playground",
            size="8",
            weight="bold",
            color=rx.color("slate", 12),
            align="center",
            margin_y="0.5em",
        ),
        rx.vstack(
            rx.hstack(

                # ── Column 1: Even / Odd ─────────────────────────────
                rx.vstack(
                    rx.heading(
                        "Is the number even or odd?",
                        size="6",
                        weight="bold",
                        color=rx.color("slate", 12),
                        width="100%",
                    ),
                    rx.text(
                        "Please opt out of the field before submitting number",
                        size="2",
                        color=rx.color("slate", 8),
                        width="100%",
                    ),
                    rx.cond(
                        State.count % 2 == 0,
                        rx.text(
                            "The count is even",
                            size="3",
                            weight="bold",
                            color=rx.color("green", 10),
                        ),
                        rx.text(
                            "The count is odd",
                            size="3",
                            weight="bold",
                            color=rx.color("red", 10),
                        ),
                    ),
                    rx.input(
                        placeholder="Enter a number",
                        on_change=State.set_amount_to_add,
                        width="70%",
                    ),
                    rx.button("Submit number", on_click=State.increment_count),
                    spacing="2",
                    align="start",
                    # flex="1" makes this column take an equal share of the
                    # available horizontal space alongside its siblings.
                    # min_width="0" allows the column to shrink below its
                    # natural content width without overflowing the card.
                    flex="1",
                    min_width="0",
                ),

                # ── Column 2: Increment Counter ───────────────────────
                rx.vstack(
                    rx.heading(
                        "Counter: Increment numbers",
                        size="6",
                        weight="bold",
                        color=rx.color("slate", 12),
                        width="100%",
                    ),
                    rx.text(
                        f"Count: {State.increment_num}",
                        size="4",
                        color=rx.color("sky", 10),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            "Increment",
                            on_click=lambda: State.increment(1),
                            color_scheme="grass",
                        ),
                        rx.button(
                            "Increment by 5",
                            on_click=lambda: State.increment(5),
                            color_scheme="green",
                        ),
                    ),
                    rx.hstack(
                        rx.button(
                            "Decrement",
                            on_click=lambda: State.decrement(1),
                            color_scheme="red",
                        ),
                        rx.button(
                            "Decrement by 5",
                            on_click=lambda: State.decrement(5),
                            color_scheme="ruby",
                        ),
                    ),
                    spacing="2",
                    align="start",
                    flex="1",
                    min_width="0",
                ),

                # ── Column 3: Items list ──────────────────────────────
                rx.vstack(
                    rx.hstack(
                        rx.heading(
                            "Items",
                            size="6",
                            weight="bold",
                            color=rx.color("slate", 12),
                            # 1. Wir schützen die Überschrift davor, zerquetscht zu werden:
                        ),
                        button_add_item(),
                        justify="between",  # Schiebt Überschrift nach links, Button nach rechts
                        align="center",     # Zentriert beide vertikal
                        width="100%",
                        ),
                        rx.flex(
                            rx.foreach(State.items, render_item),
                            wrap="wrap",
                            spacing="6",
                            width="100%",
                            padding_top="0.5em"
                        ),
                        #align="start",
                        #width="90%",
                        spacing="3",
                        align="start",
                        flex="1",
                        min_width="0",
                        width="100%",
                    ),
                spacing="4",
                align="start",
                # width="100%" makes the row fill the full card width so
                # the three flex="1" columns divide the space evenly.
                width="100%",
                ),
            ),
            border=f"1px solid {rx.color('slate', 5)}",
            border_radius="12px",
            margin_y="1em",
            background=rx.color("slate", 1),
            padding="1.75em 1.75em",
        ),


app = rx.App(theme=rx.theme(radius="full", accent_color="grass"))
app.add_page(
    index,
    title="Customer Data App",
    description="A simple app to manage customer data.",
    on_load=State.transform_data,
    route="/"
)
app.add_page(playground, route="/playground")

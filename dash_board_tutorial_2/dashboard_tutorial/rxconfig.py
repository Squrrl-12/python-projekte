import reflex as rx

config = rx.Config(
    app_name="dashboard_tutorial",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)
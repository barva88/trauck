MENU_ITEMS = [
    {
        "name": "Dashboard",
        "icon": "tim-icons icon-chart-pie-36",
        "url_name": "pages:index",
    },
    {
        "name": "Educación",
        "icon": "tim-icons icon-book-bookmark",
        "url_name": "education:dashboard",
        "children": [
            {"name": "Resumen", "url_name": "education:dashboard"},
            {"name": "Exámenes", "url_name": "education:bank"},
            {"name": "Historial", "url_name": "education:history"},
        ],
    },
    {
        "name": "Billing",
        "icon": "tim-icons icon-credit-card",
        "url_name": "billing:plans_page",
    },
    {
        "name": "Analytics",
        "icon": "tim-icons icon-chart-bar-32",
        "url_name": "analytics:dashboard",
    },
    {
        "name": "My Profile",
        "icon": "tim-icons icon-badge",
        "url_name": "my_profile:index",
    },
    {
        "name": "Comms",
        "icon": "tim-icons icon-sound-wave",
        "url_name": "comms:inbox",
    },
]
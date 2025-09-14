{
    "name": "Demo theme website",
    "category": "Theme",
    "version": "18.0.1.0.0",
    "author": "TechnoLibre",
    "license": "AGPL-3",
    "sequence": 900,
    "website": "https://technolibre.ca",
    "depends": [
        "website",
        "website_theme_install",
    ],
    "data": [
        "data/theme_website_demo_code_generator_data.xml",
        "views/theme_website_demo_code_generator_templates.xml",
    ],
    "website.assets_frontend": [
        "theme_website_demo_code_generator/static/src/scss/_variables.scss",
        "theme_website_demo_code_generator/static/src/scss/custom.scss",
    ],
    "installable": True,
}

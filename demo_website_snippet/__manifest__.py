{
    "name": "Demo Website Snippet",
    "category": "Website",
    "version": "18.0.1.0.0",
    "author": "TechnoLibre",
    "license": "AGPL-3",
    "website": "https://technolibre.ca",
    "application": True,
    "depends": ["website"],
    "data": ["views/snippets.xml"],
    "website.assets_frontend": [
        "demo_website_snippet/static/src/scss/demo_website_snippet.scss",
        "demo_website_snippet/static/src/js/website.demo_website_snippet.animation.js",
    ],
    "installable": True,
}

{
    "name": "Demo website leaflet",
    "category": "Website",
    "summary": "Leaflet integration in website",
    "version": "17.0.1.0.0",
    "author": "TechnoLibre",
    "license": "AGPL-3",
    "website": "https://technolibre.ca",
    "application": True,
    "depends": [
        "base_geoengine",
        "website",
    ],
    "external_dependencies": {
        "python": ["pyproj"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/demo_website_leaflet_map.xml",
        "views/demo_website_leaflet_map_feature.xml",
        "views/demo_website_leaflet_category.xml",
        "views/menu.xml",
        "views/geoengine.xml",
        "views/snippets.xml",
    ],
    "website.assets_frontend": [
        "demo_website_leaflet/static/src/scss/leaflet.scss"
        "demo_website_leaflet/static/src/scss/leaflet_custom.scss",
        "demo_website_leaflet/static/src/js/website.leaflet.animation.js",
        "demo_website_leaflet/static/src/js/lib/leaflet.js",
        "demo_website_leaflet/static/src/js/lib/leaflet-providers.js",
    ],
    "installable": True,
}

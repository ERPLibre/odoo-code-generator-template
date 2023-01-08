from odoo import http
from odoo.http import request


class DemoWebsiteAngularjsController(http.Controller):
    @http.route(
        ["/demo_website_angularjs/get_nb_website_page"],
        type="json",
        auth="public",
        website=True,
        methods=["POST", "GET"],
        csrf=False,
    )
    def get_page_angularjs(self, **kw):
        env = request.env(context=dict(request.env.context))
        count_page = env["website.page"].search_count(
            [("website_id", "=", env.context.get("website_id"))]
        )
        return {"nb_page": count_page}

from odoo import _, api, fields, models


class DemoModel3PortalDiagram(models.Model):
    _name = "demo.model_3.portal.diagram"
    _inherit = "portal.mixin"
    _description = "demo_model_3_portal_diagram"

    name = fields.Char()

    diagram_demo2_ids = fields.One2many(
        comodel_name="demo.model_2.portal",
        inverse_name="diagram_id",
        string="One2Many demo 2",
    )

    diagram_demo_ids = fields.One2many(
        comodel_name="demo.model.portal",
        inverse_name="diagram_id",
        string="One2Many demo",
    )

    def action_open_diagram(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "demo_portal"
            ".demo_model_3_portal_diagram_demo_model_3_portal_diagram"
            "_action_window"
        )
        action["res_id"] = self.id
        action["views"] = [(False, "diagram")]
        return action

    def _compute_access_url(self):
        # This is a comment need it for test, thanks
        super(DemoModel3PortalDiagram, self)._compute_access_url()
        for demo_model_3_portal_diagram in self:
            demo_model_3_portal_diagram.access_url = (
                "/my/demo_model_3_portal_diagram/%s"
                % demo_model_3_portal_diagram.id
            )

import logging
import os

from odoo import SUPERUSER_ID, _, api, fields, models

_logger = logging.getLogger(__name__)

MODULE_NAME = "code_generator"


def post_init_hook(cr, e):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        # The path of the actual file
        # path_module_generate = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

        short_name = MODULE_NAME.replace("_", " ").title()

        # Add code generator
        categ_id = env["ir.module.category"].search(
            [("name", "=", "Extra Tools")], limit=1
        )
        value = {
            "shortdesc": short_name,
            "name": MODULE_NAME,
            "license": "AGPL-3",
            "category_id": categ_id.id,
            "summary": "Code Generator Module",
            "author": "Mathben (mathben@technolibre.ca)",
            "website": "",
            "application": True,
            "enable_sync_code": True,
            # "path_sync_code": path_module_generate,
            "icon": os.path.join(
                os.path.dirname(__file__),
                "static",
                "description",
                "code_generator_icon.png",
            ),
        }

        # TODO HUMAN: enable your functionality to generate
        value["enable_sync_template"] = True
        value["ignore_fields"] = ""
        value["post_init_hook_show"] = True
        value["uninstall_hook_show"] = False
        value["post_init_hook_feature_code_generator"] = True
        value["uninstall_hook_feature_code_generator"] = False

        value["hook_constant_code"] = f'MODULE_NAME = "{MODULE_NAME}"'

        code_generator_id = env["code.generator.module"].create(value)

        # Add dependencies
        lst_depend_module = ["base", "mail"]
        code_generator_id.add_module_dependency(lst_depend_module)

        # Add/Update Code Generator Act Window
        model_model = "code.generator.act_window"
        model_name = "code_generator_act_window"
        dct_field = {
            "code_generator_id": {
                "field_description": "Code Generator",
                "relation": "code.generator.module",
                "required": True,
                "ttype": "many2one",
            },
            "id_name": {
                "field_description": "Action id",
                "help": "Specify id name of this action window.",
                "ttype": "char",
            },
            "is_wizard": {
                "field_description": "Is Wizard",
                "ttype": "boolean",
            },
            "model_name": {
                "field_description": "Model Name",
                "help": "The associate model, if empty, no association.",
                "ttype": "char",
            },
            "target": {
                "field_description": "Target Window",
                "selection": (
                    "[('current', 'Current Window'), ('new', 'New Window'),"
                    " ('inline', 'Inline Edit'), ('fullscreen', 'Full"
                    " Screen'), ('main', 'Main action of Current Window')]"
                ),
                "ttype": "selection",
            },
            "view_mode": {
                "field_description": "View Mode",
                "help": "The sequence of view mode.",
                "ttype": "char",
            },
            "view_type": {
                "field_description": "View Type",
                "help": "The default view for this action window.",
                "ttype": "char",
            },
        }
        model_code_generator_act_window = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Code Generator Add Controller Wizard
        model_model = "code.generator.add.controller.wizard"
        model_name = "code_generator_add_controller_wizard"
        dct_field = {
            "code_generator_id": {
                "field_description": "Code Generator",
                "relation": "code.generator.module",
                "required": True,
                "ttype": "many2one",
            },
            "field_ids": {
                "field_description": "Fields",
                "help": "Select the field you want to inherit or import data.",
                "relation": "ir.model.fields",
                "ttype": "many2many",
            },
            "model_ids": {
                "field_description": "Models",
                "help": "Select the model you want to inherit or import data.",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "user_id": {
                "field_description": "User",
                "relation": "res.users",
                "required": True,
                "ttype": "many2one",
            },
        }
        model_code_generator_add_controller_wizard = (
            code_generator_id.add_update_model(
                model_model,
                model_name,
                dct_field=dct_field,
            )
        )

        # Add/Update Code Generator Add Model Wizard
        model_model = "code.generator.add.model.wizard"
        model_name = "code_generator_add_model_wizard"
        dct_field = {
            "clear_fields_blacklist": {
                "field_description": "Clear field blacklisted",
                "help": "Erase all blacklisted fields when enable.",
                "ttype": "boolean",
            },
            "code_generator_id": {
                "field_description": "Code Generator",
                "relation": "code.generator.module",
                "required": True,
                "ttype": "many2one",
            },
            "field_ids": {
                "field_description": "Fields",
                "help": "Select the field you want to inherit or import data.",
                "relation": "ir.model.fields",
                "ttype": "many2many",
            },
            "model_ids": {
                "field_description": "Models",
                "help": "Select the model you want to inherit or import data.",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "option_adding": {
                "field_description": "Option Adding",
                "help": """Inherit to inherit a new model.
Nomenclator to export data.""",
                "required": True,
                "selection": (
                    "[('inherit', 'Inherit Model'), ('nomenclator',"
                    " 'Nomenclator')]"
                ),
                "ttype": "selection",
            },
            "option_blacklist": {
                "field_description": "Option Blacklist",
                "help": """When whitelist, all selected fields will be added.
When blacklist, all selected fields will be ignored.""",
                "required": True,
                "selection": (
                    "[('blacklist', 'Blacklist'), ('whitelist', 'Whitelist')]"
                ),
                "ttype": "selection",
            },
            "user_id": {
                "field_description": "User",
                "relation": "res.users",
                "required": True,
                "ttype": "many2one",
            },
        }
        model_code_generator_add_model_wizard = (
            code_generator_id.add_update_model(
                model_model,
                model_name,
                dct_field=dct_field,
            )
        )

        # Add/Update Code Generator Generate Views Wizard
        model_model = "code.generator.generate.views.wizard"
        model_name = "code_generator_generate_views_wizard"
        dct_field = {
            "all_model": {
                "field_description": "All models",
                "help": (
                    "Generate with all existing model, or select manually."
                ),
                "ttype": "boolean",
            },
            "clear_all_access": {
                "field_description": "Clear access",
                "help": "Clear all access/permission before execute.",
                "ttype": "boolean",
            },
            "clear_all_act_window": {
                "field_description": "Clear actions windows",
                "help": "Clear all actions windows before execute.",
                "ttype": "boolean",
            },
            "clear_all_menu": {
                "field_description": "Clear menus",
                "help": "Clear all menus before execute.",
                "ttype": "boolean",
            },
            "clear_all_view": {
                "field_description": "Clear views",
                "help": "Clear all views before execute.",
                "ttype": "boolean",
            },
            "code_generator_id": {
                "field_description": "Code Generator",
                "relation": "code.generator.module",
                "required": True,
                "ttype": "many2one",
            },
            "code_generator_view_ids": {
                "field_description": "Code Generator View",
                "relation": "code.generator.view",
                "ttype": "many2many",
            },
            "date": {
                "field_description": "Date",
                "required": True,
                "ttype": "date",
            },
            "disable_generate_access": {
                "field_description": "Disable Generate Access",
                "help": "Disable security access generation.",
                "ttype": "boolean",
            },
            "disable_generate_menu": {
                "field_description": "Disable Generate Menu",
                "help": "Disable menu generation.",
                "ttype": "boolean",
            },
            "enable_generate_all": {
                "field_description": "Enable all feature",
                "help": "Generate with all feature.",
                "ttype": "boolean",
            },
            "selected_model_calendar_view_ids": {
                "field_description": "Selected Model Calendar View",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "selected_model_diagram_view_ids": {
                "field_description": "Selected Model Diagram View",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "selected_model_form_view_ids": {
                "field_description": "Selected Model Form View",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "selected_model_graph_view_ids": {
                "field_description": "Selected Model Graph View",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "selected_model_kanban_view_ids": {
                "field_description": "Selected Model Kanban View",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "selected_model_pivot_view_ids": {
                "field_description": "Selected Model Pivot View",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "selected_model_search_view_ids": {
                "field_description": "Selected Model Search View",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "selected_model_timeline_view_ids": {
                "field_description": "Selected Model Timeline View",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "selected_model_tree_view_ids": {
                "field_description": "Selected Model Tree View",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "user_id": {
                "field_description": "User",
                "relation": "res.users",
                "required": True,
                "ttype": "many2one",
            },
        }
        model_code_generator_generate_views_wizard = (
            code_generator_id.add_update_model(
                model_model,
                model_name,
                dct_field=dct_field,
            )
        )

        # Add/Update Code Generator Ir Model Dependency
        model_model = "code.generator.ir.model.dependency"
        model_name = "code_generator_ir_model_dependency"
        dct_field = {
            "depend_id": {
                "field_description": "Dependency",
                "relation": "ir.model",
                "ttype": "many2one",
            },
        }
        model_code_generator_ir_model_dependency = (
            code_generator_id.add_update_model(
                model_model,
                model_name,
                dct_field=dct_field,
            )
        )

        # Add/Update Code Generator Ir Model Fields
        model_model = "code.generator.ir.model.fields"
        model_name = "code_generator_ir_model_fields"
        dct_field = {
            "code_generator_compute": {
                "field_description": "Compute Code Generator",
                "help": "Compute method to code_generator_writer.",
                "ttype": "char",
            },
            "comment_after": {
                "field_description": "Comment after field",
                "help": (
                    "Will show comment after writing field in python. Support"
                    " multiline. The comment is after if at the end of file."
                ),
                "ttype": "char",
            },
            "comment_before": {
                "field_description": "Comment before field",
                "help": (
                    "Will show comment before writing field in python. Support"
                    " multiline."
                ),
                "ttype": "char",
            },
            "default_lambda": {
                "field_description": "Default lambda value",
                "ttype": "char",
            },
            "field_context": {
                "field_description": "Field Context",
                "ttype": "char",
            },
            "filter_field_attribute": {
                "field_description": "Filter Field Attribute",
                "help": (
                    "Separate by ; to enumerate your attribute to filter, like"
                    " a whitelist of attributes field."
                ),
                "ttype": "char",
            },
            "is_show_whitelist_model_inherit": {
                "field_description": "Show in whitelist model inherit",
                "help": (
                    "If a field in model is in whitelist, will be show in"
                    " generated model."
                ),
                "ttype": "boolean",
            },
            "m2o_fields": {
                "field_description": "Fields",
                "relation": "ir.model.fields",
                "ttype": "many2one",
            },
            "m2o_module": {
                "field_description": "Module",
                "help": "Module",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
            "nomenclature_blacklist": {
                "field_description": "Ignore from nomenclature.",
                "ttype": "boolean",
            },
            "nomenclature_whitelist": {
                "field_description": "Force to nomenclature.",
                "ttype": "boolean",
            },
            "selection": {
                "field_description": "Selection Options",
                "help": (
                    "List of options for a selection field, specified as a"
                    " Python expression defining a list of (key, label) pairs."
                    " For example: [('blue','Blue'),('yellow','Yellow')]"
                ),
                "ttype": "char",
            },
        }
        model_code_generator_ir_model_fields = (
            code_generator_id.add_update_model(
                model_model,
                model_name,
                dct_field=dct_field,
            )
        )

        # Add/Update Code Generator Menu
        model_model = "code.generator.menu"
        model_name = "code_generator_menu"
        dct_field = {
            "code_generator_id": {
                "field_description": "Code Generator",
                "relation": "code.generator.module",
                "required": True,
                "ttype": "many2one",
            },
            "id_name": {
                "field_description": "Menu id",
                "help": "Specify id name of this menu.",
                "ttype": "char",
            },
            "ignore_act_window": {
                "field_description": "Ignore Act Window",
                "help": "Set True to force no act_window, like a parent menu.",
                "ttype": "boolean",
            },
            "m2o_act_window": {
                "field_description": "Action Windows",
                "help": "Act window to open when click on this menu.",
                "relation": "code.generator.act_window",
                "ttype": "many2one",
            },
            "parent_id_name": {
                "field_description": "Menu parent id",
                "help": "Specify id name of parent menu, optional.",
                "ttype": "char",
            },
            "sequence": {
                "field_description": "Sequence",
                "ttype": "integer",
            },
            "web_icon": {
                "field_description": "Web Icon",
                "help": "Icon menu",
                "ttype": "char",
            },
        }
        model_code_generator_menu = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Code Generator Model Code
        model_model = "code.generator.model.code"
        model_name = "code_generator_model_code"
        dct_field = {
            "code": {
                "field_description": "Code of pre_init_hook",
                "ttype": "text",
            },
            "decorator": {
                "field_description": "Decorator",
                "help": "Like @api.model. Use ; for multiple decorator.",
                "ttype": "char",
            },
            "is_templated": {
                "field_description": "Templated",
                "help": "Code for code generator from template.",
                "ttype": "boolean",
            },
            "is_wip": {
                "field_description": "Work in progress",
                "help": "Temporary function to be fill later.",
                "ttype": "boolean",
            },
            "m2o_model": {
                "field_description": "Model",
                "help": "Model",
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "m2o_module": {
                "field_description": "Module",
                "help": "Module",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
            "param": {
                "field_description": "Param",
                "help": "Like : name,color",
                "ttype": "char",
            },
            "returns": {
                "field_description": "Return type",
                "help": "Annotation to return type value.",
                "ttype": "char",
            },
            "sequence": {
                "field_description": "Sequence",
                "help": "Order of sequence code.",
                "ttype": "integer",
            },
        }
        model_code_generator_model_code = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Code Generator Model Code Import
        model_model = "code.generator.model.code.import"
        model_name = "code_generator_model_code_import"
        dct_field = {
            "code": {
                "field_description": "Code",
                "help": "Code of import header of python file",
                "ttype": "text",
            },
            "is_templated": {
                "field_description": "Templated",
                "help": "Code for code generator from template.",
                "ttype": "boolean",
            },
            "m2o_model": {
                "field_description": "Model",
                "help": "Model",
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "m2o_module": {
                "field_description": "Module",
                "help": "Module",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
            "sequence": {
                "field_description": "Sequence",
                "help": "Order of sequence code.",
                "ttype": "integer",
            },
        }
        model_code_generator_model_code_import = (
            code_generator_id.add_update_model(
                model_model,
                model_name,
                dct_field=dct_field,
            )
        )

        # Add/Update Code Generator Module
        model_model = "code.generator.module"
        model_name = "code_generator_module"
        dct_field = {
            "application": {
                "field_description": "Application",
                "ttype": "boolean",
            },
            "author": {
                "field_description": "Author",
                "ttype": "char",
            },
            "auto_install": {
                "field_description": "Automatic Installation",
                "help": (
                    "An auto-installable module is automatically installed by"
                    " the system when all its dependencies are satisfied. If"
                    " the module has no dependency, it is always installed."
                ),
                "ttype": "boolean",
            },
            "category_id": {
                "field_description": "Category",
                "relation": "ir.module.category",
                "ttype": "many2one",
            },
            "contributors": {
                "field_description": "Contributors",
                "ttype": "text",
            },
            "demo": {
                "field_description": "Demo Data",
                "ttype": "boolean",
            },
            "description": {
                "field_description": "Description",
                "ttype": "text",
            },
            "description_html": {
                "field_description": "Description HTML",
                "ttype": "html",
            },
            "disable_fix_code_generator_sequence": {
                "field_description": "Disable fix sequence",
                "help": (
                    "Don't force sequence of model in view, if True, always"
                    " auto mode."
                ),
                "ttype": "boolean",
            },
            "disable_generate_access": {
                "field_description": "Disable Generate Access",
                "help": "Disable the writing access.",
                "ttype": "boolean",
            },
            "enable_cg_generate_portal": {
                "field_description": "Wizard enable code generator portal",
                "help": "Add template of portal to wizard.",
                "ttype": "boolean",
            },
            "enable_cg_portal_enable_create": {
                "field_description": "Enable Cg Portal Enable Create",
                "help": "Template will generate 'portal_enable_create'.",
                "ttype": "boolean",
            },
            "enable_generate_portal": {
                "field_description": "Wizard enable portal",
                "help": "Add template of portal to wizard.",
                "ttype": "boolean",
            },
            "enable_pylint_check": {
                "field_description": "Enable Pylint check",
                "help": "Show pylint result at the end of generation.",
                "ttype": "boolean",
            },
            "enable_sync_code": {
                "field_description": "Enable Sync Code",
                "help": "Will sync with code on drive when generate.",
                "ttype": "boolean",
            },
            "enable_sync_template": {
                "field_description": "Sync generated code",
                "help": (
                    "Read generated code to fill the generator with fields."
                ),
                "ttype": "boolean",
            },
            "enable_template_code_generator_demo": {
                "field_description": "Functions code generator demo",
                "help": (
                    "Support help to use code generator with functionality"
                    " variables."
                ),
                "ttype": "boolean",
            },
            "enable_template_website_snippet_view": {
                "field_description": "Template website snippet",
                "help": (
                    "Add template website snippet, block drag and drop in"
                    " website builder."
                ),
                "ttype": "boolean",
            },
            "enable_template_wizard_view": {
                "field_description": "Template wizard",
                "help": "Add template wizard.",
                "ttype": "boolean",
            },
            "exclude_dependencies_str": {
                "field_description": "Exclude Dependencies Str",
                "help": (
                    "Exclude from list dependencies_id about"
                    " code.generator.module.dependency name separate by ;"
                ),
                "ttype": "char",
            },
            "export_website_optimize_binary_image": {
                "field_description": "Export Website Optimize Binary Image",
                "help": (
                    "Associate with nomenclator export data. Search url"
                    " /web/image/ in website page and remove ir.attachment who"
                    " is not into view. Remove duplicate same attachment,"
                    " image or scss."
                ),
                "ttype": "boolean",
            },
            "force_generic_template_wizard_view": {
                "field_description": "Force template wizard",
                "help": "Use default value to generate template wizard.",
                "ttype": "boolean",
            },
            "header_manifest": {
                "field_description": "Header",
                "help": "Header comment in __manifest__.py file.",
                "ttype": "text",
            },
            "hook_constant_code": {
                "field_description": "Code constant",
                "help": "Code in the begin of hook file.",
                "ttype": "text",
            },
            "icon": {
                "field_description": "Icon URL",
                "ttype": "char",
            },
            "icon_child_image": {
                "field_description": "Generated icon",
                "ttype": "binary",
            },
            "icon_image": {
                "field_description": "Icon",
                "ttype": "binary",
            },
            "icon_real_image": {
                "field_description": "Replace icon",
                "help": "This will replace icon_image",
                "ttype": "binary",
            },
            "ignore_fields": {
                "field_description": "Ignored field",
                "help": (
                    "Ignore field when enable_sync_template, use ; to separate"
                    " field."
                ),
                "ttype": "char",
            },
            "installed_version": {
                "field_description": "Latest Version",
                "ttype": "char",
            },
            "latest_version": {
                "field_description": "Installed Version",
                "ttype": "char",
            },
            "license": {
                "field_description": "License",
                "selection": (
                    "[('GPL-2', 'GPL Version 2'), ('GPL-2 or any later"
                    " version', 'GPL-2 or later version'), ('GPL-3', 'GPL"
                    " Version 3'), ('GPL-3 or any later version', 'GPL-3 or"
                    " later version'), ('AGPL-3', 'Affero GPL-3'), ('LGPL-3',"
                    " 'LGPL Version 3'), ('Other OSI approved licence', 'Other"
                    " OSI Approved Licence'), ('OEEL-1', 'Odoo Enterprise"
                    " Edition License v1.0'), ('OPL-1', 'Odoo Proprietary"
                    " License v1.0'), ('Other proprietary', 'Other"
                    " Proprietary')]"
                ),
                "ttype": "selection",
            },
            "list_scss_process_hook": {
                "field_description": "List Scss Process Hook",
                "help": (
                    "READONLY, use by computation. Value are separated by ;."
                    " List of xml_id to compute scss in hook when export"
                    " website data with scss modification."
                ),
                "ttype": "char",
            },
            "maintainer": {
                "field_description": "Maintainer",
                "ttype": "char",
            },
            "menus_by_module": {
                "field_description": "Menus",
                "ttype": "text",
            },
            "nomenclator_only": {
                "field_description": "Only export data",
                "help": "Useful to export data with existing model.",
                "ttype": "boolean",
            },
            "path_sync_code": {
                "field_description": "Directory",
                "help": (
                    "Path directory where sync the code, will erase directory"
                    " and generate new code."
                ),
                "ttype": "char",
            },
            "post_init_hook_code": {
                "field_description": "Code of post_init_hook",
                "ttype": "text",
            },
            "post_init_hook_feature_code_generator": {
                "field_description": "Code generator post_init_hook",
                "help": (
                    "Add code to use the code generator on post_init_hook."
                ),
                "ttype": "boolean",
            },
            "post_init_hook_feature_general_conf": {
                "field_description": "General conf post_init_hook",
                "help": (
                    "Add code to update general configurations on"
                    " post_init_hook."
                ),
                "ttype": "boolean",
            },
            "post_init_hook_show": {
                "field_description": "Show post_init_hook",
                "ttype": "boolean",
            },
            "pre_init_hook_code": {
                "field_description": "Code of pre_init_hook",
                "ttype": "text",
            },
            "pre_init_hook_feature_general_conf": {
                "field_description": "General conf pre_init_hook",
                "help": (
                    "Add code to update general configurations on"
                    " pre_init_hook."
                ),
                "ttype": "boolean",
            },
            "pre_init_hook_show": {
                "field_description": "Show pre_init_hook",
                "ttype": "boolean",
            },
            "published_version": {
                "field_description": "Published Version",
                "ttype": "char",
            },
            "reports_by_module": {
                "field_description": "Reports",
                "ttype": "text",
            },
            "sequence": {
                "field_description": "Sequence",
                "ttype": "integer",
            },
            "shortdesc": {
                "field_description": "Module Name",
                "required": True,
                "ttype": "char",
            },
            "state": {
                "field_description": "Status",
                "selection": (
                    "[('uninstallable', 'Uninstallable'), ('uninstalled', 'Not"
                    " Installed'), ('installed', 'Installed'), ('to upgrade',"
                    " 'To be upgraded'), ('to remove', 'To be removed'), ('to"
                    " install', 'To be installed')]"
                ),
                "ttype": "selection",
            },
            "summary": {
                "field_description": "Summary",
                "ttype": "char",
            },
            "template_auto_export_data": {
                "field_description": "Template Auto Export Data",
                "ttype": "boolean",
            },
            "template_auto_export_data_exclude_model": {
                "field_description": "Template Auto Export Data Exclude Model",
                "help": (
                    "List of model separate by ; to be exclude from export"
                    " data, because it's internal data."
                ),
                "ttype": "char",
            },
            "template_generate_website_enable_javascript": {
                "field_description": (
                    "Template Generate Website Enable Javascript"
                ),
                "ttype": "boolean",
            },
            "template_generate_website_snippet_controller_feature": {
                "field_description": "website snippet controller feature",
                "ttype": "char",
            },
            "template_generate_website_snippet_generic_model": {
                "field_description": (
                    "website snippet feature with generic model"
                ),
                "help": (
                    "Separate model name by ';' to create a list. Will"
                    " generate field of all this model."
                ),
                "ttype": "char",
            },
            "template_generate_website_snippet_type": {
                "field_description": "Template Generate Website Snippet Type",
                "help": "Choose content,effect,feature,structure",
                "ttype": "char",
            },
            "template_ignore_export_data": {
                "field_description": "Template Ignore Export Data",
                "ttype": "boolean",
            },
            "template_inherit_model_name": {
                "field_description": "Functions models inherit",
                "help": (
                    "Add model from list, separate by ';' and generate"
                    " template."
                ),
                "ttype": "char",
            },
            "template_model_name": {
                "field_description": "Functions models",
                "help": (
                    "Add model from list, separate by ';' and generate"
                    " template."
                ),
                "ttype": "char",
            },
            "template_module_id": {
                "field_description": "Template module id",
                "help": "Child module to generate.",
                "relation": "ir.module.module",
                "ttype": "many2one",
            },
            "template_module_name": {
                "field_description": "Generated module name",
                "help": (
                    "Can be empty in case of code_generator_demo, else it's"
                    " the module name goal to generate."
                ),
                "ttype": "char",
            },
            "template_module_path_generated_extension": {
                "field_description": (
                    "Path of os.path value to generated path module"
                ),
                "help": (
                    "Add parameters of os.path directory where module is"
                    " generated."
                ),
                "ttype": "char",
            },
            "to_buy": {
                "field_description": "Odoo Enterprise Module",
                "ttype": "boolean",
            },
            "uninstall_hook_code": {
                "field_description": "Code of uninstall_hook",
                "ttype": "text",
            },
            "uninstall_hook_feature_code_generator": {
                "field_description": "Code generator uninstall_hook",
                "help": (
                    "Add code to use the code generator on uninstall_hook."
                ),
                "ttype": "boolean",
            },
            "uninstall_hook_feature_general_conf": {
                "field_description": "General conf uninstall_hook",
                "help": (
                    "Add code to update general configurations on"
                    " uninstall_hook."
                ),
                "ttype": "boolean",
            },
            "uninstall_hook_show": {
                "field_description": "Show uninstall_hook",
                "ttype": "boolean",
            },
            "url": {
                "field_description": "URL",
                "ttype": "char",
            },
            "views_by_module": {
                "field_description": "Views",
                "ttype": "text",
            },
            "website": {
                "field_description": "Website",
                "ttype": "char",
            },
        }
        model_code_generator_module = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Generate server action
        # action_server view
        act_server_id = env["ir.actions.server"].search(
            [
                ("name", "=", "Generate code"),
                ("model_id", "=", model_code_generator_module.id),
            ]
        )
        if not act_server_id:
            act_server_id = env["ir.actions.server"].create(
                {
                    "name": "Generate code",
                    "model_id": model_code_generator_module.id,
                    "binding_model_id": model_code_generator_module.id,
                    "state": "code",
                    "code": """if records:
    action = {"type": "ir.actions.act_url", "target": "self", "url": "/code_generator/%s" % ','.join(records.mapped(lambda r: str(r.id)))}""",
                }
            )

            # Add record id name
            env["ir.model.data"].create(
                {
                    "name": "code_generator_module_actionserver",
                    "model": "ir.actions.server",
                    "module": MODULE_NAME,
                    "res_id": act_server_id.id,
                    "noupdate": True,
                }
            )

        # Add/Update Code Generator Module Dependency
        model_model = "code.generator.module.dependency"
        model_name = "code_generator_module_dependency"
        dct_field = {
            "depend_id": {
                "field_description": "Dependency",
                "relation": "ir.module.module",
                "ttype": "many2one",
            },
            "module_id": {
                "field_description": "Module",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
            "state": {
                "field_description": "Status",
                "selection": (
                    "[('uninstallable', 'Uninstallable'), ('uninstalled', 'Not"
                    " Installed'), ('installed', 'Installed'), ('to upgrade',"
                    " 'To be upgraded'), ('to remove', 'To be removed'), ('to"
                    " install', 'To be installed'), ('unknown', 'Unknown')]"
                ),
                "ttype": "selection",
            },
        }
        model_code_generator_module_dependency = (
            code_generator_id.add_update_model(
                model_model,
                model_name,
                dct_field=dct_field,
            )
        )

        # Add/Update Code Generator Module External Dependency
        model_model = "code.generator.module.external.dependency"
        model_name = "code_generator_module_external_dependency"
        dct_field = {
            "application_type": {
                "field_description": "Application Type",
                "selection": "[('python', 'python'), ('bin', 'bin')]",
                "ttype": "selection",
            },
            "depend": {
                "field_description": "Dependency name",
                "ttype": "char",
            },
            "is_template": {
                "field_description": "Is template",
                "help": "Will be affect template module.",
                "ttype": "boolean",
            },
            "module_id": {
                "field_description": "Module",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
        }
        model_code_generator_module_external_dependency = (
            code_generator_id.add_update_model(
                model_model,
                model_name,
                dct_field=dct_field,
            )
        )

        # Add/Update Code Generator Module Template Dependency
        model_model = "code.generator.module.template.dependency"
        model_name = "code_generator_module_template_dependency"
        dct_field = {
            "depend_id": {
                "field_description": "Dependency",
                "relation": "ir.module.module",
                "ttype": "many2one",
            },
            "module_id": {
                "field_description": "Module",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
            "state": {
                "field_description": "Status",
                "selection": (
                    "[('uninstallable', 'Uninstallable'), ('uninstalled', 'Not"
                    " Installed'), ('installed', 'Installed'), ('to upgrade',"
                    " 'To be upgraded'), ('to remove', 'To be removed'), ('to"
                    " install', 'To be installed'), ('unknown', 'Unknown')]"
                ),
                "ttype": "selection",
            },
        }
        model_code_generator_module_template_dependency = (
            code_generator_id.add_update_model(
                model_model,
                model_name,
                dct_field=dct_field,
            )
        )

        # Add/Update Code Generator Pyclass
        model_model = "code.generator.pyclass"
        model_name = "code_generator_pyclass"
        dct_field = {
            "module": {
                "field_description": "Class path",
                "help": "Class path",
                "ttype": "char",
            },
        }
        model_code_generator_pyclass = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Code Generator View
        model_model = "code.generator.view"
        model_name = "code_generator_view"
        dct_field = {
            "code_generator_id": {
                "field_description": "Code Generator",
                "relation": "code.generator.module",
                "required": True,
                "ttype": "many2one",
            },
            "has_body_sheet": {
                "field_description": "Sheet format",
                "help": "Use sheet presentation for body of form view.",
                "ttype": "boolean",
            },
            "id_name": {
                "field_description": "View id",
                "help": "Specify id name of this view.",
                "ttype": "char",
            },
            "inherit_view_name": {
                "field_description": "Inherit View Name",
                "help": (
                    "Set inherit view name, use record id (ir.model.data)."
                ),
                "ttype": "char",
            },
            "m2o_model": {
                "field_description": "Code generator Model",
                "help": "Model related with this report",
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "view_attr_class": {
                "field_description": "Class attribute",
                "ttype": "char",
            },
            "view_attr_decoration_bf": {
                "field_description": "Decoration-bf attribute",
                "ttype": "char",
            },
            "view_attr_decoration_danger": {
                "field_description": "Decoration-danger attribute",
                "ttype": "char",
            },
            "view_attr_decoration_info": {
                "field_description": "Decoration-info attribute",
                "ttype": "char",
            },
            "view_attr_decoration_it": {
                "field_description": "Decoration-it attribute",
                "ttype": "char",
            },
            "view_attr_decoration_muted": {
                "field_description": "Decoration-muted attribute",
                "ttype": "char",
            },
            "view_attr_decoration_primary": {
                "field_description": "Decoration-primary attribute",
                "ttype": "char",
            },
            "view_attr_decoration_success": {
                "field_description": "Decoration-success attribute",
                "ttype": "char",
            },
            "view_attr_decoration_warning": {
                "field_description": "Decoration-warning attribute",
                "ttype": "char",
            },
            "view_attr_string": {
                "field_description": "String attribute",
                "ttype": "char",
            },
            "view_item_ids": {
                "field_description": "View item",
                "help": "Item view to add in this view.",
                "relation": "code.generator.view.item",
                "ttype": "many2many",
            },
            "view_name": {
                "field_description": "View name",
                "ttype": "char",
            },
            "view_type": {
                "field_description": "View Type",
                "help": "Choose view type to generate.",
                "selection": (
                    "[('activity', 'Activity'), ('calendar', 'Calendar'),"
                    " ('diagram', 'Diagram'), ('form', 'Form'), ('graph',"
                    " 'Graph'), ('kanban', 'Kanban'), ('pivot', 'Pivot'),"
                    " ('search', 'Search'), ('timeline', 'Timeline'), ('tree',"
                    " 'Tree')]"
                ),
                "ttype": "selection",
            },
        }
        model_code_generator_view = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Code Generator View Item
        model_model = "code.generator.view.item"
        model_name = "code_generator_view_item"
        dct_field = {
            "action_name": {
                "field_description": "Action name",
                "ttype": "char",
            },
            "aria_label": {
                "field_description": "Aria Label",
                "help": "aria-label attribute",
                "ttype": "char",
            },
            "attrs": {
                "field_description": "Attributes",
                "help": (
                    "Specific condition, search attrs for more information."
                ),
                "ttype": "char",
            },
            "background_type": {
                "field_description": "Background Type",
                "help": "Choose background color of HTML.",
                "selection": (
                    "[('', ''), ('bg-success', 'Success'), ('bg-success-full',"
                    " 'Success full'), ('bg-warning', 'Warning'),"
                    " ('bg-warning-full', 'Warning full'), ('bg-info',"
                    " 'Info'), ('bg-info-full', 'Info full'), ('bg-danger',"
                    " 'Danger'), ('bg-danger-full', 'Danger full'),"
                    " ('bg-light', 'Light'), ('bg-dark', 'Dark')]"
                ),
                "ttype": "selection",
            },
            "binding_type": {
                "field_description": "Binding Type",
                "help": "Button type, the binding method.",
                "selection": (
                    "[('', ''), ('object', 'Object'), ('action', 'Action'),"
                    " ('server', 'Server')]"
                ),
                "ttype": "selection",
            },
            "button_type": {
                "field_description": "Button Type",
                "help": "Choose item type to generate.",
                "selection": (
                    "[('', ''), ('btn-default', 'Default'), ('btn-primary',"
                    " 'Primary'), ('btn-secondary', 'Secondary'), ('btn-link',"
                    " 'Link'), ('btn-success', 'Success'), ('btn-warning',"
                    " 'Warning'), ('btn-danger', 'Danger'), ('oe_highlight',"
                    " 'Highlight'), ('oe_stat_button', 'Statistic')]"
                ),
                "ttype": "selection",
            },
            "class_attr": {
                "field_description": "Class Attr",
                "help": "Update class attribute",
                "ttype": "char",
            },
            "clickable": {
                "field_description": "Clickable",
                "ttype": "char",
            },
            "colspan": {
                "field_description": "Colspan",
                "help": "Use this to fill more column, check HTML table.",
                "ttype": "integer",
            },
            "context": {
                "field_description": "Context",
                "help": "context attribute",
                "ttype": "char",
            },
            "domain": {
                "field_description": "Domain",
                "help": "domain attribute",
                "ttype": "char",
            },
            "edit_only": {
                "field_description": "Edit only",
                "ttype": "boolean",
            },
            "expand": {
                "field_description": "Expand",
                "ttype": "char",
            },
            "expr": {
                "field_description": "Expr",
                "help": "Example: //field[@name='name']",
                "ttype": "char",
            },
            "filter_domain": {
                "field_description": "Filter Domain",
                "help": "Like domain for field.",
                "ttype": "char",
            },
            "groups": {
                "field_description": "Groups",
                "help": "Limit access to this item by group.",
                "ttype": "char",
            },
            "has_label": {
                "field_description": "Labeled",
                "help": "Label for title.",
                "ttype": "boolean",
            },
            "help": {
                "field_description": "Help",
                "help": "Show help to user about this item.",
                "ttype": "char",
            },
            "icon": {
                "field_description": "Icon",
                "help": "Example fa-television. Only supported with button.",
                "ttype": "char",
            },
            "inner_text": {
                "field_description": "Inner Text",
                "help": "Inner text into div.",
                "ttype": "char",
            },
            "invisible": {
                "field_description": "Invisible",
                "help": "if the item is invisible",
                "ttype": "char",
            },
            "is_help": {
                "field_description": "Is Help",
                "ttype": "boolean",
            },
            "is_invisible": {
                "field_description": "Is Invisible",
                "ttype": "boolean",
            },
            "is_readonly": {
                "field_description": "Is Readonly",
                "ttype": "boolean",
            },
            "is_required": {
                "field_description": "Is Required",
                "ttype": "boolean",
            },
            "item_type": {
                "field_description": "Item Type",
                "help": "Choose item type to generate.",
                "selection": (
                    "[('field', 'Field'), ('button', 'Button'), ('html',"
                    " 'HTML'), ('filter', 'Filter'), ('div', 'Division'),"
                    " ('group', 'Group'), ('xpath', 'Xpath'), ('templates',"
                    " 'Templates'), ('t', 'T'), ('ul', 'UL'), ('li', 'LI'),"
                    " ('i', 'I'), ('strong', 'Strong'), ('#text', 'Texte'),"
                    " ('h1', 'Header 1'), ('h2', 'Header 2'), ('h3', 'Header"
                    " 3'), ('h4', 'Header 4'), ('h5', 'Header 5'),"
                    " ('notebook', 'Notebook'), ('page', 'Page'), ('p',"
                    " 'Paragraph')]"
                ),
                "ttype": "selection",
            },
            "label": {
                "field_description": "Label",
                "ttype": "char",
            },
            "nolabel": {
                "field_description": "Nolabel",
                "help": "Feature for field to remove label.",
                "ttype": "char",
            },
            "options": {
                "field_description": "Options",
                "help": (
                    "More option for this item, usually manage by Javascript."
                ),
                "ttype": "char",
            },
            "parent_id": {
                "field_description": "Parent",
                "relation": "code.generator.view.item",
                "ttype": "many2one",
            },
            "password": {
                "field_description": "Password",
                "help": "Hide character.",
                "ttype": "boolean",
            },
            "placeholder": {
                "field_description": "Placeholder",
                "ttype": "char",
            },
            "position": {
                "field_description": "Position",
                "selection": (
                    "[('inside', 'Inside'), ('replace', 'Replace'), ('after',"
                    " 'After'), ('before', 'Before'), ('attributes',"
                    " 'Attributes'), ('move', 'Move')]"
                ),
                "ttype": "selection",
            },
            "role": {
                "field_description": "Role",
                "help": "role attribute",
                "ttype": "char",
            },
            "section_type": {
                "field_description": "Section Type",
                "help": "Choose item type to generate.",
                "selection": (
                    "[('header', 'Header'), ('title', 'Title'), ('body',"
                    " 'Body'), ('footer', 'Footer')]"
                ),
                "ttype": "selection",
            },
            "sequence": {
                "field_description": "Sequence",
                "ttype": "integer",
            },
            "t_attf_class": {
                "field_description": "T Attf Class",
                "help": "t-attf-class attribute",
                "ttype": "char",
            },
            "t_if": {
                "field_description": "T If",
                "help": "t-if attribute",
                "ttype": "char",
            },
            "t_name": {
                "field_description": "T Name",
                "help": "t_name attribute",
                "ttype": "char",
            },
            "tabindex": {
                "field_description": "Tabindex",
                "help": "Tab index",
                "ttype": "char",
            },
            "title": {
                "field_description": "Title",
                "help": "title attribute",
                "ttype": "char",
            },
            "type": {
                "field_description": "Type",
                "help": "Statistique type.",
                "selection": (
                    "[('row', 'Row'), ('col', 'Col'), ('measure', 'Measure')]"
                ),
                "ttype": "selection",
            },
            "widget": {
                "field_description": "Widget",
                "help": "widget attribute",
                "ttype": "char",
            },
        }
        model_code_generator_view_item = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Code Generator Writer
        model_model = "code.generator.writer"
        model_name = "code_generator_writer"
        dct_field = {
            "basename": {
                "field_description": "Base name",
                "ttype": "char",
            },
            "code_generator_ids": {
                "field_description": "Code Generator",
                "relation": "code.generator.module",
                "ttype": "many2many",
            },
            "list_path_file": {
                "field_description": "List path file",
                "help": "Value are separated by ;",
                "ttype": "char",
            },
            "rootdir": {
                "field_description": "Root dir",
                "ttype": "char",
            },
        }
        model_code_generator_writer = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Model Server Constrain
        model_model = "ir.model.server_constrain"
        model_name = "ir_model_server_constrain"
        dct_field = {
            "constrained": {
                "field_description": "Constrained",
                "help": "Constrained fields, ej: name, age",
                "required": True,
                "ttype": "char",
            },
            "m2o_ir_model": {
                "field_description": "Code generator Model",
                "force_domain": [("transient", "=", False)],
                "help": "Model that will hold this server constrain",
                "relation": "ir.model",
                "required": True,
                "ttype": "many2one",
            },
            "txt_code": {
                "field_description": "Code",
                "help": "Code to execute",
                "required": True,
                "ttype": "text",
            },
        }
        model_ir_model_server_constrain = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Actions Act Url
        model_model = "ir.actions.act_url"
        model_name = "ir_actions_act_url"
        dct_field = {
            "binding_model_id": {
                "field_description": "Binding Model",
                "help": (
                    "Setting a value makes this action available in the"
                    " sidebar for the given model."
                ),
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "binding_type": {
                "field_description": "Binding Type",
                "required": True,
                "selection": (
                    "[('action', 'Action'), ('action_form_only', 'Form-only'),"
                    " ('report', 'Report')]"
                ),
                "ttype": "selection",
            },
            "help": {
                "field_description": "Action Description",
                "help": (
                    "Optional help text for the users with a description of"
                    " the target view, such as its usage and purpose."
                ),
                "ttype": "html",
            },
            "m2o_code_generator": {
                "field_description": "Code Generator",
                "help": "Code Generator relation",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
            "target": {
                "field_description": "Action Target",
                "required": True,
                "selection": (
                    "[('new', 'New Window'), ('self', 'This Window')]"
                ),
                "ttype": "selection",
            },
            "type": {
                "field_description": "Action Type",
                "required": True,
                "ttype": "char",
            },
            "url": {
                "field_description": "Action URL",
                "required": True,
                "ttype": "text",
            },
            "xml_id": {
                "field_description": "External ID",
                "ttype": "char",
            },
        }
        model_ir_actions_act_url = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Actions Act Window
        model_model = "ir.actions.act_window"
        model_name = "ir_actions_act_window"
        dct_field = {
            "auto_search": {
                "field_description": "Auto Search",
                "ttype": "boolean",
            },
            "binding_model_id": {
                "field_description": "Binding Model",
                "help": (
                    "Setting a value makes this action available in the"
                    " sidebar for the given model."
                ),
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "binding_type": {
                "field_description": "Binding Type",
                "required": True,
                "selection": (
                    "[('action', 'Action'), ('action_form_only', 'Form-only'),"
                    " ('report', 'Report')]"
                ),
                "ttype": "selection",
            },
            "context": {
                "field_description": "Context Value",
                "help": (
                    "Context dictionary as Python expression, empty by default"
                    " (Default: {})"
                ),
                "required": True,
                "ttype": "char",
            },
            "domain": {
                "field_description": "Domain Value",
                "help": (
                    "Optional domain filtering of the destination data, as a"
                    " Python expression"
                ),
                "ttype": "char",
            },
            "filter": {
                "field_description": "Filter",
                "ttype": "boolean",
            },
            "groups_id": {
                "field_description": "Groups",
                "relation": "res.groups",
                "ttype": "many2many",
            },
            "help": {
                "field_description": "Action Description",
                "help": (
                    "Optional help text for the users with a description of"
                    " the target view, such as its usage and purpose."
                ),
                "ttype": "html",
            },
            "limit": {
                "field_description": "Limit",
                "help": "Default limit for the list view",
                "ttype": "integer",
            },
            "m2o_res_model": {
                "field_description": "Res Model",
                "help": "Res Model",
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "m2o_src_model": {
                "field_description": "Src Model",
                "help": "Src Model",
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "multi": {
                "field_description": "Restrict to lists",
                "help": (
                    "If checked and the action is bound to a model, it will"
                    " only appear in the More menu on list views"
                ),
                "ttype": "boolean",
            },
            "res_id": {
                "field_description": "Record ID",
                "help": (
                    "Database ID of record to open in form view, when"
                    " ``view_mode`` is set to 'form' only"
                ),
                "ttype": "integer",
            },
            "res_model": {
                "field_description": "Destination Model",
                "help": "Model name of the object to open in the view window",
                "required": True,
                "ttype": "char",
            },
            "search_view": {
                "field_description": "Search View",
                "ttype": "text",
            },
            "search_view_id": {
                "field_description": "Search View Ref.",
                "relation": "ir.ui.view",
                "ttype": "many2one",
            },
            "src_model": {
                "field_description": "Source Model",
                "help": (
                    "Optional model name of the objects on which this action"
                    " should be visible"
                ),
                "ttype": "char",
            },
            "target": {
                "field_description": "Target Window",
                "selection": (
                    "[('current', 'Current Window'), ('new', 'New Window'),"
                    " ('inline', 'Inline Edit'), ('fullscreen', 'Full"
                    " Screen'), ('main', 'Main action of Current Window')]"
                ),
                "ttype": "selection",
            },
            "type": {
                "field_description": "Action Type",
                "required": True,
                "ttype": "char",
            },
            "usage": {
                "field_description": "Action Usage",
                "help": (
                    "Used to filter menu and home actions from the user form."
                ),
                "ttype": "char",
            },
            "view_id": {
                "field_description": "View Ref.",
                "relation": "ir.ui.view",
                "ttype": "many2one",
            },
            "view_mode": {
                "field_description": "View Mode",
                "help": (
                    "Comma-separated list of allowed view modes, such as"
                    " 'form', 'tree', 'calendar', etc. (Default: tree,form)"
                ),
                "required": True,
                "ttype": "char",
            },
            "view_type": {
                "field_description": "View Type",
                "help": (
                    "View type: Tree type to use for the tree view, set to"
                    " 'tree' for a hierarchical tree view, or 'form' for a"
                    " regular list view"
                ),
                "required": True,
                "selection": "[('tree', 'Tree'), ('form', 'Form')]",
                "ttype": "selection",
            },
            "views": {
                "field_description": "Views",
                "help": (
                    "This function field computes the ordered list of views"
                    " that should be enabled when displaying the result of an"
                    " action, federating view mode, views and reference view."
                    " The result is returned as an ordered list of pairs"
                    " (view_id,view_mode)."
                ),
                "ttype": "binary",
            },
            "xml_id": {
                "field_description": "External ID",
                "ttype": "char",
            },
        }
        model_ir_actions_act_window = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Actions Report
        model_model = "ir.actions.report"
        model_name = "ir_actions_report"
        dct_field = {
            "attachment": {
                "field_description": "Save as Attachment Prefix",
                "help": (
                    "This is the filename of the attachment used to store the"
                    " printing result. Keep empty to not save the printed"
                    " reports. You can use a python expression with the object"
                    " and time variables."
                ),
                "ttype": "char",
            },
            "attachment_use": {
                "field_description": "Reload from Attachment",
                "help": (
                    "If you check this, then the second time the user prints"
                    " with same attachment name, it returns the previous"
                    " report."
                ),
                "ttype": "boolean",
            },
            "binding_model_id": {
                "field_description": "Binding Model",
                "help": (
                    "Setting a value makes this action available in the"
                    " sidebar for the given model."
                ),
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "binding_type": {
                "field_description": "Binding Type",
                "required": True,
                "selection": (
                    "[('action', 'Action'), ('action_form_only', 'Form-only'),"
                    " ('report', 'Report')]"
                ),
                "ttype": "selection",
            },
            "groups_id": {
                "field_description": "Groups",
                "relation": "res.groups",
                "ttype": "many2many",
            },
            "help": {
                "field_description": "Action Description",
                "help": (
                    "Optional help text for the users with a description of"
                    " the target view, such as its usage and purpose."
                ),
                "ttype": "html",
            },
            "m2o_model": {
                "field_description": "Code generator Model",
                "help": "Model related with this report",
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "m2o_template": {
                "field_description": "Template",
                "help": "Template related with this report",
                "relation": "ir.ui.view",
                "ttype": "many2one",
            },
            "model": {
                "field_description": "Model Name",
                "required": True,
                "ttype": "char",
            },
            "model_id": {
                "field_description": "Model",
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "multi": {
                "field_description": "On Multiple Doc.",
                "help": (
                    "If set to true, the action will not be displayed on the"
                    " right toolbar of a form view."
                ),
                "ttype": "boolean",
            },
            "paperformat_id": {
                "field_description": "Paper Format",
                "relation": "report.paperformat",
                "ttype": "many2one",
            },
            "print_report_name": {
                "field_description": "Printed Report Name",
                "help": (
                    "This is the filename of the report going to download."
                    " Keep empty to not change the report filename. You can"
                    " use a python expression with the 'object' and 'time'"
                    " variables."
                ),
                "ttype": "char",
            },
            "report_file": {
                "field_description": "Report File",
                "help": (
                    "The path to the main report file (depending on Report"
                    " Type) or empty if the content is in another field"
                ),
                "ttype": "char",
            },
            "report_name": {
                "field_description": "Template Name",
                "help": (
                    "For QWeb reports, name of the template used in the"
                    " rendering. The method 'render_html' of the model"
                    " 'report.template_name' will be called (if any) to give"
                    " the html. For RML reports, this is the LocalService"
                    " name."
                ),
                "required": True,
                "ttype": "char",
            },
            "report_type": {
                "field_description": "Report Type",
                "help": (
                    "The type of the report that will be rendered, each one"
                    " having its own rendering method. HTML means the report"
                    " will be opened directly in your browser PDF means the"
                    " report will be rendered using Wkhtmltopdf and downloaded"
                    " by the user."
                ),
                "required": True,
                "selection": (
                    "[('qweb-html', 'HTML'), ('qweb-pdf', 'PDF'),"
                    " ('qweb-text', 'Text')]"
                ),
                "ttype": "selection",
            },
            "type": {
                "field_description": "Action Type",
                "required": True,
                "ttype": "char",
            },
            "xml_id": {
                "field_description": "External ID",
                "ttype": "char",
            },
        }
        model_ir_actions_report = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Actions Server
        model_model = "ir.actions.server"
        model_name = "ir_actions_server"
        dct_field = {
            "activity_date_deadline_range": {
                "field_description": "Due Date In",
                "ttype": "integer",
            },
            "activity_date_deadline_range_type": {
                "field_description": "Due type",
                "selection": (
                    "[('days', 'Days'), ('weeks', 'Weeks'), ('months',"
                    " 'Months')]"
                ),
                "ttype": "selection",
            },
            "activity_note": {
                "field_description": "Note",
                "ttype": "html",
            },
            "activity_summary": {
                "field_description": "Summary",
                "ttype": "char",
            },
            "activity_type_id": {
                "field_description": "Activity",
                "force_domain": (
                    "['|', ('res_model_id', '=', False), ('res_model_id', '=',"
                    " model_id)]"
                ),
                "relation": "mail.activity.type",
                "ttype": "many2one",
            },
            "activity_user_field_name": {
                "field_description": "User field name",
                "help": "Technical name of the user on the record",
                "ttype": "char",
            },
            "activity_user_id": {
                "field_description": "Responsible",
                "relation": "res.users",
                "ttype": "many2one",
            },
            "activity_user_type": {
                "field_description": "Activity User Type",
                "help": (
                    "Use 'Specific User' to always assign the same user on the"
                    " next activity. Use 'Generic User From Record' to specify"
                    " the field name of the user to choose on the record."
                ),
                "required": True,
                "selection": (
                    "[('specific', 'Specific User'), ('generic', 'Generic User"
                    " From Record')]"
                ),
                "ttype": "selection",
            },
            "binding_model_id": {
                "field_description": "Binding Model",
                "help": (
                    "Setting a value makes this action available in the"
                    " sidebar for the given model."
                ),
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "binding_type": {
                "field_description": "Binding Type",
                "required": True,
                "selection": (
                    "[('action', 'Action'), ('action_form_only', 'Form-only'),"
                    " ('report', 'Report')]"
                ),
                "ttype": "selection",
            },
            "channel_ids": {
                "field_description": "Add Channels",
                "relation": "mail.channel",
                "ttype": "many2many",
            },
            "child_ids": {
                "field_description": "Child Actions",
                "help": (
                    "Child server actions that will be executed. Note that the"
                    " last return returned action value will be used as global"
                    " return value."
                ),
                "relation": "ir.actions.server",
                "ttype": "many2many",
            },
            "code": {
                "field_description": "Python Code",
                "help": (
                    "Write Python code that the action will execute. Some"
                    " variables are available for use; help about python"
                    " expression is given in the help tab."
                ),
                "ttype": "text",
            },
            "comment": {
                "field_description": "Comment",
                "help": "Hint about this record.",
                "ttype": "char",
            },
            "crud_model_id": {
                "field_description": "Create/Write Target Model",
                "help": (
                    "Model for record creation / update. Set this field only"
                    " to specify a different model than the base model."
                ),
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "crud_model_name": {
                "field_description": "Target Model",
                "ttype": "char",
            },
            "help": {
                "field_description": "Action Description",
                "help": (
                    "Optional help text for the users with a description of"
                    " the target view, such as its usage and purpose."
                ),
                "ttype": "html",
            },
            "is_code_generator": {
                "field_description": "Is Code Generator",
                "help": (
                    "Do a link with code generator to show associate actions"
                    " server"
                ),
                "ttype": "boolean",
            },
            "link_field_id": {
                "field_description": "Link using field",
                "help": (
                    "Provide the field used to link the newly created record"
                    " on the record on used by the server action."
                ),
                "relation": "ir.model.fields",
                "ttype": "many2one",
            },
            "model_id": {
                "field_description": "Model",
                "help": "Model on which the server action runs.",
                "relation": "ir.model",
                "required": True,
                "ttype": "many2one",
            },
            "model_name": {
                "field_description": "Model Name",
                "ttype": "char",
            },
            "partner_ids": {
                "field_description": "Add Followers",
                "relation": "res.partner",
                "ttype": "many2many",
            },
            "sequence": {
                "field_description": "Sequence",
                "help": (
                    "When dealing with multiple actions, the execution order"
                    " is based on the sequence. Low number means high"
                    " priority."
                ),
                "ttype": "integer",
            },
            "state": {
                "field_description": "Action To Do",
                "help": """Type of server action. The following values are available:
- 'Execute Python Code': a block of python code that will be executed
- 'Create': create a new record with new values
- 'Update a Record': update the values of a record
- 'Execute several actions': define an action that triggers several other server actions
- 'Send Email': automatically send an email (Discuss)
- 'Add Followers': add followers to a record (Discuss)
- 'Create Next Activity': create an activity (Discuss)""",
                "required": True,
                "selection": (
                    "[('code', 'Execute Python Code'), ('object_create',"
                    " 'Create a new Record'), ('object_write', 'Update the"
                    " Record'), ('multi', 'Execute several actions'),"
                    " ('email', 'Send Email'), ('followers', 'Add Followers'),"
                    " ('next_activity', 'Create Next Activity')]"
                ),
                "ttype": "selection",
            },
            "template_id": {
                "field_description": "Email Template",
                "force_domain": "[('model_id', '=', model_id)]",
                "relation": "mail.template",
                "ttype": "many2one",
            },
            "type": {
                "field_description": "Action Type",
                "required": True,
                "ttype": "char",
            },
            "usage": {
                "field_description": "Usage",
                "required": True,
                "selection": (
                    "[('ir_actions_server', 'Server Action'), ('ir_cron',"
                    " 'Scheduled Action')]"
                ),
                "ttype": "selection",
            },
            "xml_id": {
                "field_description": "External ID",
                "ttype": "char",
            },
        }
        model_ir_actions_server = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Actions Todo
        model_model = "ir.actions.todo"
        model_name = "ir_actions_todo"
        dct_field = {
            "action_id": {
                "field_description": "Action",
                "relation": "ir.actions.actions",
                "required": True,
                "ttype": "many2one",
            },
            "m2o_code_generator": {
                "field_description": "Code Generator",
                "help": "Code Generator relation",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
            "sequence": {
                "field_description": "Sequence",
                "ttype": "integer",
            },
            "state": {
                "field_description": "Status",
                "required": True,
                "selection": "[('open', 'To Do'), ('done', 'Done')]",
                "ttype": "selection",
            },
        }
        model_ir_actions_todo = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Model
        model_model = "ir.model"
        model_name = "ir_model"
        dct_field = {
            "blacklist_all_ir_ui_view": {
                "field_description": "Blacklist All Ir Ui View",
                "help": (
                    "Enable to exclude this model from automatic ir.ui.view"
                    " generate."
                ),
                "ttype": "boolean",
            },
            "count": {
                "field_description": "Count (incl. archived)",
                "help": "Total number of records in this model",
                "ttype": "integer",
            },
            "description": {
                "field_description": "Description",
                "ttype": "char",
            },
            "diagram_arrow_dst_field": {
                "field_description": "Diagram Arrow Dst Field",
                "help": "Diagram arrow field name for destination.",
                "ttype": "char",
            },
            "diagram_arrow_form_view_ref": {
                "field_description": "Diagram Arrow Form View Ref",
                "help": (
                    "Diagram arrow field, reference view xml id. If empty,"
                    " will take default form."
                ),
                "ttype": "char",
            },
            "diagram_arrow_label": {
                "field_description": "Diagram Arrow Label",
                "help": "Diagram label, data to show when draw a line.",
                "ttype": "char",
            },
            "diagram_arrow_object": {
                "field_description": "Diagram Arrow Object",
                "help": "Diagram arrow model name for arrow.",
                "ttype": "char",
            },
            "diagram_arrow_src_field": {
                "field_description": "Diagram Arrow Src Field",
                "help": "Diagram arrow field name for source.",
                "ttype": "char",
            },
            "diagram_label_string": {
                "field_description": "Diagram Label String",
                "help": "Sentence to show at top of diagram.",
                "ttype": "char",
            },
            "diagram_node_form_view_ref": {
                "field_description": "Diagram Node Form View Ref",
                "help": (
                    "Diagram node field, reference view xml id. If empty, will"
                    " take default form."
                ),
                "ttype": "char",
            },
            "diagram_node_object": {
                "field_description": "Diagram Node Object",
                "help": "Diagram model name for node.",
                "ttype": "char",
            },
            "diagram_node_shape_field": {
                "field_description": "Diagram Node Shape Field",
                "help": "Diagram node field shape.",
                "ttype": "char",
            },
            "diagram_node_xpos_field": {
                "field_description": "Diagram Node Xpos Field",
                "help": "Diagram node field name for xpos.",
                "ttype": "char",
            },
            "diagram_node_ypos_field": {
                "field_description": "Diagram Node Ypos Field",
                "help": "Diagram node field name for ypos.",
                "ttype": "char",
            },
            "enable_activity": {
                "field_description": "Enable Activity",
                "help": (
                    "Will add chatter and activity to this model in form view."
                ),
                "ttype": "boolean",
            },
            "expression_export_data": {
                "field_description": "Expression Export Data",
                "help": (
                    "Set an expression to apply filter when exporting data."
                    ' example ("website_id", "in", [1,2]). Keep it empty to'
                    " export all data."
                ),
                "ttype": "char",
            },
            "ignore_name_export_data": {
                "field_description": "Ignore Name Export Data",
                "help": "List of ignore file_name separate by ;",
                "ttype": "char",
            },
            "info": {
                "field_description": "Information",
                "ttype": "text",
            },
            "inherit_model_ids": {
                "field_description": "Inherit ir Model",
                "help": "Inherit Model",
                "relation": "code.generator.ir.model.dependency",
                "ttype": "many2many",
            },
            "inherited_model_ids": {
                "field_description": "Inherited models",
                "help": "The list of models that extends the current model.",
                "relation": "ir.model",
                "ttype": "many2many",
            },
            "is_mail_thread": {
                "field_description": "Mail Thread",
                "help": (
                    "Whether this model supports messages and notifications."
                ),
                "ttype": "boolean",
            },
            "m2o_inherit_py_class": {
                "field_description": "Python Class",
                "help": "Python Class",
                "relation": "code.generator.pyclass",
                "ttype": "many2one",
            },
            "m2o_module": {
                "field_description": "Module",
                "help": "Module",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
            "menu_group": {
                "field_description": "Menu Group",
                "help": (
                    "If not empty, will create a group of element in menu when"
                    " auto-generate."
                ),
                "ttype": "char",
            },
            "menu_label": {
                "field_description": "Menu Label",
                "help": "Force label menu to use this value.",
                "ttype": "char",
            },
            "menu_name_keep_application": {
                "field_description": "Menu Name Keep Application",
                "help": (
                    "When generate menu name, do we keep application name in"
                    " item name?"
                ),
                "ttype": "boolean",
            },
            "menu_parent": {
                "field_description": "Menu Parent",
                "help": (
                    "If not empty, will create a new root menu of element in"
                    " menu when auto-generate."
                ),
                "ttype": "char",
            },
            "model": {
                "field_description": "Model",
                "required": True,
                "ttype": "char",
            },
            "modules": {
                "field_description": "In Apps",
                "help": (
                    "List of modules in which the object is defined or"
                    " inherited"
                ),
                "ttype": "char",
            },
            "nomenclator": {
                "field_description": "Nomenclator?",
                "help": "Set this if you want this model as a nomenclator",
                "ttype": "boolean",
            },
            "order": {
                "field_description": "Order",
                "help": (
                    "Change order to show the data from the model, like"
                    " orderby in SQL."
                ),
                "ttype": "char",
            },
            "rec_name": {
                "field_description": "Rec Name",
                "help": (
                    "Will be the field name to use when show the generic name."
                ),
                "ttype": "char",
            },
            "state": {
                "field_description": "Type",
                "selection": (
                    "[('manual', 'Custom Object'), ('base', 'Base Object')]"
                ),
                "ttype": "selection",
            },
            "transient": {
                "field_description": "Transient Model",
                "ttype": "boolean",
            },
        }
        model_ir_model = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Model Constraint
        model_model = "ir.model.constraint"
        model_name = "ir_model_constraint"
        dct_field = {
            "code_generator_id": {
                "field_description": "Code Generator",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
            "date_init": {
                "field_description": "Initialization Date",
                "ttype": "datetime",
            },
            "date_update": {
                "field_description": "Update Date",
                "ttype": "datetime",
            },
            "definition": {
                "field_description": "Definition",
                "help": "PostgreSQL constraint definition",
                "ttype": "char",
            },
            "message": {
                "field_description": "Message",
                "ttype": "char",
            },
            "model": {
                "field_description": "Model",
                "relation": "ir.model",
                "required": True,
                "ttype": "many2one",
            },
            "model_state": {
                "field_description": "Type",
                "selection": (
                    "[('manual', 'Custom Object'), ('base', 'Base Object')]"
                ),
                "ttype": "selection",
            },
            "module": {
                "field_description": "Module",
                "relation": "ir.module.module",
                "required": True,
                "ttype": "many2one",
            },
            "type": {
                "field_description": "Constraint Type",
                "help": (
                    "Type of the constraint: `f` for a foreign key, `u` for"
                    " other constraints."
                ),
                "required": True,
                "ttype": "char",
            },
        }
        model_ir_model_constraint = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Model Fields
        model_model = "ir.model.fields"
        model_name = "ir_model_fields"
        dct_field = {
            "code_generator_calendar_view_sequence": {
                "field_description": "calendar view sequence",
                "help": (
                    "Sequence to write this field in calendar view from Code"
                    " Generator."
                ),
                "ttype": "integer",
            },
            "code_generator_compute": {
                "field_description": "Compute Code Generator",
                "help": "Compute method to code_generator_writer.",
                "ttype": "char",
            },
            "code_generator_form_simple_view_sequence": {
                "field_description": "Form simple view sequence",
                "help": (
                    "Sequence to write this field in form simple view from"
                    " Code Generator."
                ),
                "ttype": "integer",
            },
            "code_generator_graph_view_sequence": {
                "field_description": "graph view sequence",
                "help": (
                    "Sequence to write this field in graph view from Code"
                    " Generator."
                ),
                "ttype": "integer",
            },
            "code_generator_kanban_view_sequence": {
                "field_description": "Kanban view sequence",
                "help": (
                    "Sequence to write this field in kanban view from Code"
                    " Generator."
                ),
                "ttype": "integer",
            },
            "code_generator_pivot_view_sequence": {
                "field_description": "pivot view sequence",
                "help": (
                    "Sequence to write this field in pivot view from Code"
                    " Generator."
                ),
                "ttype": "integer",
            },
            "code_generator_search_sequence": {
                "field_description": "Search sequence",
                "help": (
                    "Sequence to write this field in search from Code"
                    " Generator."
                ),
                "ttype": "integer",
            },
            "code_generator_search_view_sequence": {
                "field_description": "search view sequence",
                "help": (
                    "Sequence to write this field in search view from Code"
                    " Generator."
                ),
                "ttype": "integer",
            },
            "code_generator_sequence": {
                "field_description": "Sequence Code Generator",
                "help": "Sequence to write this field from Code Generator.",
                "ttype": "integer",
            },
            "code_generator_tree_view_sequence": {
                "field_description": "Tree view sequence",
                "help": (
                    "Sequence to write this field in tree view from Code"
                    " Generator."
                ),
                "ttype": "integer",
            },
            "column1": {
                "field_description": "Column 1",
                "help": "Column referring to the record in the model table",
                "ttype": "char",
            },
            "column2": {
                "field_description": "Column 2",
                "help": "Column referring to the record in the comodel table",
                "ttype": "char",
            },
            "comment_after": {
                "field_description": "Comment after field",
                "help": (
                    "Will show comment after writing field in python. Support"
                    " multiline. The comment is after if at the end of file."
                ),
                "ttype": "char",
            },
            "comment_before": {
                "field_description": "Comment before field",
                "help": (
                    "Will show comment before writing field in python. Support"
                    " multiline."
                ),
                "ttype": "char",
            },
            "complete_name": {
                "field_description": "Complete Name",
                "ttype": "char",
            },
            "compute": {
                "field_description": "Compute",
                "help": """Code to compute the value of the field.
Iterate on the recordset 'self' and assign the field's value:

    for record in self:
        record['size'] = len(record.name)

Modules time, datetime, dateutil are available.""",
                "ttype": "text",
            },
            "copied": {
                "field_description": "Copied",
                "help": (
                    "Whether the value is copied when duplicating a record."
                ),
                "ttype": "boolean",
            },
            "default": {
                "field_description": "Default value",
                "ttype": "char",
            },
            "default_lambda": {
                "field_description": "Default lambda value",
                "ttype": "char",
            },
            "depends": {
                "field_description": "Dependencies",
                "help": """Dependencies of compute method; a list of comma-separated field names, like

    name, partner_id.name""",
                "ttype": "char",
            },
            "domain": {
                "field_description": "Domain",
                "help": (
                    "The optional domain to restrict possible values for"
                    " relationship fields, specified as a Python expression"
                    " defining a list of triplets. For example:"
                    " [('color','=','red')]"
                ),
                "ttype": "char",
            },
            "field_context": {
                "field_description": "Field Context",
                "ttype": "char",
            },
            "field_description": {
                "field_description": "Field Label",
                "required": True,
                "ttype": "char",
            },
            "force_domain": {
                "field_description": "Force Domain",
                "ttype": "char",
            },
            "force_widget": {
                "field_description": "Force widget",
                "help": "Use this widget for this field when create views.",
                "selection": (
                    "[('barcode_handler', 'Barcode handler'), ('handle',"
                    " 'Handle'), ('float_with_uom', 'Float with uom'),"
                    " ('timesheet_uom', 'Timesheet uom'), ('radio', 'Radio'),"
                    " ('priority', 'Priority'), ('mail_thread', 'Mail"
                    " thread'), ('mail_activity', 'Mail activity'),"
                    " ('mail_followers', 'Mail followers'), ('phone',"
                    " 'Phone'), ('statinfo', 'Statinfo'), ('statusbar',"
                    " 'Statusbar'), ('many2many', 'Many2many'),"
                    " ('many2many_tags', 'Many2many tags'),"
                    " ('many2many_tags_email', 'Many2many tags email'),"
                    " ('many2many_checkboxes', 'Many2many checkboxes'),"
                    " ('many2many_binary', 'Many2many binary'), ('monetary',"
                    " 'Monetary'), ('selection', 'Selection'), ('url', 'Url'),"
                    " ('boolean_button', 'Boolean button'), ('boolean_toggle',"
                    " 'Boolean toggle'), ('toggle_button', 'Toggle button'),"
                    " ('state_selection', 'State selection'),"
                    " ('kanban_state_selection', 'Kanban state selection'),"
                    " ('kanban_activity', 'Kanban activity'),"
                    " ('tier_validation', 'Tier validation'), ('binary_size',"
                    " 'Binary size'), ('binary_preview', 'Binary preview'),"
                    " ('char_domain', 'Char domain'), ('domain', 'Domain'),"
                    " ('file_actions', 'File actions'), ('color', 'Color'),"
                    " ('copy_binary', 'Copy binary'), ('share_char', 'Share"
                    " char'), ('share_text', 'Share text'), ('share_binary',"
                    " 'Share binary'), ('selection_badge', 'Selection badge'),"
                    " ('link_button', 'Link button'), ('image', 'Image'),"
                    " ('contact', 'Contact'), ('float_time', 'Float time'),"
                    " ('image-url', 'Image-url'), ('html', 'Html'), ('email',"
                    " 'Email'), ('website_button', 'Website button'),"
                    " ('one2many', 'One2many'), ('one2many_list', 'One2many"
                    " list'), ('gauge', 'Gauge'), ('label_selection', 'Label"
                    " selection'), ('percentpie', 'Percentpie'),"
                    " ('progressbar', 'Progressbar'), ('mrp_time_counter',"
                    " 'Mrp time counter'), ('qty_available', 'Qty available'),"
                    " ('ace', 'Ace'), ('pdf_viewer', 'Pdf viewer'),"
                    " ('path_names', 'Path names'), ('path_json', 'Path"
                    " json'), ('date', 'Date'), ('color_index', 'Color"
                    " index'), ('google_partner_address', 'Google partner"
                    " address'), ('google_marker_picker', 'Google marker"
                    " picker'), ('spread_line_widget', 'Spread line widget'),"
                    " ('geo_edit_map', 'Geo edit map'), ('dynamic_dropdown',"
                    " 'Dynamic dropdown'), ('section_and_note_one2many',"
                    " 'Section and note one2many'), ('section_and_note_text',"
                    " 'Section and note text'), ('reference', 'Reference'),"
                    " ('x2many_2d_matrix', 'X2many 2d matrix'),"
                    " ('numeric_step', 'Numeric step'), ('BVEEditor',"
                    " 'Bveeditor'), ('er_diagram_image', 'Er diagram image'),"
                    " ('u2f_scan', 'U2f scan'), ('password', 'Password'),"
                    " ('open_tab', 'Open tab'), ('signature', 'Signature'),"
                    " ('upgrade_boolean', 'Upgrade boolean'),"
                    " ('many2manyattendee', 'Many2manyattendee'),"
                    " ('res_partner_many2one', 'Res partner many2one'),"
                    " ('hr_org_chart', 'Hr org chart'), ('CopyClipboardText',"
                    " 'Copyclipboardtext'), ('CopyClipboardChar',"
                    " 'Copyclipboardchar'), ('bullet_state', 'Bullet state'),"
                    " ('pad', 'Pad'), ('field_partner_autocomplete', 'Field"
                    " partner autocomplete'), ('html_frame', 'Html frame'),"
                    " ('task_workflow', 'Task workflow'),"
                    " ('document_page_reference', 'Document page reference'),"
                    " ('mis_report_widget', 'Mis report widget'), ('kpi',"
                    " 'Kpi'), ('action_barcode_handler', 'Action barcode"
                    " handler'), ('mail_failed_message', 'Mail failed"
                    " message'), ('mermaid', 'Mermaid'), ('payment',"
                    " 'Payment'), ('previous_order', 'Previous order')]"
                ),
                "ttype": "selection",
            },
            "groups": {
                "field_description": "Groups",
                "relation": "res.groups",
                "ttype": "many2many",
            },
            "help": {
                "field_description": "Field Help",
                "ttype": "text",
            },
            "ignore_on_code_generator_writer": {
                "field_description": "Ignore On Code Generator Writer",
                "help": "Enable this to ignore it when write code.",
                "ttype": "boolean",
            },
            "index": {
                "field_description": "Indexed",
                "ttype": "boolean",
            },
            "is_code_generator": {
                "field_description": "Is Code Generator",
                "help": (
                    "Do a link with code generator to show associate model"
                    " fields"
                ),
                "ttype": "boolean",
            },
            "is_date_end_view": {
                "field_description": "Show end date view",
                "help": "View timeline only, end field.",
                "ttype": "boolean",
            },
            "is_date_start_view": {
                "field_description": "Show start date view",
                "help": "View timeline only, start field.",
                "ttype": "boolean",
            },
            "is_hide_blacklist_calendar_view": {
                "field_description": "Hide in blacklist calendar view",
                "help": (
                    "Hide from view when field is blacklisted. View calendar"
                    " only."
                ),
                "ttype": "boolean",
            },
            "is_hide_blacklist_form_view": {
                "field_description": "Hide in blacklist form view",
                "help": (
                    "Hide from view when field is blacklisted. View form only."
                ),
                "ttype": "boolean",
            },
            "is_hide_blacklist_graph_view": {
                "field_description": "Hide in blacklist graph view",
                "help": (
                    "Hide from view when field is blacklisted. View graph"
                    " only."
                ),
                "ttype": "boolean",
            },
            "is_hide_blacklist_kanban_view": {
                "field_description": "Hide in blacklist kanban view",
                "help": (
                    "Hide from view when field is blacklisted. View kanban"
                    " only."
                ),
                "ttype": "boolean",
            },
            "is_hide_blacklist_list_view": {
                "field_description": "Hide in blacklist list view",
                "help": (
                    "Hide from view when field is blacklisted. View list only."
                ),
                "ttype": "boolean",
            },
            "is_hide_blacklist_model_inherit": {
                "field_description": "Hide in blacklist model inherit",
                "help": "Hide from model inherit when field is blacklisted.",
                "ttype": "boolean",
            },
            "is_hide_blacklist_pivot_view": {
                "field_description": "Hide in blacklist pivot view",
                "help": (
                    "Hide from view when field is blacklisted. View pivot"
                    " only."
                ),
                "ttype": "boolean",
            },
            "is_hide_blacklist_search_view": {
                "field_description": "Hide in blacklist search view",
                "help": (
                    "Hide from view when field is blacklisted. View search"
                    " only."
                ),
                "ttype": "boolean",
            },
            "is_show_whitelist_calendar_view": {
                "field_description": "Show in whitelist calendar view",
                "help": (
                    "If a field in model is in whitelist, all is not will be"
                    " hide. View calendar only."
                ),
                "ttype": "boolean",
            },
            "is_show_whitelist_form_view": {
                "field_description": "Show in whitelist form view",
                "help": (
                    "If a field in model is in whitelist, all is not will be"
                    " hide. View form only."
                ),
                "ttype": "boolean",
            },
            "is_show_whitelist_graph_view": {
                "field_description": "Show in whitelist graph view",
                "help": (
                    "If a field in model is in whitelist, all is not will be"
                    " hide. View graph only."
                ),
                "ttype": "boolean",
            },
            "is_show_whitelist_kanban_view": {
                "field_description": "Show in whitelist kanban view",
                "help": (
                    "If a field in model is in whitelist, all is not will be"
                    " hide. View kanban only."
                ),
                "ttype": "boolean",
            },
            "is_show_whitelist_list_view": {
                "field_description": "Show in whitelist list view",
                "help": (
                    "If a field in model is in whitelist, all is not will be"
                    " hide. View list only."
                ),
                "ttype": "boolean",
            },
            "is_show_whitelist_model_inherit": {
                "field_description": "Show in whitelist model inherit",
                "help": (
                    "If a field in model is in whitelist, will be show in"
                    " generated model."
                ),
                "ttype": "boolean",
            },
            "is_show_whitelist_pivot_view": {
                "field_description": "Show in whitelist pivot view",
                "help": (
                    "If a field in model is in whitelist, all is not will be"
                    " hide. View pivot only."
                ),
                "ttype": "boolean",
            },
            "is_show_whitelist_search_view": {
                "field_description": "Show in whitelist search view",
                "help": (
                    "If a field in model is in whitelist, all is not will be"
                    " hide. View search only."
                ),
                "ttype": "boolean",
            },
            "model": {
                "field_description": "Object Name",
                "help": (
                    "The technical name of the model this field belongs to"
                ),
                "required": True,
                "ttype": "char",
            },
            "model_id": {
                "field_description": "Model",
                "help": "The model this field belongs to",
                "relation": "ir.model",
                "required": True,
                "ttype": "many2one",
            },
            "modules": {
                "field_description": "In Apps",
                "help": "List of modules in which the field is defined",
                "ttype": "char",
            },
            "on_delete": {
                "field_description": "On Delete",
                "help": "On delete property for many2one fields",
                "selection": (
                    "[('cascade', 'Cascade'), ('set null', 'Set NULL'),"
                    " ('restrict', 'Restrict')]"
                ),
                "ttype": "selection",
            },
            "readonly": {
                "field_description": "Readonly",
                "ttype": "boolean",
            },
            "related": {
                "field_description": "Related Field",
                "help": (
                    "The corresponding related field, if any. This must be a"
                    " dot-separated list of field names."
                ),
                "ttype": "char",
            },
            "related_field_id": {
                "field_description": "Related field",
                "relation": "ir.model.fields",
                "ttype": "many2one",
            },
            "relation": {
                "field_description": "Object Relation",
                "help": (
                    "For relationship fields, the technical name of the target"
                    " model"
                ),
                "ttype": "char",
            },
            "relation_field": {
                "field_description": "Relation Field",
                "help": (
                    "For one2many fields, the field on the target model that"
                    " implement the opposite many2one relationship"
                ),
                "ttype": "char",
            },
            "relation_field_id": {
                "field_description": "Relation field",
                "relation": "ir.model.fields",
                "ttype": "many2one",
            },
            "relation_table": {
                "field_description": "Relation Table",
                "help": (
                    "Used for custom many2many fields to define a custom"
                    " relation table name"
                ),
                "ttype": "char",
            },
            "required": {
                "field_description": "Required",
                "ttype": "boolean",
            },
            "selectable": {
                "field_description": "Selectable",
                "ttype": "boolean",
            },
            "selection": {
                "field_description": "Selection Options",
                "help": (
                    "List of options for a selection field, specified as a"
                    " Python expression defining a list of (key, label) pairs."
                    " For example: [('blue','Blue'),('yellow','Yellow')]"
                ),
                "ttype": "char",
            },
            "size": {
                "field_description": "Size",
                "ttype": "integer",
            },
            "state": {
                "field_description": "Type",
                "required": True,
                "selection": (
                    "[('manual', 'Custom Field'), ('base', 'Base Field')]"
                ),
                "ttype": "selection",
            },
            "store": {
                "field_description": "Stored",
                "help": "Whether the value is stored in the database.",
                "ttype": "boolean",
            },
            "track_visibility": {
                "field_description": "Tracking",
                "help": (
                    "When set, every modification to this field will be"
                    " tracked in the chatter."
                ),
                "selection": (
                    "[('onchange', 'On Change'), ('always', 'Always')]"
                ),
                "ttype": "selection",
            },
            "translate": {
                "field_description": "Translatable",
                "help": (
                    "Whether values for this field can be translated (enables"
                    " the translation mechanism for that field)"
                ),
                "ttype": "boolean",
            },
            "ttype": {
                "field_description": "Field Type",
                "required": True,
                "selection": (
                    "[('binary', 'binary'), ('boolean', 'boolean'), ('char',"
                    " 'char'), ('date', 'date'), ('datetime', 'datetime'),"
                    " ('float', 'float'), ('html', 'html'), ('integer',"
                    " 'integer'), ('many2many', 'many2many'), ('many2one',"
                    " 'many2one'), ('monetary', 'monetary'), ('one2many',"
                    " 'one2many'), ('reference', 'reference'), ('selection',"
                    " 'selection'), ('text', 'text')]"
                ),
                "ttype": "selection",
            },
        }
        model_ir_model_fields = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Module Module
        model_model = "ir.module.module"
        model_name = "ir_module_module"
        dct_field = {
            "application": {
                "field_description": "Application",
                "ttype": "boolean",
            },
            "author": {
                "field_description": "Author",
                "ttype": "char",
            },
            "auto_install": {
                "field_description": "Automatic Installation",
                "help": (
                    "An auto-installable module is automatically installed by"
                    " the system when all its dependencies are satisfied. If"
                    " the module has no dependency, it is always installed."
                ),
                "ttype": "boolean",
            },
            "category_id": {
                "field_description": "Category",
                "relation": "ir.module.category",
                "ttype": "many2one",
            },
            "contributors": {
                "field_description": "Contributors",
                "ttype": "text",
            },
            "demo": {
                "field_description": "Demo Data",
                "ttype": "boolean",
            },
            "description": {
                "field_description": "Description",
                "ttype": "text",
            },
            "description_html": {
                "field_description": "Description HTML",
                "ttype": "html",
            },
            "header_manifest": {
                "field_description": "Header",
                "help": "Header comment in __manifest__.py file.",
                "ttype": "text",
            },
            "icon": {
                "field_description": "Icon URL",
                "ttype": "char",
            },
            "icon_image": {
                "field_description": "Icon",
                "ttype": "binary",
            },
            "installed_version": {
                "field_description": "Latest Version",
                "ttype": "char",
            },
            "latest_version": {
                "field_description": "Installed Version",
                "ttype": "char",
            },
            "license": {
                "field_description": "License",
                "selection": (
                    "[('GPL-2', 'GPL Version 2'), ('GPL-2 or any later"
                    " version', 'GPL-2 or later version'), ('GPL-3', 'GPL"
                    " Version 3'), ('GPL-3 or any later version', 'GPL-3 or"
                    " later version'), ('AGPL-3', 'Affero GPL-3'), ('LGPL-3',"
                    " 'LGPL Version 3'), ('Other OSI approved licence', 'Other"
                    " OSI Approved Licence'), ('OEEL-1', 'Odoo Enterprise"
                    " Edition License v1.0'), ('OPL-1', 'Odoo Proprietary"
                    " License v1.0'), ('Other proprietary', 'Other"
                    " Proprietary')]"
                ),
                "ttype": "selection",
            },
            "maintainer": {
                "field_description": "Maintainer",
                "ttype": "char",
            },
            "menus_by_module": {
                "field_description": "Menus",
                "ttype": "text",
            },
            "published_version": {
                "field_description": "Published Version",
                "ttype": "char",
            },
            "reports_by_module": {
                "field_description": "Reports",
                "ttype": "text",
            },
            "sequence": {
                "field_description": "Sequence",
                "ttype": "integer",
            },
            "shortdesc": {
                "field_description": "Module Name",
                "ttype": "char",
            },
            "state": {
                "field_description": "Status",
                "selection": (
                    "[('uninstallable', 'Uninstallable'), ('uninstalled', 'Not"
                    " Installed'), ('installed', 'Installed'), ('to upgrade',"
                    " 'To be upgraded'), ('to remove', 'To be removed'), ('to"
                    " install', 'To be installed')]"
                ),
                "ttype": "selection",
            },
            "summary": {
                "field_description": "Summary",
                "ttype": "char",
            },
            "to_buy": {
                "field_description": "Odoo Enterprise Module",
                "ttype": "boolean",
            },
            "url": {
                "field_description": "URL",
                "ttype": "char",
            },
            "views_by_module": {
                "field_description": "Views",
                "ttype": "text",
            },
            "website": {
                "field_description": "Website",
                "ttype": "char",
            },
        }
        model_ir_module_module = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Generate server action
        # action_server view
        act_server_id = env["ir.actions.server"].search(
            [
                ("name", "=", "Install Modules"),
                ("model_id", "=", model_ir_module_module.id),
            ]
        )
        if not act_server_id:
            act_server_id = env["ir.actions.server"].create(
                {
                    "name": "Install Modules",
                    "model_id": model_ir_module_module.id,
                    "binding_model_id": model_ir_module_module.id,
                    "state": "code",
                    "code": "records.button_immediate_install()",
                }
            )

        # Add/Update Ir Module Module Dependency
        model_model = "ir.module.module.dependency"
        model_name = "ir_module_module_dependency"
        dct_field = {
            "depend_id": {
                "field_description": "Dependency",
                "relation": "ir.module.module",
                "ttype": "many2one",
            },
            "module_id": {
                "field_description": "Module",
                "relation": "ir.module.module",
                "ttype": "many2one",
            },
            "state": {
                "field_description": "Status",
                "selection": (
                    "[('uninstallable', 'Uninstallable'), ('uninstalled', 'Not"
                    " Installed'), ('installed', 'Installed'), ('to upgrade',"
                    " 'To be upgraded'), ('to remove', 'To be removed'), ('to"
                    " install', 'To be installed'), ('unknown', 'Unknown')]"
                ),
                "ttype": "selection",
            },
        }
        model_ir_module_module_dependency = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Ui Menu
        model_model = "ir.ui.menu"
        model_name = "ir_ui_menu"
        dct_field = {
            "action": {
                "field_description": "Action",
                "ttype": "reference",
            },
            "active": {
                "field_description": "Active",
                "ttype": "boolean",
            },
            "complete_name": {
                "field_description": "Full Path",
                "ttype": "char",
            },
            "groups_id": {
                "field_description": "Groups",
                "help": (
                    "If you have groups, the visibility of this menu will be"
                    " based on these groups. If this field is empty, Odoo will"
                    " compute visibility based on the related object's read"
                    " access."
                ),
                "relation": "res.groups",
                "ttype": "many2many",
            },
            "ignore_act_window": {
                "field_description": "Ignore Act Window",
                "help": "Set True to force no act_window, like a parent menu.",
                "ttype": "boolean",
            },
            "m2o_module": {
                "field_description": "Module",
                "help": "Module",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
            "parent_id": {
                "field_description": "Parent Menu",
                "relation": "ir.ui.menu",
                "ttype": "many2one",
            },
            "parent_path": {
                "field_description": "Parent Path",
                "ttype": "char",
            },
            "sequence": {
                "field_description": "Sequence",
                "ttype": "integer",
            },
            "web_icon": {
                "field_description": "Web Icon File",
                "ttype": "char",
            },
            "web_icon_data": {
                "field_description": "Web Icon Image",
                "ttype": "binary",
            },
        }
        model_ir_ui_menu = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Ir Ui View
        model_model = "ir.ui.view"
        model_name = "ir_ui_view"
        dct_field = {
            "active": {
                "field_description": "Active",
                "help": """If this view is inherited,
* if True, the view always extends its parent
* if False, the view currently does not extend its parent but can be enabled
         """,
                "ttype": "boolean",
            },
            "arch": {
                "field_description": "View Architecture",
                "ttype": "text",
            },
            "arch_base": {
                "field_description": "Base View Architecture",
                "ttype": "text",
            },
            "arch_db": {
                "field_description": "Arch Blob",
                "ttype": "text",
            },
            "arch_fs": {
                "field_description": "Arch Filename",
                "ttype": "char",
            },
            "field_parent": {
                "field_description": "Child Field",
                "ttype": "char",
            },
            "groups_id": {
                "field_description": "Groups",
                "help": (
                    "If this field is empty, the view applies to all users."
                    " Otherwise, the view applies to the users of those groups"
                    " only."
                ),
                "relation": "res.groups",
                "ttype": "many2many",
            },
            "inherit_id": {
                "field_description": "Inherited View",
                "relation": "ir.ui.view",
                "ttype": "many2one",
            },
            "is_code_generator": {
                "field_description": "Is Code Generator",
                "help": (
                    "Do a link with code generator to show associate"
                    " ir.ui.view"
                ),
                "ttype": "boolean",
            },
            "is_hide_blacklist_write_view": {
                "field_description": (
                    "Hide in blacklist when writing code view"
                ),
                "help": "Hide from view when field is blacklisted.",
                "ttype": "boolean",
            },
            "is_show_whitelist_write_view": {
                "field_description": (
                    "Show in whitelist when writing code view"
                ),
                "help": (
                    "If a field in model is in whitelist, all is not will be"
                    " hide. "
                ),
                "ttype": "boolean",
            },
            "key": {
                "field_description": "Key",
                "ttype": "char",
            },
            "m2o_model": {
                "field_description": "Code generator Model",
                "help": "Model",
                "relation": "ir.model",
                "ttype": "many2one",
            },
            "mode": {
                "field_description": "View inheritance mode",
                "help": """Only applies if this view inherits from an other one (inherit_id is not False/Null).

* if extension (default), if this view is requested the closest primary view
is looked up (via inherit_id), then all views inheriting from it with this
view's model are applied
* if primary, the closest primary view is fully resolved (even if it uses a
different model than this one), then this view's inheritance specs
(<xpath/>) are applied, and the result is used as if it were this view's
actual arch.
""",
                "required": True,
                "selection": (
                    "[('primary', 'Base view'), ('extension', 'Extension"
                    " View')]"
                ),
                "ttype": "selection",
            },
            "model": {
                "field_description": "Model",
                "ttype": "char",
            },
            "model_data_id": {
                "field_description": "Model Data",
                "relation": "ir.model.data",
                "ttype": "many2one",
            },
            "priority": {
                "field_description": "Sequence",
                "required": True,
                "ttype": "integer",
            },
            "type": {
                "field_description": "View Type",
                "selection": (
                    "[('tree', 'Tree'), ('form', 'Form'), ('graph', 'Graph'),"
                    " ('pivot', 'Pivot'), ('calendar', 'Calendar'),"
                    " ('diagram', 'Diagram'), ('gantt', 'Gantt'), ('kanban',"
                    " 'Kanban'), ('search', 'Search'), ('qweb', 'QWeb'),"
                    " ('timeline', 'Timeline'), ('activity', 'Activity')]"
                ),
                "ttype": "selection",
            },
            "xml_id": {
                "field_description": "External ID",
                "help": "ID of the view defined in xml file",
                "ttype": "char",
            },
        }
        model_ir_ui_view = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Res Config Settings
        model_model = "res.config.settings"
        model_name = "res_config_settings"
        dct_field = {
            "alias_domain": {
                "field_description": "Alias Domain",
                "help": (
                    "If you have setup a catch-all email domain redirected to"
                    " the Odoo server, enter the domain name here."
                ),
                "ttype": "char",
            },
            "attachment_location": {
                "field_description": "Storage Location",
                "help": "Attachment storage location.",
                "required": True,
                "selection": "[('db', 'DB'), ('file', 'FILE')]",
                "ttype": "selection",
            },
            "attachment_location_changed": {
                "field_description": "Storage Location Changed",
                "ttype": "boolean",
            },
            "auth_signup_reset_password": {
                "field_description": "Enable password reset from Login page",
                "ttype": "boolean",
            },
            "auth_signup_template_user_id": {
                "field_description": (
                    "Template user for new users created through signup"
                ),
                "relation": "res.users",
                "ttype": "many2one",
            },
            "auth_signup_uninvited": {
                "field_description": "Customer Account",
                "selection": (
                    "[('b2b', 'On invitation'), ('b2c', 'Free sign up')]"
                ),
                "ttype": "selection",
            },
            "binary_max_size": {
                "field_description": "File Size Limit",
                "help": """Maximum allowed file size in megabytes. Note that this setting only adjusts
            the binary widgets accordingly. The maximum file size on your server can probably
            be restricted in several places. Note that a large file size limit and therefore
            large files in your system can significantly limit performance.""",
                "required": True,
                "ttype": "integer",
            },
            "branding_branding_system_email": {
                "field_description": "System User Email",
                "ttype": "char",
            },
            "branding_branding_system_image": {
                "field_description": "System User Image",
                "help": (
                    "This field holds the image used as avatar for this"
                    " contact, limited to 1024x1024px"
                ),
                "ttype": "binary",
            },
            "branding_branding_system_name": {
                "field_description": "System User Name",
                "ttype": "char",
            },
            "branding_color_01": {
                "field_description": "Color 01",
                "ttype": "char",
            },
            "branding_color_02": {
                "field_description": "Color 02",
                "ttype": "char",
            },
            "branding_color_03": {
                "field_description": "Color 03",
                "ttype": "char",
            },
            "branding_color_04": {
                "field_description": "Color 04",
                "ttype": "char",
            },
            "branding_color_05": {
                "field_description": "Color 05",
                "ttype": "char",
            },
            "branding_color_06": {
                "field_description": "Color 06",
                "ttype": "char",
            },
            "branding_color_07": {
                "field_description": "Color 07",
                "ttype": "char",
            },
            "branding_color_08": {
                "field_description": "Color 08",
                "ttype": "char",
            },
            "branding_color_09": {
                "field_description": "Color 09",
                "ttype": "char",
            },
            "branding_color_10": {
                "field_description": "Color 10",
                "ttype": "char",
            },
            "branding_color_11": {
                "field_description": "Color 11",
                "ttype": "char",
            },
            "branding_color_12": {
                "field_description": "Color 12",
                "ttype": "char",
            },
            "branding_color_background": {
                "field_description": "Form Color",
                "ttype": "char",
            },
            "branding_color_black": {
                "field_description": "Black Color",
                "ttype": "char",
            },
            "branding_color_brand": {
                "field_description": "Brand Color",
                "ttype": "char",
            },
            "branding_color_danger": {
                "field_description": "Danger Color",
                "ttype": "char",
            },
            "branding_color_dark": {
                "field_description": "Dark Color",
                "ttype": "char",
            },
            "branding_color_gray_100": {
                "field_description": "Gray 100 Color",
                "ttype": "char",
            },
            "branding_color_gray_200": {
                "field_description": "Gray 200 Color",
                "ttype": "char",
            },
            "branding_color_gray_300": {
                "field_description": "Gray 300 Color",
                "ttype": "char",
            },
            "branding_color_gray_400": {
                "field_description": "Gray 400 Color",
                "ttype": "char",
            },
            "branding_color_gray_500": {
                "field_description": "Gray 500 Color",
                "ttype": "char",
            },
            "branding_color_gray_600": {
                "field_description": "Gray 600 Color",
                "ttype": "char",
            },
            "branding_color_gray_700": {
                "field_description": "Gray 700 Color",
                "ttype": "char",
            },
            "branding_color_gray_800": {
                "field_description": "Gray 800 Color",
                "ttype": "char",
            },
            "branding_color_gray_900": {
                "field_description": "Gray 900 Color",
                "ttype": "char",
            },
            "branding_color_info": {
                "field_description": "Info Color",
                "ttype": "char",
            },
            "branding_color_light": {
                "field_description": "Light Color",
                "ttype": "char",
            },
            "branding_color_lightsecondary": {
                "field_description": "Light Secondary Color",
                "ttype": "char",
            },
            "branding_color_muted": {
                "field_description": "Muted Color",
                "ttype": "char",
            },
            "branding_color_notification_error": {
                "field_description": "Notification Error Color",
                "ttype": "char",
            },
            "branding_color_notification_info": {
                "field_description": "Notification Info Color",
                "ttype": "char",
            },
            "branding_color_primary": {
                "field_description": "Primary Color",
                "ttype": "char",
            },
            "branding_color_secondary": {
                "field_description": "Secondary Color",
                "ttype": "char",
            },
            "branding_color_success": {
                "field_description": "Success Color",
                "ttype": "char",
            },
            "branding_color_text": {
                "field_description": "Text Color",
                "ttype": "char",
            },
            "branding_color_view": {
                "field_description": "View Color",
                "ttype": "char",
            },
            "branding_color_warning": {
                "field_description": "Warning Color",
                "ttype": "char",
            },
            "branding_color_white": {
                "field_description": "White Color",
                "ttype": "char",
            },
            "branding_company_favicon": {
                "field_description": "Company Favicon",
                "ttype": "binary",
            },
            "branding_company_logo": {
                "field_description": "Company Logo",
                "help": (
                    "This field holds the image used as avatar for this"
                    " contact, limited to 1024x1024px"
                ),
                "ttype": "binary",
            },
            "branding_company_name": {
                "field_description": "Company Name",
                "ttype": "char",
            },
            "branding_documentation": {
                "field_description": "Documentation URL",
                "ttype": "char",
            },
            "branding_publisher": {
                "field_description": "Publisher",
                "ttype": "char",
            },
            "branding_share": {
                "field_description": "Share URL",
                "ttype": "char",
            },
            "branding_store": {
                "field_description": "Store URL",
                "ttype": "char",
            },
            "branding_support": {
                "field_description": "Support URL",
                "ttype": "char",
            },
            "branding_system_name": {
                "field_description": "System Name",
                "ttype": "char",
            },
            "branding_system_user": {
                "field_description": "System User",
                "relation": "res.users",
                "required": True,
                "ttype": "many2one",
            },
            "branding_website": {
                "field_description": "Website URL",
                "ttype": "char",
            },
            "company_id": {
                "field_description": "Company",
                "relation": "res.company",
                "required": True,
                "ttype": "many2one",
            },
            "company_share_partner": {
                "field_description": "Share partners to all companies",
                "help": """Share your partners to all companies defined in your instance.
 * Checked : Partners are visible for every companies, even if a company is defined on the partner.
 * Unchecked : Each company can see only its partner (partners where company is defined). Partners not related to a company are visible for all companies.""",
                "ttype": "boolean",
            },
            "digest_emails": {
                "field_description": "Digest Emails",
                "ttype": "boolean",
            },
            "digest_id": {
                "field_description": "Digest Email",
                "relation": "digest.digest",
                "ttype": "many2one",
            },
            "external_email_server_default": {
                "field_description": "External Email Servers",
                "ttype": "boolean",
            },
            "external_report_layout_id": {
                "field_description": "Document Template",
                "relation": "ir.ui.view",
                "ttype": "many2one",
            },
            "fail_counter": {
                "field_description": "Fail Mail",
                "ttype": "integer",
            },
            "group_multi_company": {
                "field_description": "Manage multiple companies",
                "ttype": "boolean",
            },
            "group_multi_currency": {
                "field_description": "Multi-Currencies",
                "help": "Allows to work in a multi currency environment",
                "ttype": "boolean",
            },
            "module_auth_ldap": {
                "field_description": "LDAP Authentication",
                "ttype": "boolean",
            },
            "module_auth_oauth": {
                "field_description": (
                    "Use external authentication providers (OAuth)"
                ),
                "ttype": "boolean",
            },
            "module_base_gengo": {
                "field_description": "Translate Your Website with Gengo",
                "ttype": "boolean",
            },
            "module_base_import": {
                "field_description": (
                    "Allow users to import data from CSV/XLS/XLSX/ODS files"
                ),
                "ttype": "boolean",
            },
            "module_google_calendar": {
                "field_description": (
                    "Allow the users to synchronize their calendar  with"
                    " Google Calendar"
                ),
                "ttype": "boolean",
            },
            "module_google_drive": {
                "field_description": "Attach Google documents to any record",
                "ttype": "boolean",
            },
            "module_google_spreadsheet": {
                "field_description": "Google Spreadsheet",
                "ttype": "boolean",
            },
            "module_inter_company_rules": {
                "field_description": "Manage Inter Company",
                "ttype": "boolean",
            },
            "module_muk_mail_branding": {
                "field_description": "Mail Branding",
                "help": "Brand your outgoing mails with your own style.",
                "ttype": "boolean",
            },
            "module_muk_pos_branding": {
                "field_description": "PoS Branding",
                "help": "Brand the PoS panel according to your needs.",
                "ttype": "boolean",
            },
            "module_muk_web_branding": {
                "field_description": "Web Branding",
                "help": "Customize the backend according to your needs.",
                "ttype": "boolean",
            },
            "module_muk_web_theme_branding": {
                "field_description": "Theme Branding",
                "help": "Customize the theme according to your needs.",
                "ttype": "boolean",
            },
            "module_muk_web_theme_mail": {
                "field_description": "Theme Mail",
                "help": "Optimizes the mail chatter for the theme.",
                "ttype": "boolean",
            },
            "module_muk_web_theme_mobile": {
                "field_description": "Theme Mobile",
                "help": "Allow Odoo to be used as a PWA app.",
                "ttype": "boolean",
            },
            "module_muk_web_theme_website": {
                "field_description": "Theme Website",
                "help": "Add theme styled website navigation.",
                "ttype": "boolean",
            },
            "module_muk_website_branding": {
                "field_description": "Website Branding",
                "help": "Brand the website according to your needs.",
                "ttype": "boolean",
            },
            "module_pad": {
                "field_description": "Collaborative Pads",
                "ttype": "boolean",
            },
            "module_partner_autocomplete": {
                "field_description": "Auto-populate company data",
                "ttype": "boolean",
            },
            "module_voip": {
                "field_description": "Asterisk (VoIP)",
                "ttype": "boolean",
            },
            "module_web_unsplash": {
                "field_description": "Unsplash Image Library",
                "ttype": "boolean",
            },
            "paperformat_id": {
                "field_description": "Paper format",
                "relation": "report.paperformat",
                "ttype": "many2one",
            },
            "report_footer": {
                "field_description": "Custom Report Footer",
                "help": "Footer text displayed at the bottom of all reports.",
                "ttype": "text",
            },
            "s_data2export": {
                "field_description": "Model data to export",
                "help": "Model data to export",
                "selection": (
                    "[('nonomenclator', 'Include the data of all of the"
                    " selected models to export.'), ('nomenclator', 'Include"
                    " the data of the selected models to export set it as"
                    " nomenclator.')]"
                ),
                "ttype": "selection",
            },
            "show_effect": {
                "field_description": "Show Effect",
                "ttype": "boolean",
            },
            "theme_background_blend_mode": {
                "field_description": "Apps Menu Background Blend Mode",
                "selection": (
                    "[('normal', 'Normal'), ('multiply', 'Multiply'),"
                    " ('screen', 'Screen'), ('overlay', 'Overlay'),"
                    " ('hard-light', 'Hard-light'), ('darken', 'Darken'),"
                    " ('lighten', 'Lighten'), ('color-dodge', 'Color-dodge'),"
                    " ('color-burn', 'Color-burn'), ('hard-light',"
                    " 'Hard-light'), ('difference', 'Difference'),"
                    " ('exclusion', 'Exclusion'), ('hue', 'Hue'),"
                    " ('saturation', 'Saturation'), ('color', 'Color'),"
                    " ('luminosity', 'Luminosity')]"
                ),
                "ttype": "selection",
            },
            "theme_background_image": {
                "field_description": "Apps Menu Background Image",
                "ttype": "binary",
            },
            "theme_color_appbar_background": {
                "field_description": "Theme AppBar Background",
                "ttype": "char",
            },
            "theme_color_appbar_color": {
                "field_description": "Theme AppBar Color",
                "ttype": "char",
            },
            "theme_color_brand": {
                "field_description": "Theme Brand Color",
                "ttype": "char",
            },
            "theme_color_menu": {
                "field_description": "Theme Menu Color",
                "ttype": "char",
            },
            "theme_color_primary": {
                "field_description": "Theme Primary Color",
                "ttype": "char",
            },
            "theme_color_required": {
                "field_description": "Theme Required Color",
                "ttype": "char",
            },
            "theme_default_chatter_preference": {
                "field_description": "Chatter Position",
                "selection": "[('normal', 'Normal'), ('sided', 'Sided')]",
                "ttype": "selection",
            },
            "theme_default_sidebar_preference": {
                "field_description": "Sidebar Type",
                "selection": (
                    "[('invisible', 'Invisible'), ('small', 'Small'),"
                    " ('large', 'Large')]"
                ),
                "ttype": "selection",
            },
            "user_default_rights": {
                "field_description": "Default Access Rights",
                "ttype": "boolean",
            },
        }
        model_res_config_settings = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Add/Update Res Groups
        model_model = "res.groups"
        model_name = "res_groups"
        dct_field = {
            "category_id": {
                "field_description": "Application",
                "relation": "ir.module.category",
                "ttype": "many2one",
            },
            "color": {
                "field_description": "Color Index",
                "ttype": "integer",
            },
            "comment": {
                "field_description": "Comment",
                "ttype": "text",
            },
            "full_name": {
                "field_description": "Group Name",
                "ttype": "char",
            },
            "implied_ids": {
                "field_description": "Inherits",
                "help": (
                    "Users of this group automatically inherit those groups"
                ),
                "relation": "res.groups",
                "ttype": "many2many",
            },
            "m2o_module": {
                "field_description": "Module",
                "help": "Module",
                "relation": "code.generator.module",
                "ttype": "many2one",
            },
            "menu_access": {
                "field_description": "Access Menu",
                "relation": "ir.ui.menu",
                "ttype": "many2many",
            },
            "rule_groups": {
                "field_description": "Rules",
                "force_domain": [("global", "=", False)],
                "relation": "ir.rule",
                "ttype": "many2many",
            },
            "share": {
                "field_description": "Share Group",
                "help": (
                    "Group created to set access rights for sharing data with"
                    " some users."
                ),
                "ttype": "boolean",
            },
            "trans_implied_ids": {
                "field_description": "Transitively inherits",
                "relation": "res.groups",
                "ttype": "many2many",
            },
            "users": {
                "field_description": "Users",
                "relation": "res.users",
                "ttype": "many2many",
            },
            "view_access": {
                "field_description": "Views",
                "relation": "ir.ui.view",
                "ttype": "many2many",
            },
        }
        model_res_groups = code_generator_id.add_update_model(
            model_model,
            model_name,
            dct_field=dct_field,
        )

        # Added one2many field, many2one need to be create before add one2many
        model_model = "code.generator.ir.model.dependency"
        dct_field = {
            "ir_model_ids": {
                "field_description": "Ir model",
                "ttype": "one2many",
                "help": "Origin model with dependency",
                "relation": "ir.model",
            },
        }
        code_generator_id.add_update_model_one2many(model_model, dct_field)

        model_model = "code.generator.module"
        dct_field = {
            "code_generator_act_window_id": {
                "field_description": "Code Generator Act Window",
                "ttype": "one2many",
                "relation": "code.generator.act_window",
                "relation_field": "code_generator_id",
            },
            "code_generator_menus_id": {
                "field_description": "Code Generator Menus",
                "ttype": "one2many",
                "relation": "code.generator.menu",
                "relation_field": "code_generator_id",
            },
            "code_generator_views_id": {
                "field_description": "Code Generator Views",
                "ttype": "one2many",
                "relation": "code.generator.view",
                "relation_field": "code_generator_id",
            },
            "dependencies_id": {
                "field_description": "Dependencies module",
                "ttype": "one2many",
                "relation": "code.generator.module.dependency",
                "relation_field": "module_id",
            },
            "dependencies_template_id": {
                "field_description": "Dependencies template module",
                "ttype": "one2many",
                "relation": "code.generator.module.template.dependency",
                "relation_field": "module_id",
            },
            "exclusion_ids": {
                "field_description": "Exclusions",
                "ttype": "one2many",
                "relation": "ir.module.module.exclusion",
                "relation_field": "module_id",
            },
            "external_dependencies_id": {
                "field_description": "External Dependencies",
                "ttype": "one2many",
                "relation": "code.generator.module.external.dependency",
                "relation_field": "module_id",
            },
            "o2m_codes": {
                "field_description": "O2M Codes",
                "ttype": "one2many",
                "relation": "code.generator.model.code",
                "relation_field": "m2o_module",
            },
            "o2m_groups": {
                "field_description": "O2M Groups",
                "ttype": "one2many",
                "relation": "res.groups",
                "relation_field": "m2o_module",
            },
            "o2m_menus": {
                "field_description": "O2M Menus",
                "ttype": "one2many",
                "relation": "ir.ui.menu",
                "relation_field": "m2o_module",
            },
            "o2m_model_access": {
                "field_description": "O2M Model Access",
                "ttype": "one2many",
                "relation": "ir.model.access",
            },
            "o2m_model_act_server": {
                "field_description": "O2M Model Act Server",
                "ttype": "one2many",
                "relation": "ir.actions.server",
            },
            "o2m_model_act_todo": {
                "field_description": "O2M Model Act Todo",
                "ttype": "one2many",
                "relation": "ir.actions.todo",
                "relation_field": "m2o_code_generator",
            },
            "o2m_model_act_url": {
                "field_description": "O2M Model Act Url",
                "ttype": "one2many",
                "relation": "ir.actions.act_url",
                "relation_field": "m2o_code_generator",
            },
            "o2m_model_act_window": {
                "field_description": "O2M Model Act Window",
                "ttype": "one2many",
                "relation": "ir.actions.act_window",
            },
            "o2m_model_constraints": {
                "field_description": "O2M Model Constraints",
                "ttype": "one2many",
                "relation": "ir.model.constraint",
                "relation_field": "code_generator_id",
            },
            "o2m_model_reports": {
                "field_description": "O2M Model Reports",
                "ttype": "one2many",
                "relation": "ir.actions.report",
            },
            "o2m_model_rules": {
                "field_description": "O2M Model Rules",
                "ttype": "one2many",
                "relation": "ir.rule",
            },
            "o2m_model_server_constrains": {
                "field_description": "O2M Model Server Constrains",
                "ttype": "one2many",
                "relation": "ir.model.server_constrain",
            },
            "o2m_model_views": {
                "field_description": "O2M Model Views",
                "ttype": "one2many",
                "relation": "ir.ui.view",
            },
            "o2m_models": {
                "field_description": "O2M Models",
                "ttype": "one2many",
                "relation": "ir.model",
                "relation_field": "m2o_module",
            },
            "o2m_nomenclator_blacklist_fields": {
                "field_description": "O2M Nomenclator Blacklist Fields",
                "ttype": "one2many",
                "force_domain": [("nomenclature_blacklist", "=", True)],
                "relation": "code.generator.ir.model.fields",
                "relation_field": "m2o_module",
            },
            "o2m_nomenclator_whitelist_fields": {
                "field_description": "O2M Nomenclator Whitelist Fields",
                "ttype": "one2many",
                "force_domain": [("nomenclature_whitelist", "=", True)],
                "relation": "code.generator.ir.model.fields",
                "relation_field": "m2o_module",
            },
        }
        code_generator_id.add_update_model_one2many(model_model, dct_field)

        model_model = "code.generator.view.item"
        dct_field = {
            "child_id": {
                "field_description": "Child",
                "ttype": "one2many",
                "relation": "code.generator.view.item",
                "relation_field": "parent_id",
            },
        }
        code_generator_id.add_update_model_one2many(model_model, dct_field)

        model_model = "ir.actions.act_window"
        dct_field = {
            "view_ids": {
                "field_description": "No of Views",
                "ttype": "one2many",
                "relation": "ir.actions.act_window.view",
                "relation_field": "act_window_id",
            },
        }
        code_generator_id.add_update_model_one2many(model_model, dct_field)

        model_model = "ir.actions.server"
        dct_field = {
            "fields_lines": {
                "field_description": "Value Mapping",
                "ttype": "one2many",
                "relation": "ir.server.object.lines",
                "relation_field": "server_id",
            },
        }
        code_generator_id.add_update_model_one2many(model_model, dct_field)

        model_model = "ir.model"
        dct_field = {
            "access_ids": {
                "field_description": "Access",
                "ttype": "one2many",
                "relation": "ir.model.access",
                "relation_field": "model_id",
            },
            "field_id": {
                "field_description": "Fields",
                "ttype": "one2many",
                "required": True,
                "relation": "ir.model.fields",
                "relation_field": "model_id",
            },
            "o2m_act_window": {
                "field_description": "Act window",
                "ttype": "one2many",
                "relation": "ir.actions.act_window",
                "relation_field": "m2o_res_model",
            },
            "o2m_code_import": {
                "field_description": "Codes import",
                "ttype": "one2many",
                "relation": "code.generator.model.code.import",
                "relation_field": "m2o_model",
            },
            "o2m_codes": {
                "field_description": "Codes",
                "ttype": "one2many",
                "relation": "code.generator.model.code",
                "relation_field": "m2o_model",
            },
            "o2m_constraints": {
                "field_description": "Constraints",
                "ttype": "one2many",
                "force_domain": [("type", "=", "u"), ("message", "!=", None)],
                "relation": "ir.model.constraint",
                "relation_field": "model",
            },
            "o2m_reports": {
                "field_description": "Reports",
                "ttype": "one2many",
                "help": "Reports associated with this model",
                "relation": "ir.actions.report",
                "relation_field": "m2o_model",
            },
            "o2m_server_action": {
                "field_description": "Server action",
                "ttype": "one2many",
                "force_domain": [
                    ("binding_type", "=", "action"),
                    "|",
                    ("state", "=", "code"),
                    ("state", "=", "multi"),
                    ("usage", "=", "ir_actions_server"),
                ],
                "relation": "ir.actions.server",
                "relation_field": "model_id",
            },
            "o2m_server_constrains": {
                "field_description": "Server Constrains",
                "ttype": "one2many",
                "help": "Server Constrains attach to this model",
                "relation": "ir.model.server_constrain",
                "relation_field": "m2o_ir_model",
            },
            "rule_ids": {
                "field_description": "Record Rules",
                "ttype": "one2many",
                "relation": "ir.rule",
                "relation_field": "model_id",
            },
            "view_ids": {
                "field_description": "Views",
                "ttype": "one2many",
                "relation": "ir.ui.view",
            },
        }
        code_generator_id.add_update_model_one2many(model_model, dct_field)

        model_model = "ir.model.fields"
        dct_field = {
            "code_generator_ir_model_fields_ids": {
                "field_description": "Code Generator Ir Model Fields",
                "ttype": "one2many",
                "help": (
                    "Link to update field when generate, because it cannot"
                    " update ir.model.fields in runtime"
                ),
                "relation": "code.generator.ir.model.fields",
                "relation_field": "m2o_fields",
            },
        }
        code_generator_id.add_update_model_one2many(model_model, dct_field)

        model_model = "ir.module.module"
        dct_field = {
            "dependencies_id": {
                "field_description": "Dependencies",
                "ttype": "one2many",
                "relation": "ir.module.module.dependency",
                "relation_field": "module_id",
            },
            "exclusion_ids": {
                "field_description": "Exclusions",
                "ttype": "one2many",
                "relation": "ir.module.module.exclusion",
                "relation_field": "module_id",
            },
        }
        code_generator_id.add_update_model_one2many(model_model, dct_field)

        model_model = "ir.ui.menu"
        dct_field = {
            "child_id": {
                "field_description": "Child IDs",
                "ttype": "one2many",
                "relation": "ir.ui.menu",
                "relation_field": "parent_id",
            },
        }
        code_generator_id.add_update_model_one2many(model_model, dct_field)

        model_model = "ir.ui.view"
        dct_field = {
            "inherit_children_ids": {
                "field_description": "Views which inherit from this one",
                "ttype": "one2many",
                "relation": "ir.ui.view",
                "relation_field": "inherit_id",
            },
            "model_ids": {
                "field_description": "Models",
                "ttype": "one2many",
                "force_domain": [("model", "=", "ir.ui.view")],
                "relation": "ir.model.data",
            },
        }
        code_generator_id.add_update_model_one2many(model_model, dct_field)

        model_model = "res.groups"
        dct_field = {
            "model_access": {
                "field_description": "Access Controls",
                "ttype": "one2many",
                "relation": "ir.model.access",
                "relation_field": "group_id",
            },
        }
        code_generator_id.add_update_model_one2many(model_model, dct_field)

        # Generate view
        # Action generate view
        wizard_view = env["code.generator.generate.views.wizard"].create(
            {
                "code_generator_id": code_generator_id.id,
                "enable_generate_all": False,
            }
        )

        wizard_view.button_generate_views()

        # Generate module
        value = {"code_generator_ids": code_generator_id.ids}
        env["code.generator.writer"].create(value)


def uninstall_hook(cr, e):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        code_generator_id = env["code.generator.module"].search(
            [("name", "=", MODULE_NAME)]
        )
        if code_generator_id:
            code_generator_id.unlink()

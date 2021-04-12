from odoo import _, api, models, fields, SUPERUSER_ID

import os

MODULE_NAME = "auto_backup"


def post_init_hook(cr, e):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        # The path of the actual file
        path_module_generate = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "OCA_server-tools")
        )

        short_name = MODULE_NAME.replace("_", " ").title()

        # Add code generator
        value = {
            "shortdesc": short_name,
            "name": MODULE_NAME,
            "license": "AGPL-3",
            "author": "TechnoLibre",
            "website": "https://technolibre.ca",
            "application": True,
            "enable_sync_code": True,
            "path_sync_code": path_module_generate,
        }

        # TODO HUMAN: enable your functionality to generate
        value["enable_sync_template"] = True
        value["ignore_fields"] = ""
        value["post_init_hook_show"] = False
        value["uninstall_hook_show"] = False
        value["post_init_hook_feature_code_generator"] = False
        value["uninstall_hook_feature_code_generator"] = False

        value["hook_constant_code"] = f'MODULE_NAME = "{MODULE_NAME}"'

        code_generator_id = env["code.generator.module"].create(value)

        # Add Db Backup
        value = {
            "name": "db_backup",
            "model": "db.backup",
            "m2o_module": code_generator_id.id,
            "rec_name": None,
            "nomenclator": True,
        }
        model_db_backup = env["ir.model"].create(value)

        # Cron
        value = {
            "m2o_module": code_generator_id.id,
            "name": "Backup Scheduler",
            "user_id": env.ref("base.user_root").id,
            "interval_number": 1,
            "interval_type": "days",
            "numbercall": -1,
            "nextcall_template": "(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d 03:00:00')",
            "model_id": model_db_backup.id,
            "state": "code",
            "code": "model.action_backup_all()",
        }
        env["ir.cron"].create(value)

        # action_backup_all function cron
        value = {
            "code": '''"""Run all scheduled backups."""
return self.search([]).action_backup()''',
            "name": "action_backup_all",
            "decorator": "@api.model",
            "param": "",
            "m2o_module": code_generator_id.id,
            "m2o_model": model_db_backup.id,
        }
        env["code.generator.model.code"].create(value)

        # Begin Field
        value_field_backup_format = {
            "name": "backup_format",
            "model": "db.backup",
            "field_description": "Backup Format",
            "code_generator_sequence": 14,
            "ttype": "selection",
            "selection": "[('zip', 'zip (includes filestore)'), ('dump', 'pg_dump custom format (without filestore)')]",
            "model_id": model_db_backup.id,
            "default": "zip",
            "help": "Choose the format for this backup.",
        }
        env["ir.model.fields"].create(value_field_backup_format)

        value_field_days_to_keep = {
            "name": "days_to_keep",
            "model": "db.backup",
            "field_description": "Days To Keep",
            "code_generator_sequence": 6,
            "code_generator_tree_view_sequence": 3,
            "ttype": "integer",
            "model_id": model_db_backup.id,
            "required": True,
            "help": "Backups older than this will be deleted automatically. Set 0 to disable autodeletion.",
        }
        env["ir.model.fields"].create(value_field_days_to_keep)

        value_field_folder = {
            "name": "folder",
            "model": "db.backup",
            "field_description": "Folder",
            "code_generator_sequence": 5,
            "code_generator_tree_view_sequence": 1,
            "code_generator_search_sequence": 2,
            "ttype": "char",
            "model_id": model_db_backup.id,
            "default": "lambda self: self._default_folder()",
            "required": True,
            "help": "Absolute path for storing the backups",
        }
        field_folder = env["ir.model.fields"].create(value_field_folder)

        value_field_method = {
            "name": "method",
            "model": "db.backup",
            "field_description": "Method",
            "code_generator_sequence": 7,
            "ttype": "selection",
            "selection": "[('local', 'Local disk'), ('sftp', 'Remote SFTP server')]",
            "model_id": model_db_backup.id,
            "default": "local",
            "help": "Choose the storage method for this backup.",
        }
        env["ir.model.fields"].create(value_field_method)

        value_field_name = {
            "name": "name",
            "model": "db.backup",
            "field_description": "Name",
            "code_generator_sequence": 4,
            "code_generator_tree_view_sequence": 0,
            "code_generator_search_sequence": 1,
            "ttype": "char",
            "model_id": model_db_backup.id,
            "store": True,
            "code_generator_compute": "_compute_name",
            "help": "Summary of this backup process",
        }
        field_name = env["ir.model.fields"].create(value_field_name)

        value_field_sftp_host = {
            "name": "sftp_host",
            "model": "db.backup",
            "field_description": "SFTP Server",
            "code_generator_sequence": 8,
            "code_generator_search_sequence": 3,
            "ttype": "char",
            "model_id": model_db_backup.id,
            "help": "The host name or IP address from your remote server. For example 192.168.0.1",
        }
        env["ir.model.fields"].create(value_field_sftp_host)

        value_field_sftp_password = {
            "name": "sftp_password",
            "model": "db.backup",
            "field_description": "SFTP Password",
            "code_generator_sequence": 11,
            "ttype": "char",
            "model_id": model_db_backup.id,
            "help": "The password for the SFTP connection. If you specify a private key file, then this is the password to decrypt it.",
        }
        env["ir.model.fields"].create(value_field_sftp_password)

        value_field_sftp_port = {
            "name": "sftp_port",
            "model": "db.backup",
            "field_description": "SFTP Port",
            "code_generator_sequence": 9,
            "ttype": "integer",
            "model_id": model_db_backup.id,
            "default": 22,
            "help": "The port on the FTP server that accepts SSH/SFTP calls.",
        }
        env["ir.model.fields"].create(value_field_sftp_port)

        value_field_sftp_private_key = {
            "name": "sftp_private_key",
            "model": "db.backup",
            "field_description": "Private key location",
            "code_generator_sequence": 12,
            "ttype": "char",
            "model_id": model_db_backup.id,
            "help": "Path to the private key file. Only the Odoo user should have read permissions for that file.",
        }
        env["ir.model.fields"].create(value_field_sftp_private_key)

        value_field_sftp_public_host_key = {
            "name": "sftp_public_host_key",
            "model": "db.backup",
            "field_description": "Public host key",
            "code_generator_sequence": 13,
            "ttype": "char",
            "model_id": model_db_backup.id,
            "help": "Verify SFTP server's identity using its public rsa-key. The host key verification protects you from man-in-the-middle attacks. Can be generated with command 'ssh-keyscan -p PORT -H HOST/IP' and the right key is immediately after the words 'ssh-rsa'.",
        }
        env["ir.model.fields"].create(value_field_sftp_public_host_key)

        value_field_sftp_user = {
            "name": "sftp_user",
            "model": "db.backup",
            "field_description": "Username in the SFTP Server",
            "code_generator_sequence": 10,
            "ttype": "char",
            "model_id": model_db_backup.id,
            "help": "The username where the SFTP connection should be made with. This is the user on the external server.",
        }
        env["ir.model.fields"].create(value_field_sftp_user)

        # Hack to solve field name
        field_x_name = env["ir.model.fields"].search(
            [("model_id", "=", model_db_backup.id), ("name", "=", "x_name")]
        )
        field_x_name.unlink()
        model_db_backup.rec_name = "name"
        # End Field

        # Generate view
        lst_item_view = []
        # Form custom
        if True:
            # HEADER
            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "action_backup",
                    "label": "Execute backup",
                    "section_type": "header",
                    "item_type": "button",
                    "button_type": "oe_highlight",
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item.id)

            # TITLE
            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "name",
                    "section_type": "title",
                    "item_type": "field",
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item.id)

            # BODY
            view_item_group_basic_backup = env["code.generator.view.item"].create(
                {
                    "item_type": "group",
                    "section_type": "body",
                    "label": "Basic backup configuration",
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item_group_basic_backup.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "folder",
                    "section_type": "body",
                    "item_type": "field",
                    "parent_id": view_item_group_basic_backup.id,
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "days_to_keep",
                    "section_type": "body",
                    "item_type": "field",
                    "parent_id": view_item_group_basic_backup.id,
                    "sequence": 2,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "method",
                    "section_type": "body",
                    "item_type": "field",
                    "parent_id": view_item_group_basic_backup.id,
                    "sequence": 3,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "backup_format",
                    "section_type": "body",
                    "item_type": "field",
                    "parent_id": view_item_group_basic_backup.id,
                    "sequence": 4,
                }
            )
            lst_item_view.append(view_item.id)

            view_item_div = env["code.generator.view.item"].create(
                {
                    "item_type": "div",
                    "section_type": "body",
                    "attrs": "{'invisible': [('method', '!=', 'sftp')]}",
                    "sequence": 2,
                }
            )
            lst_item_view.append(view_item_div.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "html",
                    "parent_id": view_item_div.id,
                    "sequence": 1,
                    "background_type": "bg-warning",
                    "label": "Use SFTP with caution! This writes files to external servers under the path you specify.",
                }
            )
            lst_item_view.append(view_item.id)

            view_item_group_sftp = env["code.generator.view.item"].create(
                {
                    "item_type": "group",
                    "section_type": "body",
                    "label": "SFTP Settings",
                    "parent_id": view_item_div.id,
                    "sequence": 2,
                }
            )
            lst_item_view.append(view_item_group_sftp.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "sftp_host",
                    "placeholder": "sftp.example.com",
                    "section_type": "body",
                    "item_type": "field",
                    "parent_id": view_item_group_sftp.id,
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "sftp_port",
                    "section_type": "body",
                    "item_type": "field",
                    "parent_id": view_item_group_sftp.id,
                    "sequence": 2,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "sftp_user",
                    "placeholder": "john",
                    "section_type": "body",
                    "item_type": "field",
                    "parent_id": view_item_group_sftp.id,
                    "sequence": 3,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "sftp_password",
                    "password": True,
                    "section_type": "body",
                    "item_type": "field",
                    "parent_id": view_item_group_sftp.id,
                    "sequence": 4,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "sftp_private_key",
                    "placeholder": "/home/odoo/.ssh/id_rsa",
                    "section_type": "body",
                    "item_type": "field",
                    "parent_id": view_item_group_sftp.id,
                    "sequence": 5,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "sftp_public_host_key",
                    "placeholder": "AAAA...",
                    "section_type": "body",
                    "item_type": "field",
                    "parent_id": view_item_group_sftp.id,
                    "sequence": 6,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "action_name": "action_sftp_test_connection",
                    "label": "Test SFTP Connection",
                    "section_type": "body",
                    "parent_id": view_item_group_sftp.id,
                    "item_type": "button",
                    "icon": "fa-television",
                    "sequence": 7,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "label": """
    Automatic backups of the database can be scheduled as follows:
    <ol>
        <li>Go to Settings / Technical / Automation / Scheduled Actions.</li>
        <li>Search the action named 'Backup scheduler'.</li>
        <li>Set the scheduler to active and fill in how often you want backups generated.</li>
    </ol>
    """,
                    "colspan": 2,
                    "section_type": "body",
                    "item_type": "html",
                    "is_help": True,
                    "sequence": 10,
                }
            )
            lst_item_view.append(view_item.id)

            view_code_generator = env["code.generator.view"].create(
                {
                    "code_generator_id": code_generator_id.id,
                    "view_type": "form",
                    # "view_name": "view_backup_conf_form",
                    "m2o_model": model_db_backup.id,
                    "view_item_ids": [(6, 0, lst_item_view)],
                    "has_body_sheet": False,
                }
            )

        # tree view
        if True:
            pass

        # search view
        if True:
            pass

        # act_window view
        if True:
            pass

        # action server view
        if True:
            pass

        # menu view
        if True:
            pass

        # portal view
        if True:
            pass

        # website view
        if True:
            pass

        # Action generate view
        wizard_view = env["code.generator.generate.views.wizard"].create(
            {
                "code_generator_id": code_generator_id.id,
                "enable_generate_all": False,
                "code_generator_view_ids": [(6, 0, view_code_generator.ids)],
            }
        )

        wizard_view.button_generate_views()

        # Generate module
        value = {"code_generator_ids": code_generator_id.ids}
        code_generator_writer = env["code.generator.writer"].create(value)


def uninstall_hook(cr, e):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        code_generator_id = env["code.generator.module"].search([("name", "=", MODULE_NAME)])
        if code_generator_id:
            code_generator_id.unlink()

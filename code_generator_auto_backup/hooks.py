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

        ##### Cron
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

        ##### Begin Field
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
            "ttype": "char",
            "model_id": model_db_backup.id,
            "default": "lambda self: self._default_folder()",
            "required": True,
            "help": "Absolute path for storing the backups",
        }
        env["ir.model.fields"].create(value_field_folder)

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
            "ttype": "char",
            "model_id": model_db_backup.id,
            "store": True,
            "code_generator_compute": "_compute_name",
            "help": "Summary of this backup process",
        }
        env["ir.model.fields"].create(value_field_name)

        value_field_sftp_host = {
            "name": "sftp_host",
            "model": "db.backup",
            "field_description": "SFTP Server",
            "code_generator_sequence": 8,
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
        ##### End Field

        # Generate view
        ##### Begin Views
        lst_view_id = []
        # form view
        if True:
            lst_item_view = []
            # HEADER
            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "header",
                    "item_type": "button",
                    "action_name": "action_backup",
                    "button_type": "oe_highlight",
                    "label": "Execute backup",
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item.id)

            # TITLE
            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "title",
                    "item_type": "field",
                    "action_name": "name",
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item.id)

            # BODY
            view_item_body_1 = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "group",
                    "label": "Basic backup configuration",
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item_body_1.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "folder",
                    "parent_id": view_item_body_1.id,
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "days_to_keep",
                    "parent_id": view_item_body_1.id,
                    "sequence": 2,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "method",
                    "parent_id": view_item_body_1.id,
                    "sequence": 3,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "backup_format",
                    "parent_id": view_item_body_1.id,
                    "sequence": 4,
                }
            )
            lst_item_view.append(view_item.id)

            view_item_body_2 = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "div",
                    "attrs": "{'invisible': [('method', '!=', 'sftp')]}",
                    "sequence": 2,
                }
            )
            lst_item_view.append(view_item_body_2.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "html",
                    "background_type": "bg-warning",
                    "label": "Use SFTP with caution! This writes files to external servers under the path you specify.",
                    "parent_id": view_item_body_2.id,
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item.id)

            view_item_body_2 = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "group",
                    "label": "SFTP Settings",
                    "parent_id": view_item_body_2.id,
                    "sequence": 2,
                }
            )
            lst_item_view.append(view_item_body_2.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "sftp_host",
                    "placeholder": "sftp.example.com",
                    "parent_id": view_item_body_2.id,
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "sftp_port",
                    "parent_id": view_item_body_2.id,
                    "sequence": 2,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "sftp_user",
                    "placeholder": "john",
                    "parent_id": view_item_body_2.id,
                    "sequence": 3,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "sftp_password",
                    "password": True,
                    "parent_id": view_item_body_2.id,
                    "sequence": 4,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "sftp_private_key",
                    "placeholder": "/home/odoo/.ssh/id_rsa",
                    "parent_id": view_item_body_2.id,
                    "sequence": 5,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "sftp_public_host_key",
                    "placeholder": "AAAA...",
                    "parent_id": view_item_body_2.id,
                    "sequence": 6,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "button",
                    "action_name": "action_sftp_test_connection",
                    "icon": "fa-television",
                    "label": "Test SFTP Connection",
                    "parent_id": view_item_body_2.id,
                    "sequence": 7,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "html",
                    "colspan": 2,
                    "label": """
                    Automatic backups of the database can be scheduled as follows:
                    <ol>
                    <li>Go to Settings / Technical / Automation / Scheduled Actions.</li>
                    <li>Search the action named 'Backup scheduler'.</li>
                    <li>Set the scheduler to active and fill in how often you want backups generated.</li>
                    </ol>
                    """,
                    "is_help": True,
                    "sequence": 4,
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
                    "id_name": "view_backup_conf_form",
                }
            )
            lst_view_id.append(view_code_generator.id)

        # tree view
        if True:
            lst_item_view = []
            # BODY
            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "name",
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "folder",
                    "sequence": 2,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "days_to_keep",
                    "sequence": 3,
                }
            )
            lst_item_view.append(view_item.id)

            view_code_generator = env["code.generator.view"].create(
                {
                    "code_generator_id": code_generator_id.id,
                    "view_type": "tree",
                    # "view_name": "view_backup_conf_form",
                    "m2o_model": model_db_backup.id,
                    "view_item_ids": [(6, 0, lst_item_view)],
                    "id_name": "view_backup_conf_tree",
                }
            )
            lst_view_id.append(view_code_generator.id)

        # search view
        if True:
            lst_item_view = []
            # BODY
            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "name",
                    "sequence": 1,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "folder",
                    "sequence": 2,
                }
            )
            lst_item_view.append(view_item.id)

            view_item = env["code.generator.view.item"].create(
                {
                    "section_type": "body",
                    "item_type": "field",
                    "action_name": "sftp_host",
                    "sequence": 3,
                }
            )
            lst_item_view.append(view_item.id)

            view_code_generator = env["code.generator.view"].create(
                {
                    "code_generator_id": code_generator_id.id,
                    "view_type": "search",
                    # "view_name": "view_backup_conf_form",
                    "m2o_model": model_db_backup.id,
                    "view_item_ids": [(6, 0, lst_item_view)],
                    "id_name": "view_backup_conf_search",
                }
            )
            lst_view_id.append(view_code_generator.id)

        # act_window view
        if True:
            action_backup_conf_form = env["code.generator.act_window"].create(
                {
                    "code_generator_id": code_generator_id.id,
                    "name": "Automated Backups",
                    "id_name": "action_backup_conf_form",
                }
            )

        # action_server view
        if True:
            pass

        # menu view
        if True:
            env["code.generator.menu"].create(
                {
                    "code_generator_id": code_generator_id.id,
                    "id_name": "backup_conf_menu",
                    "parent_id_name": "base.next_id_9",
                    "m2o_act_window": action_backup_conf_form.id,
                }
            )
        ##### End Views

        # Action generate view
        wizard_view = env["code.generator.generate.views.wizard"].create(
            {
                "code_generator_id": code_generator_id.id,
                "enable_generate_all": False,
                "code_generator_view_ids": [(6, 0, lst_view_id)],
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

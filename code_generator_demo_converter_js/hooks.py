import html
import os
import tempfile
from collections import namedtuple

import requests
import tree_sitter_javascript
import wget
from bs4 import BeautifulSoup
from odoo import SUPERUSER_ID, _, api, fields, models
from tree_sitter import Language, Parser

MODULE_NAME = "demo_business_plan"

# TODO Update keys for your Webfetcher
URL_HTML = ""
URL_JS = ""
KEY_JS_VARIABLE = ""
KEY_GOOD_JS_FILE = ""
KEY_REMOVE_SECTION_JS_FILE = ""
KEY_TO_ADD_BEGIN_FILE = """"""
KEY_CHILD = ""
KEY_DISABLED_CHILD = ""
KEY_CLASS_HELP = ""
KEY_ALL_DIV = ""
KEY_ALL_INPUT = ""
KEY_ALL_TEXTAREA = ""
KEY_ALL_RADIOBUTTON = ""
PREFIX_MODEL = ""

# Constant
TTYPE_INPUT = "char"
TTYPE_TEXTAREA = "html"
KEEP_CACHE = True
JS_LANGUAGE = Language(tree_sitter_javascript.language())
JS_ESCAPES = {
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
}
JS_LINE_TERMINATORS = ("\r\n", "\n", "\r", "\u2028", "\u2029")


def js_escape_to_text(sequence):
    body = sequence[1:]
    if body in JS_LINE_TERMINATORS:
        # Line continuation: the backslash and the newline vanish
        return ""
    if body[0] == "x":
        return chr(int(body[1:], 16))
    if body[0] == "u":
        return chr(int(body[1:].strip("{}"), 16))
    if body.isdigit() and "8" not in body and "9" not in body:
        # Legacy octal escape, \0 included
        return chr(int(body, 8))
    return JS_ESCAPES.get(body, body)


def js_string_to_text(node):
    parts = []
    for child in node.named_children:
        if child.type == "string_fragment":
            parts.append(child.text.decode())
        elif child.type == "escape_sequence":
            parts.append(js_escape_to_text(child.text.decode()))
        elif child.type == "template_substitution":
            raise ValueError(
                f"Template string with substitution is not a literal: "
                f"{node.text.decode()[:80]}"
            )
    # \uD83D\uDE00 decodes to two surrogates, joined back here
    return "".join(parts).encode("utf-16", "surrogatepass").decode("utf-16")


def js_number_to_python(text):
    text = text.replace("_", "")
    if text[:2].lower() in ("0x", "0o", "0b"):
        return int(text, 0)
    if any(char in text for char in ".eE"):
        return float(text)
    if len(text) > 1 and text[0] == "0":
        # Legacy octal literal
        return int(text, 8)
    return int(text)


def js_literal_to_python(node):
    """Return the Python value of a JavaScript literal, executing nothing.

    Accepts arrays, objects, strings, template strings without substitution,
    numbers, booleans, null, undefined, a sign before a number and "+"
    between two literals. Anything else — a call, a variable, a computed or
    shorthand key, a spread — raises ValueError: the file is downloaded, and
    evaluating it would run whatever code it carries.
    """
    node_type = node.type
    if node_type == "parenthesized_expression":
        return js_literal_to_python(node.named_children[0])
    if node_type in ("string", "template_string"):
        return js_string_to_text(node)
    if node_type == "number":
        return js_number_to_python(node.text.decode())
    if node_type in ("true", "false"):
        return node_type == "true"
    if node_type in ("null", "undefined"):
        return None
    if node_type == "array":
        return [
            js_literal_to_python(child)
            for child in node.named_children
            if child.type != "comment"
        ]
    if node_type == "object":
        result = {}
        for child in node.named_children:
            if child.type == "comment":
                continue
            if child.type != "pair":
                raise ValueError(
                    f"Unsupported object member {child.type}: "
                    f"{child.text.decode()[:80]}"
                )
            key = child.child_by_field_name("key")
            if key.type == "property_identifier":
                key_value = key.text.decode()
            elif key.type in ("string", "number"):
                key_value = str(js_literal_to_python(key))
            else:
                raise ValueError(
                    f"Unsupported object key {key.type}: "
                    f"{key.text.decode()[:80]}"
                )
            result[key_value] = js_literal_to_python(
                child.child_by_field_name("value")
            )
        return result
    if node_type == "unary_expression":
        operator = node.child_by_field_name("operator").type
        value = js_literal_to_python(node.child_by_field_name("argument"))
        if operator in ("-", "+") and isinstance(value, (int, float)):
            return -value if operator == "-" else value
    if node_type == "binary_expression":
        if node.child_by_field_name("operator").type == "+":
            left = js_literal_to_python(node.child_by_field_name("left"))
            right = js_literal_to_python(node.child_by_field_name("right"))
            if isinstance(left, str) or isinstance(right, str):
                return f"{left}{right}"
            return left + right
    raise ValueError(
        f"Not a JavaScript literal ({node_type}): {node.text.decode()[:80]}"
    )


def extract_js_variable(source, name):
    """Return the value last assigned to the variable name in source.

    Both a declaration (var, let, const) and a plain assignment count, the
    last one in the file winning as it would at run time. The value must be
    a literal, see js_literal_to_python. Raises ValueError when name is never
    assigned.
    """
    tree = Parser(JS_LANGUAGE).parse(source.encode())
    value_node = None
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type == "variable_declarator":
            target = node.child_by_field_name("name")
            value = node.child_by_field_name("value")
        elif node.type == "assignment_expression":
            target = node.child_by_field_name("left")
            value = node.child_by_field_name("right")
        else:
            target = value = None
        if (
            target is not None
            and value is not None
            and target.type == "identifier"
            and target.text.decode() == name
        ):
            value_node = value
        # Reversed, so nodes come out of the stack in source order
        stack.extend(reversed(node.children))
    if value_node is None:
        raise ValueError(f"No assignment to JavaScript variable {name}")
    return js_literal_to_python(value_node)


def download_url_and_get_content(url, dir_path):
    if KEEP_CACHE:
        filename_js = wget.download(url, out=dir_path)
        with open(filename_js, "r") as file:
            content = file.read()
    else:
        r = requests.get(url)
        if r.status_code == 200:
            content = r.text

    return content.strip()


def convert_text_to_variable_name(content):
    # Cannot start by number
    if content[0].isdigit():
        content = f"s_{content}"

    content = content.replace("'", "")
    content = content.replace('"', "")
    content = content.replace(" &", "")
    content = content.replace(" /", "")
    content = content.replace("/", " ")
    content = content.replace("-", "_")
    return content.lower().replace(" ", "_")


def convert_text_to_model_name(content):
    content = content.replace(" &", "")
    # content = content.replace("'", "")
    # content = content.replace('"', "")
    # content = content.replace(" /", "")
    # content = content.replace("/", " ")
    # content = content.replace("-", "_")
    return content.lower().replace(" ", ".")


def convert_html_to_text(content):
    return html.unescape(content)


def amend_sentence(string):
    result = ""
    string = list(string)

    # Traverse the string
    for i in range(len(string)):

        # Convert to lowercase if its
        # an uppercase character
        if string[i] >= "A" and string[i] <= "Z":
            string[i] = chr(ord(string[i]) + 32)

            # Print space before it
            # if its an uppercase character
            if i != 0:
                result += " "

                # Print the character
            result += string[i]

            # if lowercase character
        # then just print
        else:
            result += string[i]
    return result.title()


def extract_field_from_html(content):
    lst_field = []
    soup = BeautifulSoup(content, "html.parser")
    all_div = soup.find_all("div", class_=KEY_ALL_DIV)
    for div in all_div:
        # Get help
        lst_div_help = div.find_all("label", class_=KEY_CLASS_HELP)
        if not lst_div_help or len(lst_div_help) > 1:
            # TODO support table of data
            if len(lst_div_help) > 1:
                # Detect matrix, ignore it
                print(f"Ignore {lst_div_help}, continue..")
                continue
            print(f"Ignore content {div}, continue...")
            continue
            # raise ValueError(f"Wrong format of div_help: {lst_div_help}")
        lst_div_help = lst_div_help[0].contents
        help_str = ""
        for help in lst_div_help:
            if str(help) in ("<br/>", "<br />"):
                help_str += "\n"
            else:
                help_str += help.strip().replace("'", "\\'")
        # Get description
        lst_div_content = div.find_all("textarea", class_=KEY_ALL_TEXTAREA)
        ttype = TTYPE_TEXTAREA
        if not lst_div_content:
            lst_div_content = div.find_all("input", class_=KEY_ALL_INPUT)
            ttype = TTYPE_INPUT
        if not lst_div_content:
            # TODO support KEY_ALL_RADIOBUTTON
            lst_div_content = div.find_all("div", class_=KEY_ALL_RADIOBUTTON)
            print(f"Ignore radio button {lst_div_content}, continue...")
            continue
        if not lst_div_content:
            raise ValueError(f"Wrong format of div_field: {lst_div_content}")
        for div_content in lst_div_content:
            content_id = div_content.get("id")
            content_placeholder = div_content.get("placeholder")
            if content_placeholder:
                # Move placeholder in help
                content_placeholder = content_placeholder.replace("'", "\\'")
                help_str += f"\n--\n{content_placeholder}"
            name = convert_text_to_variable_name(amend_sentence(content_id))
            description = amend_sentence(content_id)
            field = {
                "help": help_str,
                "name": name,
                "description": description,
                "ttype": ttype,
            }
            field_obj = namedtuple("ObjectName", field.keys())(*field.values())
            lst_field.append(field_obj)

    return lst_field


def generate_model_from_js():
    assert URL_JS, "Need to fill constant URL_JS"
    lst_data = []
    lst_translation = []
    # ignore KEEP_CACHE, or delete it if necessary
    temp_dir_path = tempfile.mkdtemp()
    print(f"Debug temp dir {temp_dir_path}")
    path_js = os.path.join(temp_dir_path, "file_to_convert.js")
    filename_js = wget.download(URL_JS, out=path_js)
    # Special treatment, support only specific js
    with open(filename_js, "r") as file:
        file_content = file.read()
        assert (
            KEY_GOOD_JS_FILE not in file_content
        ), f"js {URL_JS} not supported, need key {KEY_GOOD_JS_FILE}"
        if KEY_REMOVE_SECTION_JS_FILE in file_content:
            file_content = file_content[
                : file_content.rfind(KEY_REMOVE_SECTION_JS_FILE)
            ]
        file_content = KEY_TO_ADD_BEGIN_FILE + file_content.replace(
            KEY_JS_VARIABLE, "content"
        )
    lst_extract_info = extract_js_variable(file_content, "content")
    for dct_extract_info in lst_extract_info:
        data = {}
        info = namedtuple("ObjectName", dct_extract_info.keys())(
            *dct_extract_info.values()
        )
        child_disabled_info = dct_extract_info.get(KEY_DISABLED_CHILD)
        if child_disabled_info:
            print(child_disabled_info)
            raise ValueError(f"Do not support {KEY_DISABLED_CHILD}.")
        new_fr_url = os.path.join(URL_HTML, "fr", info.Url[1:])
        data["url_fr"] = new_fr_url
        data["data_fr"] = download_url_and_get_content(
            new_fr_url, temp_dir_path
        )
        new_en_url = os.path.join(URL_HTML, "en", info.Url[1:])
        data["url_en"] = new_en_url
        data["data_en"] = download_url_and_get_content(
            new_en_url, temp_dir_path
        )
        data["title_fr"] = convert_html_to_text(info.FrTitle)
        data["title_en"] = info.EnTitle
        lst_translation.append((data["title_en"], data["title_fr"]))
        child_info = dct_extract_info.get(KEY_CHILD)
        if child_info:
            lst_child = []
            for dct_sub_link in child_info:
                sub_link = namedtuple("ObjectName", dct_sub_link.keys())(
                    *dct_sub_link.values()
                )
                dct_child = {}
                new_fr_url = os.path.join(URL_HTML, "fr", sub_link.Url[1:])
                dct_child["url_fr"] = new_fr_url
                dct_child["data_fr"] = download_url_and_get_content(
                    new_fr_url, temp_dir_path
                )
                new_en_url = os.path.join(URL_HTML, "en", sub_link.Url[1:])
                dct_child["url_en"] = new_en_url
                dct_child["data_en"] = download_url_and_get_content(
                    new_en_url, temp_dir_path
                )
                dct_child["title_fr"] = convert_html_to_text(sub_link.FrTitle)
                dct_child["title_en"] = sub_link.EnTitle
                lst_translation.append(
                    (dct_child["title_en"], dct_child["title_fr"])
                )
                dct_child["fields"] = extract_field_from_html(
                    dct_child["data_en"]
                )
                dct_child["fields_fr"] = extract_field_from_html(
                    dct_child["data_fr"]
                )
                sub_child_info = dct_sub_link.get(KEY_CHILD)
                if sub_child_info:
                    print(sub_child_info)
                    raise ValueError(f"Do not support {KEY_CHILD}.")
                child_obj = namedtuple("ObjectName", dct_child.keys())(
                    *dct_child.values()
                )
                lst_child.append(child_obj)
            data["child"] = lst_child
        data_obj = namedtuple("ObjectName", data.keys())(*data.values())
        lst_data.append(data_obj)

    return lst_data, lst_translation


def generate_i18n(module_name, module_path, lst_translation):
    i18n_path = os.path.join(module_path, "i18n")
    os.makedirs(i18n_path, exist_ok=True)
    translation_file = os.path.join(i18n_path, f"{module_name}.pot")
    with open(translation_file, "w") as file:
        file.write('# Translation for Odoo Server."\n')
        file.write('msgid ""\n')
        file.write('msgstr ""\n')
        file.write('"Project-Id-Version: Odoo Server 12.0"\n')
        file.write("\n")
        for txt_en, _ in lst_translation:
            new_txt_en = txt_en.replace("\n", "\\n").replace('"', '\\"')
            file.write(f"#. module: {module_name}\n")
            file.write(f"#:\n")
            file.write(f'msgid "{new_txt_en}"\n')
            file.write('msgstr ""\n\n')

    translation_file = os.path.join(i18n_path, f"fr_CA.po")
    with open(translation_file, "w") as file:
        file.write('# Translation for Odoo Server."\n')
        file.write('msgid ""\n')
        file.write('msgstr ""\n')
        file.write('"Project-Id-Version: Odoo Server 12.0"\n')
        file.write("\n")
        for txt_en, txt_fr in lst_translation:
            new_txt_en = txt_en.replace("\n", "\\n").replace('"', '\\"')
            new_txt_fr = txt_fr.replace("\n", "\\n").replace('"', '\\"')
            file.write(f"#. module: {module_name}\n")
            file.write(f"#:\n")
            file.write(f'msgid "{new_txt_en}"\n')
            file.write(f'msgstr "{new_txt_fr}"\n\n')


def post_init_hook(env):
    lst_data, lst_translation = generate_model_from_js()

    # The path of the actual file
    path_module_generate = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..")
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
        # "path_sync_code": path_module_generate,
    }

    # TODO HUMAN: enable your functionality to generate
    value["enable_sync_template"] = False
    value["post_init_hook_show"] = False
    value["uninstall_hook_show"] = False
    value["post_init_hook_feature_code_generator"] = False
    value["uninstall_hook_feature_code_generator"] = False

    value["hook_constant_code"] = f'MODULE_NAME = "{MODULE_NAME}"'

    code_generator_id = env["code.generator.module"].create([value])

    value = {
        "name": "Business Plan",
        "model": PREFIX_MODEL,
        "m2o_module": code_generator_id.id,
        "rec_name": None,
        "nomenclator": True,
    }
    model_business_plan = env["ir.model"].create([value])

    # Hack to solve field name
    field_x_name = env["ir.model.fields"].search(
        [
            ("model_id", "=", model_business_plan.id),
            ("name", "=", "x_name"),
        ]
    )
    field_x_name.name = "name"
    model_business_plan.rec_name = "name"

    for data in lst_data:
        model = f"{PREFIX_MODEL}.{convert_text_to_model_name(data.title_en)}"
        data_name = convert_text_to_variable_name(data.title_en)
        value = {
            "name": data.title_en,
            "model": model,
            "m2o_module": code_generator_id.id,
            "rec_name": None,
            "nomenclator": True,
        }
        model_data = env["ir.model"].create(value)

        ##### Begin Field
        for child in data.child:
            # TODO create group
            i = -1
            for field in child.fields:
                i += 1
                # name = convert_text_to_variable_name(child.title_en)
                value_field_demo_html = {
                    "name": field.name,
                    "model": model,
                    "field_description": field.description,
                    "help": field.help,
                    "ttype": field.ttype,
                    "model_id": model_data.id,
                }

                try:
                    field_fr = child.fields_fr[i]
                    lst_translation.append(
                        (field.description, field_fr.description)
                    )
                    lst_translation.append((field.help, field_fr.help))
                except Exception as e:
                    print(e)
                try:
                    env["ir.model.fields"].create(value_field_demo_html)
                except Exception as e:
                    print(e)

        # Link with business plan
        value_field_business_plan_many2one = {
            "name": data_name,
            "model": PREFIX_MODEL,
            "field_description": data.title_en,
            "ttype": "many2one",
            # TODO remove comodel_name from code_generator
            "relation": model,
            "model_id": model_business_plan.id,
        }
        env["ir.model.fields"].create(value_field_business_plan_many2one)

        value_field_business_plan_one2many = {
            "name": "business_plan_id",
            "model": model,
            "field_description": "Business Plan",
            "ttype": "one2many",
            "relation": PREFIX_MODEL,
            "relation_field": data_name,
            "model_id": model_data.id,
        }
        env["ir.model.fields"].create(value_field_business_plan_one2many)

        # Hack to solve field name
        field_x_name = env["ir.model.fields"].search(
            [("model_id", "=", model_data.id), ("name", "=", "x_name")]
        )
        field_x_name.name = "name"
        model_data.rec_name = "name"
        ##### End Field

    # Generate view
    wizard_view = env["code.generator.generate.views.wizard"].create(
        {
            "code_generator_id": code_generator_id.id,
            "enable_generate_all": False,
            # 'enable_generate_portal': True,
        }
    )

    wizard_view.button_generate_views()

    # Generate module
    value = {"code_generator_ids": code_generator_id.ids}
    code_generator_writer = env["code.generator.writer"].create(value)

    new_module_path = os.path.join(path_module_generate, MODULE_NAME)
    generate_i18n(MODULE_NAME, new_module_path, lst_translation)


def uninstall_hook(env):
    code_generator_id = env["code.generator.module"].search(
        [("name", "=", MODULE_NAME)]
    )
    if code_generator_id:
        code_generator_id.unlink()

import json
def match_template(template, **kwargs):
    str_message = template
    str_message = str_message.format(**kwargs)
    str_message = str_message.replace("{{","{")
    str_message = str_message.replace("}}","}")
    return json.loads(str_message)
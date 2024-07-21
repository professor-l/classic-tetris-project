import re

def parse_docstring(doc: str):
    doc = re.sub(r"\n *", r"\n", doc)
    doc = re.sub(r"([^\n])\n([^\n])", r"\1 \2", doc)
    doc = doc.strip()
    return doc

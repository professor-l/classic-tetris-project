from hamcrest.core.base_matcher import BaseMatcher
import lxml.html

class UsesTemplate(BaseMatcher):
    def __init__(self, template):
        self.template = template

    def _matches(self, response):
        for template in response.templates:
            if template.name == self.template:
                return True
        return False

    def describe_to(self, description):
        description.append_text(f"uses template: '{self.template}'")

    def describe_mismatch(self, response, description):
        description.append_text("used templates: ")
        description.append_text(str([t.name for t in response.templates]))

def uses_template(template):
    return UsesTemplate(template)


class HasHtml(BaseMatcher):
    def __init__(self, selector, text):
        self.selector = selector
        self.text = text

    def _matches(self, response):
        html = lxml.html.fromstring(response.content)
        elements = html.cssselect(self.selector)
        if not elements:
            return False
        if self.text:
            for element in elements:
                if element.text.strip() == self.text:
                    return True
        else:
            return True
        return False

    def describe_to(self, description):
        description.append_text(f"HTML with element matching '{self.selector}'")
        if self.text:
            description.append_text(f" with text '{self.text}'")

    def describe_mismatch(self, response, description):
        description.append_text("got ")
        description.append_text(response.content)

def has_html(selector, text=None):
    return HasHtml(selector, text)


class RedirectsTo(BaseMatcher):
    def __init__(self, url, status_code):
        self.url = url
        self.status_code = status_code

    def _matches(self, response):
        return response.status_code == self.status_code and response.url == self.url

    def describe_to(self, description):
        description.append_text(f"redirect to '{self.url}' with status code {self.status_code}")

def redirects_to(url, status_code=302):
    return RedirectsTo(url, status_code)

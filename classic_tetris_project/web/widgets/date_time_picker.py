from django import forms
from datetime import datetime, timedelta

from classic_tetris_project.util import memoize

class DateTimePicker(forms.widgets.Input):
    input_type = "hidden"
    template_name = "widgets/date_time_picker.html"

    def format_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return value

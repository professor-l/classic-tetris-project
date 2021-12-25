from django import forms

class DateTimePicker(forms.widgets.Input):
    input_type = "text"
    template_name = "widgets/date_time_picker.html"

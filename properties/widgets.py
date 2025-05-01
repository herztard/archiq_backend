from django.forms.widgets import FileInput
from django.utils.safestring import mark_safe


class S3FileUploadWidget(FileInput):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and hasattr(value, "url"):
            output.append(f'<p>Текущий файл: <a href="{value}" target="_blank">{value}</a></p>')
        output.append(super().render(name, value, attrs, renderer))
        return mark_safe(''.join(output)) 
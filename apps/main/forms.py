import re

from django import forms

from apps.main.models import Lead


class LeadForm(forms.ModelForm):
    # Длиннее, чем в модели: пользователь вводит телефон с маской, в базу идёт +7XXXXXXXXXX
    phone = forms.CharField(
        label="Телефон",
        max_length=30,
        error_messages={"required": "Укажите телефон"},
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
    )

    class Meta:
        model = Lead
        fields = ("name", "phone", "car_model", "source")
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "source": forms.HiddenInput(),
        }
        error_messages = {
            "name": {"required": "Укажите имя"},
        }

    def clean_name(self) -> str:
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Укажите имя")
        return name

    def clean_phone(self) -> str:
        """Приводит телефон к виду +7XXXXXXXXXX: принимает 8…, 7…, +7… и 10 цифр."""
        digits = re.sub(r"\D", "", self.cleaned_data["phone"])
        if len(digits) == 11 and digits[0] in "78":
            digits = digits[1:]
        if len(digits) != 10:
            raise forms.ValidationError("Введите номер в формате +7 (999) 123-45-67")
        return f"+7{digits}"

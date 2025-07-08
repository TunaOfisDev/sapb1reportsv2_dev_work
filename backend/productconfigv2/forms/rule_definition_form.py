# backend/productconfigv2/forms/rule_definition_form.py

from django import forms
from ..models import Rule


class RuleDefinitionForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = [
            "product_family", "rule_type", "name",
            "conditions", "actions"
        ]
        widgets = {
            "product_family": forms.Select(attrs={"class": "form-control"}),
            "rule_type": forms.Select(choices=Rule.RULE_TYPE_CHOICES, attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "conditions": forms.Textarea(attrs={"rows": 5, "class": "form-control", "placeholder": '{"Engine": "500cc"}'}),
            "actions": forms.Textarea(attrs={"rows": 5, "class": "form-control", "placeholder": '{"disable": ["Option1", "Option2"]}'}),
        }

    def clean_conditions(self):
        import json
        data = self.cleaned_data["conditions"]
        try:
            parsed = json.loads(data)
            return parsed
        except Exception as e:
            raise forms.ValidationError(f"Geçersiz JSON formatı: {e}")

    def clean_actions(self):
        import json
        data = self.cleaned_data["actions"]
        try:
            parsed = json.loads(data)
            return parsed
        except Exception as e:
            raise forms.ValidationError(f"Geçersiz JSON formatı: {e}")

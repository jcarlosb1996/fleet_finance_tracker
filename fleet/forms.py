from decimal import Decimal
from django import forms
from .models import Deposit, Vehicle , Partner
from .models import RecurringExpense
from django.utils import timezone

class RecurringExpenseForm(forms.ModelForm):
    class Meta:
        model = RecurringExpense
        fields = ["name", "vehicle", "amount_monthly", "notes"]
class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['name','email']


class DepositForm(forms.ModelForm):
    paid_at = forms.DateField(                      # optional: lets you set formats & initial
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d", "%m/%d/%Y"],     # user can also type
        initial=timezone.now().date,                # optional: prefill today
    )

    class Meta:
        model = Deposit
        fields = ["source", "vehicle", "paid_at", "amount_net", "notes"]
        help_texts = {
            "paid_at": "The date the money hit your account.",
            "amount_net": "Net amount of this deposit (after any platform fees).",
        }

class VehicleForm(forms.ModelForm):
    shared = forms.BooleanField(
        label="Share this vehicle with a partner",
        required=False
    )

    class Meta:
        model = Vehicle
        fields = ["name", "plate", "year", "make", "model", "image", "partner", "partner_pct", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an instance, pre-check shared when partner split exists
        inst = self.instance
        if inst and (inst.partner and (inst.partner_pct or 0) > 0):
            self.fields["shared"].initial = True

    def clean(self):
        cleaned = super().clean()
        shared = cleaned.get("shared")
        partner = cleaned.get("partner")
        pct = cleaned.get("partner_pct") or Decimal("0.00")

        if shared:
            if not partner:
                raise forms.ValidationError("Select a partner when 'Share this vehicle' is checked.")
            if pct <= 0 or pct > 100:
                raise forms.ValidationError("Partner percentage must be > 0 and ≤ 100.")
        else:
            # Force 100% yours
            cleaned["partner"] = None
            cleaned["partner_pct"] = Decimal("0.00")

        return cleaned

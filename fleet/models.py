from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta, date

class RecurringExpense(models.Model):
    name = models.CharField(max_length=120)
    vehicle = models.ForeignKey(
        "Vehicle",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recurring_expenses",
        help_text="Leave blank for a global expense (applies 100% to you)."
    )
    amount_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
            return f"{self.name}{f' ({self.vehicle.name})' if self.vehicle else ''}"

    def weekly_amount(self):
        """
        Your preference: divide monthly by 4 (simple).
        """
        return (self.amount_monthly / Decimal("4")).quantize(Decimal("0.01"))

    def owner_weekly_share(self):
        """
        How much YOU pay each week.
        - If the expense is tied to a shared vehicle (vehicle has a partner), you pay 50%.
        - If it's your own vehicle or a global expense (no vehicle), you pay 100%.
        """
        wk = self.weekly_amount()
        if self.vehicle and self.vehicle.partner:
            return (wk * Decimal("0.50")).quantize(Decimal("0.01"))
        return wk

class Partner(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

class Vehicle(models.Model):

    name = models.CharField(max_length=120)           # e.g., "2019 Toyota RAV4"
    plate = models.CharField(max_length=20, blank=True)
    year  = models.PositiveIntegerField(blank=True, null=True)
    make  = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)

    image = models.ImageField(upload_to="vehicles/", blank=True, null=True)

    partner = models.ForeignKey(Partner, null=True, blank=True, on_delete=models.SET_NULL)
    partner_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))

    notes = models.TextField(blank=True)

    def clean(self):
        if self.partner_pct < 0 or self.partner_pct > 100:
            raise ValidationError("partner_pct must be between 0 and 100.")

    @property
    def owner_pct(self) -> Decimal:
        return Decimal("100.00") - (self.partner_pct or Decimal("0.00"))

    def __str__(self):
        return self.name


class IncomeSource(models.TextChoices):
    TURO   = "TURO",   "Turo"
    UBER   = "UBER",   "Uber"
    AMAZON = "AMAZON", "Amazon"
    OTHER  = "OTHER",  "Other"


class Deposit(models.Model):
   
    vehicle = models.ForeignKey(Vehicle, null=True, blank=True,
                                on_delete=models.SET_NULL, related_name="deposits")
    source = models.CharField(max_length=12, choices=IncomeSource.choices, default=IncomeSource.TURO)

    # The actual calendar date the money hit your account
    paid_at = models.DateField()

    # Net amount of this deposit (already after platform fees if you record that way)
    amount_net = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # Snapshot splits for reporting
    owner_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    partner_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # (Optional) store the computed Monday of the week for fast grouping
    week_start = models.DateField(editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-paid_at", "-created_at"]

    def clean(self):
        if self.amount_net < 0:
            raise ValidationError("amount_net cannot be negative.")

    @staticmethod
    def monday_of_week(d: date) -> date:
     
        return d - timedelta(days=d.weekday())

    def compute_splits(self):
        if self.vehicle and self.vehicle.partner_pct:
            partner_pct = self.vehicle.partner_pct
            partner_amt = (self.amount_net * partner_pct) / Decimal("100.00")
            owner_amt = self.amount_net - partner_amt
            return owner_amt, partner_amt
        else:
            # No partner split
            return self.amount_net, Decimal("0.00")

    def save(self, *args, **kwargs):
        # Compute week_start from paid_at so Monday..Sunday buckets are consistent.
        self.week_start = self.monday_of_week(self.paid_at)

        # Compute split snapshot
        owner_amt, partner_amt = self.compute_splits()
        self.owner_amount = owner_amt
        self.partner_amount = partner_amt

        super().save(*args, **kwargs)

    def __str__(self):
        veh = self.vehicle.name if self.vehicle else "No Vehicle"
        return f"{self.paid_at} · {self.source} · {veh} · ${self.amount_net}"


from collections import OrderedDict
from django.db.models.functions import TruncMonth, Coalesce
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum , Value , Q , DecimalField
from .models import Deposit , Vehicle , Partner,RecurringExpense , IncomeSource
from .forms import DepositForm , PartnerForm, RecurringExpenseForm ,VehicleForm



def expense_list(request):
    expenses = RecurringExpense.objects.select_related("vehicle").order_by("vehicle__name", "name")
    weekly_owner_total = sum(float(e.owner_weekly_share()) for e in expenses)
    return render(request, "fleet/expense_list.html", {
        "expenses": expenses,
        "weekly_owner_total": weekly_owner_total,
    })

def expense_add(request):
    form = RecurringExpenseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        e = form.save()
        messages.success(request, f"Expense '{e.name}' added.")
        return redirect("expense_list")
    return render(request, "fleet/expense_add.html", {"form": form})

def _weekly_owner_expense_total():
    # Sum YOUR weekly share across all recurring expenses as Decimal
    total = Decimal("0.00")
    for e in RecurringExpense.objects.select_related("vehicle"):
        total += e.owner_weekly_share()  # already returns a Decimal
    return total

def summary_weekly(request):
    rows_raw = (
        Deposit.objects.values("week_start")
        .order_by("-week_start")
        .annotate(
            total_net=Sum("amount_net"),
            total_owner=Sum("owner_amount"),
            total_partner=Sum("partner_amount"),
        )[:26]
    )

    weekly_owner_exp_const = _weekly_owner_expense_total()  # Decimal

    rows = []
    for r in rows_raw:
        total_owner = r["total_owner"] or Decimal("0.00")
        total_net   = r["total_net"]   or Decimal("0.00")
        total_part  = r["total_partner"] or Decimal("0.00")

        owner_after = (total_owner - weekly_owner_exp_const).quantize(Decimal("0.01"))

        rows.append({
            "week_start": r["week_start"],
            "total_net": total_net,
            "total_owner": total_owner,
            "total_partner": total_part,
            "weekly_expenses": weekly_owner_exp_const,   # Decimal
            "owner_after_expenses": owner_after,         # Decimal
        })
        

    return render(request, "fleet/summary_weekly.html", {"rows": rows})


def partner_list(request):
    partners = Partner.objects.all().order_by("name")
    return render(request, "fleet/partner_list.html", {"partners": partners})

def partner_add(request):
    form = PartnerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Partner added successfully.")
        return redirect("partner_list")
    return render(request, "fleet/partner_add.html", {"form": form})    

def vehicle_list(request):
    """
    List all vehicles with key info and image.
    """
    vehicles = Vehicle.objects.select_related("partner").order_by("name")
    return render(request, "fleet/vehicle_list.html", {"vehicles": vehicles})

def vehicle_add(request):
    """
    Create a new vehicle (with image). Uses multipart/form-data for upload.
    """
    form = VehicleForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        v = form.save()
        messages.success(request, f"Vehicle '{v.name}' added.")
        return redirect("vehicle_list")
    return render(request, "fleet/vehicle_add.html", {"form": form})

from collections import OrderedDict
from decimal import Decimal
from django.db.models import Sum, Value, Q, DecimalField
from django.db.models.functions import TruncMonth, Coalesce
from django.shortcuts import render

from .models import Deposit, RecurringExpense, Vehicle, IncomeSource

def month_to_month_earnings(request):
    # optional per-vehicle filter (?vehicle=<id>)
    vehicle_id = request.GET.get("vehicle")

    # deposits: Turo only
    dep_qs = Deposit.objects.filter(source=IncomeSource.TURO)
    if vehicle_id:
        dep_qs = dep_qs.filter(vehicle_id=vehicle_id)

    # owner income by month
    income_by_month = (
        dep_qs.exclude(paid_at__isnull=True)
              .annotate(month=TruncMonth("paid_at"))
              .values("month")
              .annotate(
                  owner_income=Coalesce(
                      Sum("owner_amount"),
                      Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)),
                  )
              )
              .order_by("month")
    )

    # build month dict
    by_month = OrderedDict()
    for row in income_by_month:
        m = row["month"]
        by_month[m] = {
            "month": m,
            "owner_income": row["owner_income"] or Decimal("0"),
            "owner_expenses": Decimal("0"),
        }

    # recurring expenses relevant to scope (global + this vehicle)
    exp_qs = RecurringExpense.objects.select_related("vehicle")
    if vehicle_id:
        exp_qs = exp_qs.filter(Q(vehicle_id=vehicle_id) | Q(vehicle__isnull=True))

    def owner_monthly_share(exp):
        amt = exp.amount_monthly or Decimal("0")
        if exp.vehicle is None:
            return amt  # global: owner pays 100%
        return (amt * (exp.vehicle.owner_pct / Decimal("100"))).quantize(Decimal("0.01"))

    total_owner_expense_monthly = sum((owner_monthly_share(e) for e in exp_qs), Decimal("0"))

    for m in by_month.keys():
        by_month[m]["owner_expenses"] = total_owner_expense_monthly

    # rows + totals
    rows = []
    total_income = total_expenses = total_net = Decimal("0")
    for m, data in by_month.items():
        inc = Decimal(data["owner_income"] or 0)
        exp = Decimal(data["owner_expenses"] or 0)
        net = inc - exp
        rows.append({"month": m, "owner_income": inc, "owner_expenses": exp, "owner_net": net})
        total_income += inc
        total_expenses += exp
        total_net += net

    context = {
        "rows": rows,
        "total_owner_income": total_income,
        "total_owner_expenses": total_expenses,
        "total_owner_net": total_net,
        "vehicles": Vehicle.objects.all(),
        "selected_vehicle": int(vehicle_id) if vehicle_id else None,
    }
    return render(request, "fleet/month-to-month.html", context)


def deposit_list(request):
    
    deposits = Deposit.objects.select_related("vehicle").order_by("-paid_at", "-created_at")[:50]
    totals = deposits.aggregate(
        total_net=Sum("amount_net"),
        total_owner=Sum("owner_amount"),
        total_partner=Sum("partner_amount"),
    )
    return render(request, "fleet/deposit_list.html", {
        "deposits": deposits,
        "totals": totals,
    })


def deposit_add(request):
  
    form = DepositForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        d = form.save()  # Deposit.save() computes week_start + splits
        messages.success(request, f"Saved: {d.source} · {d.vehicle or 'No Vehicle'} · ${d.amount_net} on {d.paid_at}.")
        return redirect("deposit_list")
    return render(request, "fleet/deposit_add.html", {"form": form})



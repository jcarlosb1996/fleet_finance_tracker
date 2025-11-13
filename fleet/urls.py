from django.urls import path
from . import views

urlpatterns = [
    path("", views.deposit_list, name="deposit_list"),   # homepage: list + totals
    path("deposit/add/", views.deposit_add, name="deposit_add"),
    path("summary/weekly/", views.summary_weekly, name="summary_weekly"),
    path("vehicles/", views.vehicle_list, name="vehicle_list"),
    path("vehicles/add/", views.vehicle_add, name="vehicle_add"),  # next step
    path("partners/", views.partner_list, name="partner_list"),
    path("partners/add/", views.partner_add, name="partner_add"),
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/add/", views.expense_add, name="expense_add"),
    path("reports/month-to-month/", views.month_to_month_earnings, name="month-to-month"),
]

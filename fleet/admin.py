from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Partner, Vehicle, Deposit

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "email")

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "plate", "partner", "partner_pct")
    list_filter = ("partner",)

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ("paid_at", "source", "vehicle", "amount_net", "owner_amount", "partner_amount", "week_start")
    list_filter = ("source", "vehicle", "week_start")
    date_hierarchy = "paid_at"

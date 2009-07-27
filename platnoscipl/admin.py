from django.contrib import admin

from models import PaymentStatus


class PaymentStatusAdmin(admin.ModelAdmin):
    pass
admin.site.register(PaymentStatus, PaymentStatusAdmin)

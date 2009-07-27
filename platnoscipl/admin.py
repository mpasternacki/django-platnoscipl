from django.contrib import admin

from models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('session_id',
                    'transaction_id',
                    'is_current',
                    'timestamp',
                    'desc',
                    'status', )
    list_filter = ('is_current', )
    date_hierarchy = 'timestamp'
admin.site.register(Payment, PaymentAdmin)

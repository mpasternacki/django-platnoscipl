from django.dispatch import Signal

payment_status_notification = Signal(providing_args=('previous', ))

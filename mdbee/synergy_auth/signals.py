from django.dispatch import Signal

app_settings_signal = Signal(providing_args=['app_settings', 'request'])

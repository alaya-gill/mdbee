from django.dispatch import Signal

utils_signals = Signal(providing_args=["utils", "request"])

from django.contrib import admin
from .models import DHTData, SoilMoistureData, MotionData, PumpData

admin.site.register(DHTData)
admin.site.register(SoilMoistureData)
admin.site.register(MotionData)
admin.site.register(PumpData)

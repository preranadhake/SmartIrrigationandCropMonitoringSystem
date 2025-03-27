from rest_framework.serializers import ModelSerializer
from .models import MotionData  

class MotionDataSerializer(ModelSerializer):
    class Meta:
        model = MotionData
        fields = '__all__'  

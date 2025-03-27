from django.db import models

class DiseasePrediction(models.Model):
    image_name = models.CharField(max_length=255)
    predicted_disease = models.CharField(max_length=255)
    remedy = models.TextField()
    pesticides = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.predicted_disease} - {self.image_name}"

class PhotoData(models.Model):
    photo = models.ImageField(upload_to="photos/")
    timestamp = models.DateTimeField(auto_now_add=True)



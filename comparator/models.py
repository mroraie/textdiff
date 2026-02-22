from django.db import models

# Create your models here.
# 
# Note: This app currently doesn't require database models as it performs
# text comparison operations without storing results. If you need to:
# - Store comparison history
# - Track user comparisons
# - Save comparison results
# You can add models here. For example:
#
# class Comparison(models.Model):
#     text1 = models.TextField()
#     text2 = models.TextField()
#     mode = models.CharField(max_length=20)
#     similarity = models.FloatField()
#     created_at = models.DateTimeField(auto_now_add=True)

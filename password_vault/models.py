from django.db import models

# Create your models here.

class Vault(models.Model):
    saved_password = models.CharField(db_column='SavedPassword', unique=True, max_length=256)
    website = models.CharField(db_column='Website', unique=True, max_length=256)
    # slug = extension_fields.AutoSlugField(unique = True, populate_from = ['class_name', blank=True])
    description = models.CharField(db_column = 'Description', max_length = 8000, blank = True, null=True)
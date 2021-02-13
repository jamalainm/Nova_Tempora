from django.db import models

# Create your models here.

class CharApp(models.Model):
    app_id = models.AutoField(primary_key=True)
    sexus = models.CharField(max_length=80, verbose_name='Sexus')
    gens = models.CharField(max_length=80, verbose_name='Gens')
    praenomen = models.CharField(max_length=80,verbose_name='Praenōmen')
    date_applied = models.DateTimeField(verbose_name='Date Applied')
    account_id = models.IntegerField(default=1, verbose_name='Account ID')
    submitted = models.BooleanField(default=False)

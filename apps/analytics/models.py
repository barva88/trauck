from django.db import models


class DailyRevenueFact(models.Model):
    date = models.DateField(db_index=True)
    mrr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refunds = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_customers = models.IntegerField(default=0)
    active_subscriptions = models.IntegerField(default=0)
    arpu = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    arr = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('date',)
        ordering = ['-date']


class DailyCreditsFact(models.Model):
    date = models.DateField(db_index=True)
    credits_granted = models.IntegerField(default=0)
    credits_consumed = models.IntegerField(default=0)
    credits_balance_avg = models.IntegerField(default=0)
    by_service = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('date',)
        ordering = ['-date']


class DailyLoadsFact(models.Model):
    date = models.DateField(db_index=True)
    loads_created = models.IntegerField(default=0)
    loads_accepted = models.IntegerField(default=0)
    loads_completed = models.IntegerField(default=0)
    gross_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    acceptance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ('date',)
        ordering = ['-date']


class DailyRiskFact(models.Model):
    date = models.DateField(db_index=True)
    brokers_verified = models.IntegerField(default=0)
    high_risk_count = models.IntegerField(default=0)
    medium_risk_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('date',)
        ordering = ['-date']

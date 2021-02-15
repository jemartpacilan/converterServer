from django.db import models


class Job(models.Model):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    READY = "READY"

    STATE_CHOICES = [
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
        (READY, "Ready"),
    ]

    component_id = models.IntegerField(blank=False)
    access_url = models.CharField(max_length=400)
    updated_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default=READY,
    )

    @classmethod
    def update_state(self, pk, state, updated_date):
        return self.objects.filter(pk=pk).update(state=state, updated_date=updated_date)

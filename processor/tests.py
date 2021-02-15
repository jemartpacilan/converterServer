from django.utils import timezone
from django.test import TestCase
from .models import Job
from django.test import Client


class JobTestCase(TestCase):
    def setUp(self):
        self.job = Job.objects.create(
            component_id=1, access_url="test_resources/LMNOP_A.zip"
        )

    def test_job_default_state(self):
        """
        Check if the default value of the job's state upon creation is READY
        """
        self.assertEqual(self.job.state, "READY")
        self.assertNotEqual(self.job.state, "COMPLETED")

    def test_update_job_state(self):
        """
        Check if job's state is correctly updated
        """
        time_now = timezone.now()
        Job.update_state(self.job.id, "FAILED", time_now)
        job = Job.objects.get(component_id=1)
        self.assertEqual(job.state, "FAILED")
        self.assertEqual(job.updated_date, time_now)


class JobViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_job_successful_creation(self):
        """
        Check if job if created successfully upon post action
        """
        response = self.client.post(
            "/job-queue/", {"component_id": 1, "access_url": "test/test.zip"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "Job Successfully created")

    def test_get_job(self):
        """
        Check if job if retrieved successfully upon post action
        """
        self.client.post(
            "/job-queue/", {"component_id": 1, "access_url": "test/test.zip"}
        )
        response = self.client.get("/job-queue/")
        self.assertEqual(response.status_code, 200)

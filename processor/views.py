from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import Job
from .utils import process_in_allegro, terminate_process
import base64, os, json, logging, sys

logger = logging.getLogger("django.error")
logger_info = logging.getLogger("django.info")


@method_decorator(csrf_exempt, name="dispatch")
class JobView(View):
    def post(self, request):
        # Endpoint to create a job to process in the queue
        component_id = request.POST.get("component_id")
        access_url = request.POST.get("access_url")

        message = "Job Successfully created"
        try:
            Job.objects.create(component_id=component_id, access_url=access_url)
        except Exception as e:
            message = "Job Creation error : {}".format(e)
            logger.exception(message)

        return HttpResponse(message, content_type="application/json")

    def get(self, request):
        # Endpoint to get the job to process with specified state (default is "READY")
        limit = request.POST.get("limit", 10)
        state = request.POST.get("state", "READY")

        data_items = list(
            Job.objects.filter(state=state).values("id", "component_id", "access_url")[
                :limit
            ]
        )
        data = {"count": len(data_items), "data_items": data_items}
        return HttpResponse(json.dumps(data), content_type="application/json")


@method_decorator(csrf_exempt, name="dispatch")
class JobProcessorView(View):
    def post(self, request):
        # Endpoint to process the job for extraction of files and conversion to .olb
        msg = "Something went wrong"
        status = "PROCESSING"

        queue_id = request.POST.get("id")

        Job.update_state(queue_id, status, timezone.now())

        response = self.process_test_request(request)

        content = response.content
        if "Please provide a link" in content or "Error Encountered" in content:
            msg = content
            Job.update_state(queue_id, "FAILED", timezone.now())
        else:
            msg = "Succesfully converted!"
            status = "COMPLETED"
            Job.update_state(queue_id, "COMPLETED", timezone.now())
        obj = {"status": status, "message": msg}
        return HttpResponse(obj, content_type="application/json")

    def process_test_request(self, request):
        # This method is only used for processing files locally (test env)
        # For testing only. Utilize process_production_request() for accessing download request
        return_file = process_in_allegro(
            r"{}".format(
                os.path.join(os.path.abspath(sys.path[0]), request.POST["access_url"])
            )
        )
        return HttpResponse("processed", content_type="application/json")

    def process_production_request(self, request):
        # This method is a reference to the the index function in views.py file of azureserver repo
        # Use this method for production and when accessing production download request
        try:
            if request.method == "POST":
                s3_url = request.POST["s3_link"]
                part_id = request.POST["part_id"]
                urllib_request = urllib2.Request(s3_url)
                page = urllib2.urlopen(urllib_request)
                file_name = request.POST["s3_link"].split("?")
                file_name = file_name[0]
                new_zip_name = get_file_name(file_name)

                with open(new_zip_name, "wb") as f:
                    f.write(page.read())

                return_file = process_in_allegro(new_zip_name, True)

                return_file_encoded = base64.b64encode(return_file)
                try:
                    os.remove(new_zip_name)
                except WindowsError as e:
                    remove = terminate_process(new_zip_name, e.message)
                    if remove:
                        os.remove(new_zip_name)
                try:
                    os.remove(new_zip_name[:-4] + "_processed.zip")
                except WindowsError as e:
                    remove = terminate_process(
                        new_zip_name[:-4] + "_processed.zip", e.message
                    )
                    if remove:
                        os.remove(new_zip_name[:-4] + "_processed.zip")

                # Send the processed file to SnapEDA via POST
                snap_url = "https://www.snapeda.com/api/save_processed_part_allegro/"
                # snap_url = "http://3.238.120.27:8080/api/save_processed_part_allegro/"

                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                data = urllib.urlencode(
                    {
                        "part_id": part_id,
                        "s3_link": s3_url,
                        "return_file_encoded": return_file_encoded,
                    }
                )
                urllib_request = urllib2.Request(
                    snap_url, data, headers={"User-Agent": "Magic Browser"}
                )
                page = urllib2.urlopen(urllib_request, context=ctx)
                response = page.read()
                return HttpResponse(response)

            return HttpResponse("Please provide an S3 link")
        except:
            logger.exception(
                "\r\n########## PARTID: {} ########## \n"
                "Fatal error in main loop".format(part_id)
            )
            return HttpResponse("Error Encountered")

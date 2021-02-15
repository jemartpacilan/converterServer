from .batch_extractor import BatchExtractor
import logging, re, subprocess

logger = logging.getLogger("django.error")

def process_in_allegro(zip_location):
    """
    Method for extracting and conversion of files using allegro software
    """
    my_extractor = BatchExtractor(zip_location)
    extraction_successful = my_extractor.extract_files()

    if extraction_successful:
        return my_extractor.process_files()

def get_file_name(full_url):
    pattern = re.compile("/")
    matches = re.finditer(pattern, full_url)
    for match in matches:
        index = match.end()
    return full_url[index:]

def terminate_process(path, e):
    # Used to termincate a process
    logger.info("Trying to terminate a process due to: %s", e)
    remove = True
    p = None
    try:
        p = subprocess.Popen(path)
    except WindowsError:
        remove = False
        logger.error("this process was not found and we tried to Popen it: %s", path)
    if p is not None:
        try:
            p.terminate()
        except WindowsError as e:
            remove = False
            logger.error(
                "this process was found but triggered an error trying to terminate it: %s --- %s",
                path,
                e,
            )
    return remove
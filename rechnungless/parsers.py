import os
import json
import base64

import httpx
from pathlib import Path
from datetime import datetime

from documents.parsers import DocumentParser
from documents.parsers import ParseError
from documents.parsers import make_thumbnail_from_pdf
from django.utils.timezone import is_naive
from django.utils.timezone import make_aware



class RechnunglessParser(DocumentParser):

    def parse(self, document_path, mime_type, file_name=None):

        #The target PDF document
        archive_file = os.path.join(self.tempdir, "archived.pdf")

        #Read XML
        content = self.read_file_handle_unicode_errors(document_path)

        #Make the request to RechunglessConverter
        url=os.getenv("RECHNUNGLESS_ENDPOINT", "http://rechnungless:8080") + "/" + os.getenv("RECHNUNGLESS_RESSOURCE", "rechnungless") + "/convert"
        header = {"Content-Type": "application/xml"}
        r = httpx.post(url, headers=header, data=content, timeout=os.getenv("RECHNUNGLESS_TIMEOUT", 60.0))

        #HTTP 500 / Server Error -> Something went REALLY wrong
        if r.status_code == httpx.codes.INTERNAL_SERVER_ERROR:
            raise ParseError("Server Error: " + str(r.content))

        #Other Error (apart from HTTP 422)
        if r.status_code not in (httpx.codes.OK, httpx.codes.UNPROCESSABLE_ENTITY) :
            raise ParseError("Unknown Error: HTTP " + str(r.status_code) + " " + str(r.content))

        #Only HTTP 200 and HTTP 422 left -> ok to parse json
        response = json.loads(r.content)

        #SHOULD NOT BE THE CASE HERE, just checking for sanity (should only occur on HTTP 500)
        if response["result"] == "failed":
            message = "Conversion failed: \n"
            for msg in response["messages"]:
                message += msg
            raise ParseError(message)

        if r.status_code == httpx.codes.UNPROCESSABLE_ENTITY:
            message = "The XML file is not valid:"
            for msg in response["messages"]:
                message += "\n" + msg
            raise ParseError(message)

        #HTTP 200 -> we should have gotten back a pdf as part of the response
        #Print to the Console if we just accepted a technically invalid file
        if response["result"] == "invalid":
            print("THE FILE THAT WAS JUST PROCESSED WAS TECHNICALLY INVALID!")
        #Write the file to disk
        with open(archive_file, 'wb') as afile:
            afile.write(base64.b64decode(response["archive_pdf"]))

        #Just use the plain XML text as the content
        self.text = content

        #Set the archive_path variable for paperless to be able to find our file
        self.archive_path = archive_file

        #Check if RechnunglessConverter could find an issue date in the XML and set it
        if "issue_date" in response and type(response["issue_date"]) == str:
            self.date = datetime.strptime(response["issue_date"], "%Y%m%d")
            if is_naive(self.date):
                self.date = make_aware(self.date)



    def extract_metadata(self, document_path, mime_type):
        #TODO
        return []

    def get_thumbnail(self, document_path: Path, mime_type, file_name=None) -> Path:
        #Simply create the preview image from the just created PDF
        return make_thumbnail_from_pdf(self.archive_path, self.tempdir)

    def get_settings(self):
        #No Settings available
        return None

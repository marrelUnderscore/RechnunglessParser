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

VERSION = "0.1.0"
VERSION_SPLIT = VERSION.split(".")

RECHNUNGLESS_ENDPOINT = os.getenv("RECHNUNGLESS_ENDPOINT", "http://rechnungless:8080")
RECHNUNGLESS_RESSOURCE = os.getenv("RECHNUNGLESS_ENDPOINT", "rechnungless")

RECHNUNGLESS_TIMEOUT = int(os.getenv("RECHNUNGLESS_ENDPOINT", 60))
RECHNUNGLESS_BASEURL = RECHNUNGLESS_ENDPOINT + "/" + RECHNUNGLESS_RESSOURCE
RECHNUNGLESS_SKIPVERSIONCHECK = os.getenv("RECHUNGLESS_SKIPVERSIONCHECK", "False").casefold() == "True".casefold()
RECHNUNGLESS_PARSEINVALIDXMLS = os.getenv("RECHUNGLESS_PARSEINVALIDXMLS", "False").casefold() == "True".casefold()

class RechnunglessParser(DocumentParser):

    def parse(self, document_path, mime_type, file_name=None):
        #Check if RechnunglessConverter is running a compatible version to this RechnunglessParser (i.e. major and minor version are the same)
        if not RECHNUNGLESS_SKIPVERSIONCHECK:
            self._do_version_check()

        #Create a path for the target PDF file
        archive_file = os.path.join(self.tempdir, "archived.pdf")

        #Read XML file
        content = self.read_file_handle_unicode_errors(document_path)

        #Make the request to RechnunglessConverter
        url=RECHNUNGLESS_BASEURL + "/convert"
        if RECHNUNGLESS_PARSEINVALIDXMLS:
            url += "?parseinvalidxmls=true"
        header = {"Content-Type": "application/xml"}
        r = httpx.post(url, headers=header, data=content, timeout=RECHNUNGLESS_TIMEOUT)

        #Check if response was technically ok and get back the corresponding json object if it was
        response = self._decode_check_response(r)

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
        #Check if RechnunglessConverter is running a compatible version to this RechnunglessParser (i.e. major and minor version are the same)
        if not RECHNUNGLESS_SKIPVERSIONCHECK:
            self._do_version_check()

        # Read XML
        content = self.read_file_handle_unicode_errors(document_path)

        # Make the request to RechunglessConverter
        url = RECHNUNGLESS_BASEURL + "/metadata"
        if RECHNUNGLESS_PARSEINVALIDXMLS:
            url += "?parseinvalidxmls=true"
        header = {"Content-Type": "application/xml"}
        r = httpx.post(url, headers=header, data=content, timeout=RECHNUNGLESS_TIMEOUT)

        # Check if response was technically ok and get back the corresponding json object if it was
        response = self._decode_check_response(r)

        return response["metadata"]

    def get_thumbnail(self, document_path: Path, mime_type, file_name=None) -> Path:
        #Simply create the preview image from the just created PDF
        return make_thumbnail_from_pdf(self.archive_path, self.tempdir)

    def get_settings(self):
        #No Settings available
        return None



    def _decode_check_response(self, httpresponse):
        # HTTP 500 / Server Error -> Something went REALLY wrong #TODO Invalid File?
        if httpresponse.status_code == httpx.codes.INTERNAL_SERVER_ERROR:
            raise ParseError(f"Server Error: {httpresponse.content}")

        # Other Error (apart from HTTP 422)
        if httpresponse.status_code not in (httpx.codes.OK, httpx.codes.UNPROCESSABLE_ENTITY):
            raise ParseError(f"Unknown Error (HTTP {httpresponse.status_code}): {httpresponse.content}")

        #Only Unprocessable Entity & OK left -> parse the response
        response = json.loads(httpresponse.content)

        # SHOULD NOT BE THE CASE HERE, just checking for sanity (should only occur on HTTP 500, which is already checked for above)
        if response["result"] == "failed":
            message = "Parsing failed: \n"
            for msg in response["messages"]:
                message += msg
            raise ParseError(message)

        if response["result"] == "invalid" and not RECHNUNGLESS_PARSEINVALIDXMLS:
            message = "The XML file is not valid:"
            for msg in response["messages"]:
                message += "\n" + msg
            raise ParseError(message)

        # Print to the Console if we just accepted a technically invalid file
        if response["result"] == "invalid":
            print("THE FILE THAT WAS JUST PROCESSED WAS TECHNICALLY INVALID! This was ignored however, because the RECHNUNGLESS_PARSEINVALIDXMLS parameter is set.")

        #We either have a valid invoice, or it was invalid, but the PARSEINVALIDXMLS-Parameter was set.
        #In both cases we can return the json object for further processing.
        return response

    def _do_version_check(self):
        url = RECHNUNGLESS_BASEURL + "/version"
        r = httpx.get(url, timeout=RECHNUNGLESS_TIMEOUT)
        if r.status_code != httpx.codes.OK:
            raise ParseError(f"Server Error during version check (HTTP {r.status_code}): {str(r.content)}")
        response = json.loads(r.content)
        if VERSION_SPLIT[0] != response["major"] or VERSION_SPLIT[1] != response["minor"]:
            raise ParseError(f"RechnunglessParser and RechnunglessConverter are on incompatible versions ({VERSION} vs {response['major']}.{response['minor']}.{response['patch']})")
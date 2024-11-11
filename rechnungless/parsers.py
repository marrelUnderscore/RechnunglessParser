import base64

import httpx

from documents.parsers import DocumentParser
from documents.parsers import ParseError
import os
from pathlib import Path
import json



class RechnunglessParser(DocumentParser):

    def parse(self, document_path, mime_type, file_name=None):
        # This method does not return anything. Rather, you should assign
        # whatever you got from the document to the following fields:

        # The content of the document.
        archive_file = os.path.join(self.tempdir, "archived.pdf")


        with open(document_path, 'r') as content_file:
            content = content_file.read()

        url=os.getenv("RECHNUNGLESS_ENDPOINT", "http://rechnungless:8080") + "/rechnungless/convert/pdf2"
        header = {"Content-Type": "application/xml"}
        r = httpx.post(url, headers=header, data=content, timeout=60.0)
        if r.status_code != httpx.codes.OK:
            raise ParseError("Error while converting: HTTP" + r.status_code + " " + r.content)
        response = json.loads(r.content)

        if response["result"] == "failed":
            message = "Failed to convert the invoice: \n"
            for msg in response["messages"]:
                message += msg
            raise ParseError(message)

        if response["result"] == "invalid" and os.getenv("RECHNUNGLESS_IGNORE_INVALID", "False").lower() != "true":
            message = "The invoice was determined to be invalid: \n"
            for msg in response["messages"]:
                message += msg
            raise ParseError(message)


        with open(archive_file, 'wb') as afile:
            afile.write(base64.b64decode(response["archive_pdf"]))

        self.text = content

        # Optional: path to a PDF document that you created from the original.
        self.archive_path = archive_file

        # Optional: "created" date of the document.
        #self.date = get_created_from_metadata(document_path)

    def get_thumbnail(self, document_path: Path, mime_type, file_name=None) -> Path:

        # This should return the path to a thumbnail you created for this
        # document.

        thumb_file = os.path.join(self.tempdir, "archived.jpg")

        with open(document_path, 'r') as content_file:
            content = content_file.read()

        url = "http://rechnungless:8080/rechnungless/convert/thumbnail"
        header = {"Content-Type": "application/xml"}
        r = httpx.post(url, headers=header, data=content,timeout=60.0)
        with open(thumb_file, 'wb') as afile:
            afile.write(r.content)



        return thumb_file


    def get_settings(self):
        """
        This parser does not implement additional settings yet
        """
        return None
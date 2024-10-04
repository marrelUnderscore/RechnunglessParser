import httpx

from documents.parsers import DocumentParser
import os
from pathlib import Path



class RechnunglessParser(DocumentParser):

    def parse(self, document_path, mime_type, file_name=None):
        # This method does not return anything. Rather, you should assign
        # whatever you got from the document to the following fields:

        # The content of the document.
        archive_file = os.path.join(self.tempdir, "archived.pdf")


        with open(document_path, 'r') as content_file:
            content = content_file.read()

        url="http://rechnungless:8080/rechnungless/convert/pdf"
        header = {"Content-Type": "application/xml"}
        r = httpx.post(url, headers=header, data=content, timeout=60.0)
        with open(archive_file, 'wb') as afile:
            afile.write(r.content)

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
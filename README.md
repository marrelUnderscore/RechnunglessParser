# RechnunglessParser
A custom parser for paperless to visualize XML type eInvoices (mainly xRechnung) as PDFs.  
Please note that this is not a professional software product. You are using this at your own risk.  
This uses a custom java web service called [RechnunglessConverter](https://github.com/marrelUnderscore/RechnunglessConverter) based on the library created by https://www.mustangproject.org/ to visualize the eInvoice as a PDF.
## Current Features
 - [x] Process XML files as electronic bills and visualize them as PDFs
 - [x] Reject XML files that do not pass validation (malformed eInvoice, not xRechnung/Factura-X format, ...)
 - [x] Recognize the issue date from the XML and use it in paperless
 - [x] Extract additional metadata from the XML and save that to paperless as metadata
 - [ ] eInvoices can have a bunch of attachments of various formats - maybe append these to the end of the pdf - currently they are simply ignored
## Usage
This project is intended to be used with a docker based installation of paperless-ngx. In order to add this to your paperless installation you need to add the following to your docker-compose file:
```yaml
services:
  [...]
  webserver: # This is your main paperless-ngx container
    [...]
    depends_on:
      [...]
      - rechnungless
    volumes:
      [...]
        # Replace the part before the colon with the path to the rechnungless folder found in this repo
      - /path/to/your/rechnungless:/usr/src/paperless/src/rechnungless
    environment:
      [...]
      PAPERLESS_APPS: rechnungless.apps.RechnunglessConfig
#     ...optional config for the RechnunglessParser - see below...
  [...]
  rechnungless:
    image: ghcr.io/marrelunderscore/rechnunglessconverter:latest
    restart: unless-stopped
```
After that, restart your paperless stack. If everything went right, paperless should now accept XML files and process them.
## Versioning
Since this project consists of two parts, you have to make sure that the versions of RechnunglessParser and RechnunglessConverter that you are using are compatible with each other.
This is the case if both the major and minor version number is identical (version numbers use the schema [major].[minor].[patch]),
so for example versions 0.2.3 and 0.2.11 would be compatible, while versions 1.2.3 and 1.3.3 would not.
The parser checks for this and returns an error if the versions are incompatible. (This can be turned off for testing purposes, see the configuration section below).
## Configuration
There are different configuration options for RechnunglessParser. Some (like RECHNUNGLESS_PARSEINVALIDXMLS) have effects on RechnunglessConverter.  
Place these in the "environment"-section of your main paperless container ("webserver" in the example above)

| ENV-Variable                  | Description                                                                                                                                                                                                                                          | Default                  |
|-------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|
| RECHNUNGLESS_ENDPOINT         | The domain and port of your RechnunglessConverter service                                                                                                                                                                                            | http://rechnungless:8080 |
| RECHNUNGLESS_RESSOURCE        | The name under which your tomcat artifact can be reached                                                                                                                                                                                             | rechnungless             |
| RECHNUNGLESS_TIMEOUT          | The maximum time the parser should wait for an answer from the converter                                                                                                                                                                             | 60                       |
| RECHNUNGLESS_PARSEINVALIDXMLS | Determines if the program should try to generate a PDF, even if the XML was determined to be invalid (not recommended, since this will try to parse *every* XML you ingest as an invoice, even if it isn't one!)                                     | false                    |
| RECHNUNGLESS_SKIPVERSIONCHECK | This parameter disables the version check that is done everytime before parsing an XML file to make sure your RechnunglessConverter is on a compatible version (not recommended, since incompatible versions might lead to incorrect results/errors) | false                    |

Hint: The URLs that are used by RechnunglessParser are generated in the following way: `$(RECHNUNGLESS_ENDPOINT)/$(RECHNUNGLESS_RESSOURCE)/<function that does the magic>`



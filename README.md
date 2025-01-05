# RechnunglessParser
A custom parser for paperless to visualize XML type eInvoices (Factura-X and xRechnung) as PDFs.  
**! Still Work-In-Progress. USE AT YOUR OWN RISK !**  
This uses a [custom java web service](https://github.com/marrelUnderscore/RechnunglessConverter) based on the library created by https://www.mustangproject.org/ to visualize the eInvoice as a pdf.
## Current Features
 - [x] Process XML files as electronic bills and visualize them as PDFs
 - [x] Reject XML files that do not pass validation (malformed eInvoice, not xRechnung/Factura-X format, ...)
 - [x] Recognize the issue date from the XML and use it in paperless
 - [ ] Extract additional metadata from the XML and save that to paperless as metadata
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
#     ...optional config for the RechnunglessParser...
  [...]
  rechnungless:
    image: ghcr.io/marrelunderscore/rechnunglessconverter:latest
    restart: unless-stopped
#   environment:
#     ...optional config for the RechnunglessConverter...
```
After that, restart your paperless stack. If everything went right, paperless should now accept xml files and process them.
## Versioning
Since this project consists of two parts, you have to make sure that the versions of RechnunglessParser and RechnunglessConverter that you are using are compatible with each other.
This is the case if both the major and minor version number is identical (version numbers use the schema [major].[minor].[patch]),
so for example versions 0.2.3 and 0.2.11 would be compatible, while versions 1.2.3 and 1.3.3 would not.
The parser checks for this and returns an error if the versions are determined to not be compatible.
## Configuration
There are different configuration options for both the RechnunglessParser and the RechnunglessConverter
### RechnunglessParser
Place these in the "environment"-section of your main paperless container ("webserver" in the example above)

| ENV-Variable            | Description                                                              | Default                  |
|-------------------------|--------------------------------------------------------------------------|--------------------------|
| RECHNUNGLESS_ENDPOINT   | The domain and port of your RechnunglessConverter service                | http://rechnungless:8080 |
| RECHNUNGLESS_RESSOURCE  | The name under which your tomcat artifact can be reached                 | rechnungless             |
| RECHNUNGLESS_TIMEOUT    | The maximum time the parser should wait for an answer from the converter | 60.0                     |
Hint: The URLs that are used by RechnunglessParser are generated in the following way: \$(RECHNUNGLESS_ENDPOINT)/$(RECHNUNGLESS_RESSOURCE)/\<function that does the magic>

### RechnunglessConverter
Place these in the "environment"-section of your rechnungless container

| ENV-Variable                  | Description                                                                                                                                                                                                     | Default |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| RECHNUNGLESS_PARSEINVALIDXMLS | Determines if the converter should try to generate a PDF, even if the XML was determined to be invalid (not recommended, since this will try to visualize *every* XML you ingest, even if it isn't an invoice!) | false   |

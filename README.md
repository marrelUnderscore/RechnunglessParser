# RechnunglessParser
A custom parser for paperless to visualize XML type eInvoices (Factura-X and xRechung) as PDFs.  
**! Still Work-In-Progress. USE AT YOUR OWN RISK !**  
This uses a custom java web service based on the library created by https://www.mustangproject.org/ to visualize the eInvoice as a pdf.
## Current Features
 - [x] Process XML files as electronic bills and visualize them as PDFs
 - [x] Reject XML files that do not pass validation (malformed eInvoice, not xRechung/Factura-X format, ...)
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
## Configuration
There are different configuration options for both the RechnunglessParser and the RechnunglessConverter
### RechnunglessParser
Place these in the "environment"-section of your main paperless container ("webserver" in the example above)

| ENV-Variable            | Description                                                              | Default                 |
|-------------------------|--------------------------------------------------------------------------|-------------------------|
| RECHNUNGLESS_ENDPOINT   | The domain and port of your PaperlessConverter service                   | http://rechungless:8080 |
| RECHNUNGLESS_RESSOURCE  | The name under which your tomcat artifact can be reached                 | rechnungless            |
| RECHNUNGLESS_TIMEOUT    | The maximum time the parser should wait for an answer from the converter | 60.0                    |

### RechnunglessConverter
Place these in the "environment"-section of your rechnungless container

| ENV-Variable                 | Description                                                                                             | Default |
|------------------------------|---------------------------------------------------------------------------------------------------------|---------|
| RECHUNGLESS_PARSEINVALIDXMLS | Determines if the converter should try to generate a PDF, even if the XML was determined to be invalid | false   |

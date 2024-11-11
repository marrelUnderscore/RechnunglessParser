# RechnunglessParser
A custom parser for paperless to visualize xml type eInvoices (Factura-X and xRechung) as PDFs.  
**! Currently a proof of concept, still missing a lot of validation/error handeling - but that's already in the works. USE AT YOUR OWN RISK !**  
This uses a custom java web service based on the libraray created by https://www.mustangproject.org/ to visualize the eInvoice as a pdf.
## Usage
This project is intended to be used with a docker based installation of paperless-ngx. In order to add this to your paperless installtion you need to add the following to your docker-compose file:
```yaml
services:
  [...]
  webserver:
    [...]
    depends_on:
      [...]
      - rechnungless
    volumes:
      [...]
        # Replace with the path to the rechnungless folder found in this repo
      - /path/to/your/rechnungless:/usr/src/paperless/src/rechnungless
    environment:
      [...]
      PAPERLESS_APPS: rechnungless.apps.RechnunglessConfig
  [...]
  rechnungless:
    image: ghcr.io/marrelunderscore/rechnunglessconverter:latest
    restart: unless-stopped
```
After that, restart your paperless stack. If everything went right, paperless should now accept xml files and process them.

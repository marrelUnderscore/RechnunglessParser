from django.apps import AppConfig

from rechnungless.signals import rechnungless_consumer_declaration


class RechnunglessConfig(AppConfig):
    name = "rechnungless"

    def ready(self):
        from documents.signals import document_consumer_declaration

        document_consumer_declaration.connect(rechnungless_consumer_declaration)

        AppConfig.ready(self)
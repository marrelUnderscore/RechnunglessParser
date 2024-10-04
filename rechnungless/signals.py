def get_parser(*args, **kwargs):
    from rechnungless.parsers import RechnunglessParser

    return RechnunglessParser(*args, **kwargs)


def rechnungless_consumer_declaration(sender, **kwargs):
    return {
        "parser": get_parser,
        "weight": 10,
        "mime_types": {
            "application/xml": ".xml",
            "text/xml": ".xml",
        },
    }
import logging
import logging.config

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "entropic": {
                "handlers": ["null"],
                "propagate": False,
            },
        },
        "handlers": {
            "null": {"class": "logging.NullHandler"},
        },
    }
)

logger = logging.getLogger("entropic")

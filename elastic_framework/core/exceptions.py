import logging

from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class APIError(APIException):
    def __init__(self, message, status_code, show=False, code='',
                 *args, **kwargs):
        super(APIError, self).__init__(message, *args, **kwargs)
        self.status_code = status_code
        self.detail = message
        self.show = show
        self.code = code
        # XXX I think this will fill up the logs wit useless messages
        logger.warning(u'API error {}'.format(message))

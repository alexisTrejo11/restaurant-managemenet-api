class DataError(Exception):
    """Custom exception for errors in the Result class."""
    pass

class Result:
    def __init__(self, data=None, error_message=None):
        self.data = data
        self.error_message = error_message

    def is_success(self):
        return self.error_message is None

    def is_failure(self):
        return self.error_message is not None

    def get_data(self):
        if self.is_success():
            return self.data
        raise DataError("Can't retrieve data from a failed result")
    
    def get_error_msg(self):
        if self.is_failure():
            return self.error_message
        raise DataError("Can't retrieve data from a successful result")

    @staticmethod
    def error(error_message):
        return Result(data=None, error_message=error_message) 

    @staticmethod
    def success(data=None):
        return Result(data=data, error_message=None)
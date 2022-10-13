from fastapi.responses import ORJSONResponse


class ErrorResponse:
    error_message = None
    error_code = None
    correct_params = None

    def return_json(self):
        json = {
            "Status": "Failure",
            "error": {
                "code": self.error_code,
                "message": self.error_message,
                "correction": self.correct_params
            }
        }

        return ORJSONResponse(json)

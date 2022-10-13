from fastapi.responses import ORJSONResponse


class PrecipitationResponse:
    std_dev = None
    precipitation_value=None
    success_code = None

    def return_json(self):
        json = {
            "Status": "Success",
            "body": {
                "code": self.success_code,
                "predicted_precipitation(0.1 mm)": self.precipitation_value,
                "standard_deviation": self.std_dev
            }
        }

        return ORJSONResponse(json)

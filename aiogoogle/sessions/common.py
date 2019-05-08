def _call_callback(request, response):
    if request.callback is not None:
        if (
            response.status_code is not None
            and response.status_code >= 200
            and response.status_code < 300
        ):
            if response.json is not None:
                response.json = request.callback(response.content)
            elif response.data is not None:
                response.data = request.callback(response.content)
    return response

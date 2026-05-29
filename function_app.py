import azure.functions as func
import json

app = func.FunctionApp(
    http_auth_level=func.AuthLevel.ANONYMOUS
)

# Route: POST /api/hello
@app.route(route="hello", methods=["POST"])
def hello(req: func.HttpRequest) -> func.HttpResponse:

    body = req.get_json()

    name = body.get("name", "World")

    return func.HttpResponse(
        json.dumps(
            {
                "message": f"Hello, {name}! from Azure ⚡"
            }
        ),
        mimetype="application/json"
    )
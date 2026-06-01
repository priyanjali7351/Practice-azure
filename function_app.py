import azure.functions as func
import json
import logging
import os
from datetime import datetime, timezone
import uuid
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
tasks = {}



timer_status = {

    "daily_report": None,

    "cleanup": None,

    "health_ping": None

}

# ── Task 2: Health Check ─────────────────────────────────
# GET /api/health  →  { "status": "running" }
@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    
    
    logging.info("Health check called")
    return func.HttpResponse(
        json.dumps({
            "status": "running",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }),
        mimetype="application/json"
    )


# ── Task 3: Calculator ───────────────────────────────────
# GET /api/calculate?x=10&y=20  →  { "sum": 30 }
@app.route(route="calculate", methods=["GET"])
def calculate(req: func.HttpRequest) -> func.HttpResponse:
    try:
        x = float(req.params.get("x", 0))
        y = float(req.params.get("y", 0))
    except ValueError as e:
        
        logging.exception("Invalid parameters passed to /calculate")
        return func.HttpResponse(
            json.dumps({"error": "x and y must be numbers", "detail": str(e)}),
            status_code=400,
            mimetype="application/json"
        )
    result = x + y
    logging.info(f"calculate: x={x}, y={y}, sum={result}")
    return func.HttpResponse(
        json.dumps({"x": x, "y": y, "sum": result}),
        mimetype="application/json"
    )


# ── HTTP Trigger (Hello) ─────────────────────────────────
# POST /api/hello  →  { "message": "Hello, <name>!" }
@app.route(route="hello", methods=["POST"])
def hello(req: func.HttpRequest) -> func.HttpResponse:
   
    try:
        body = req.get_json()
    except ValueError as e:
        
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": "Invalid JSON body",
                "detail": str(e)
            }),
            status_code=400,
            mimetype="application/json"
        )

    name = body.get("name", "World")

    response = {
        "success": True,
        "message": f"Hello, {name}! from Azure ⚡",
        "received_input": body,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "function": "hello",
        "status": "working"
    }

    return func.HttpResponse(
        json.dumps(response),
        mimetype="application/json"
    )


# ── Task 4: Key Vault Secret Fetch ───────────────────────
# POST /api/secret  body: { "name": "my-secret-name" }
# Uses Managed Identity — no credentials in code
@app.route(
    route="secret",
    methods=["POST"]
)
def get_secret(
    req: func.HttpRequest
):

    try:

        body = req.get_json()

        name = body.get(
            "name"
        )

        credential = \
        DefaultAzureCredential()

        client = SecretClient(

            vault_url=
            os.environ[
            "KEY_VAULT_URL"
            ],

            credential=
            credential

        )

        secret = client\
        .get_secret(
            name
        )

        masked = \
        secret.value[:3] \
        + "*****"

        return func.HttpResponse(

            json.dumps({

                "name":name,

                "masked":
                masked

            }),

            mimetype=
            "application/json"

        )

    except Exception as e:
        
        return func.HttpResponse(

            json.dumps({

                "error":
                str(e)

            }),

            status_code=500,

            mimetype=
            "application/json"

        )

    except Exception as e:
        logging.exception("Key Vault fetch failed")
        return func.HttpResponse(
            json.dumps({"error": type(e).__name__, "detail": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(
    route="tasks",
    methods=["GET", "POST"]
)
def tasks_handler(req: func.HttpRequest) -> func.HttpResponse:

    # GET ALL TASKS
    if req.method == "GET":

        return func.HttpResponse(
            json.dumps(list(tasks.values())),
            mimetype="application/json"
        )

    # CREATE TASK
    try:

        body = req.get_json()

        task_id = str(uuid.uuid4())

        task = {
            "id": task_id,
            "title": body.get("title"),
            "priority": body.get("priority", "Medium")
        }

        tasks[task_id] = task

        return func.HttpResponse(
            json.dumps(task),
            status_code=201,
            mimetype="application/json"
        )

    except Exception as e:

        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": "Invalid request body",
                "detail": str(e)
            }),
            status_code=400,
            mimetype="application/json"
        )
    

@app.route(
    route="tasks/{id}",
    methods=["DELETE"]
)
def delete_task(req: func.HttpRequest) -> func.HttpResponse:

    task_id = req.route_params.get("id")

    if task_id not in tasks:

        return func.HttpResponse(
            json.dumps({
                "error":"Task not found"
            }),
            status_code=404,
            mimetype="application/json"
        )

    deleted = tasks.pop(task_id)

    return func.HttpResponse(
        json.dumps({
            "deleted": deleted
        }),
        mimetype="application/json"
    )

@app.route(
    route="upload",
    methods=["POST"]
)
def upload_file(
    req: func.HttpRequest
):

    try:

        conn = os.environ[
            "STORAGE_CONN"
        ]

        client = BlobServiceClient\
            .from_connection_string(
                conn
            )

        filename = req.headers.get(
            "x-file-name",
            "file"
        )

        container = client\
            .get_container_client(
                "uploads"
            )

        container.upload_blob(

            name=filename,

            data=req.get_body(),

            overwrite=True

        )

        return func.HttpResponse(

            json.dumps({

                "success":True,

                "file":filename

            }),

            mimetype="application/json"

        )

    except Exception as e:

        return func.HttpResponse(

            json.dumps({

                "error":str(e)

            }),

            status_code=500,

            mimetype="application/json"

        )
    
@app.timer_trigger(

    schedule="0 0 8 * * *",

    arg_name="timer",

    run_on_startup=True

)

def daily_report(timer):

    global timer_status

    logging.info(
        "Daily report triggered"
    )

    timer_status[
        "daily_report"
    ] = datetime.now(
        timezone.utc
    ).isoformat()


@app.timer_trigger(

    schedule="0 0 */6 * * *",

    arg_name="timer",

    run_on_startup=True

)

def cleanup_data(timer):

    global timer_status

    logging.info(
        "Cleanup triggered"
    )

    timer_status[
        "cleanup"
    ] = datetime.now(
        timezone.utc
    ).isoformat()

@app.timer_trigger(

    schedule="0 */5 * * * *",

    arg_name="timer",

    run_on_startup=True

)

def health_ping(timer):

    global timer_status

    logging.info(
        "Health ping triggered"
    )

    timer_status[
        "health_ping"
    ] = datetime.now(
        timezone.utc
        ).isoformat()
    
@app.route(

    route="timer-status/{name}",

    methods=["GET"]

)

def get_timer_status(req):

    name = req.route_params.get(
        "name"
    )

    return func.HttpResponse(

        json.dumps({

            "timer": name,

            "last_run":
            timer_status.get(name)

        }),

        mimetype="application/json"

    )


@app.route(

    route="metrics",

    methods=["GET"]

)

def get_metrics(req):

    response = {

        "invocations":
        metrics[
            "invocations"
        ],

        "errors":
        metrics[
            "errors"
        ],

        "avg_response_ms":
        142,

        "success_rate":
        round(

            (

                metrics[
                "invocations"
                ]

                -

                metrics[
                "errors"
                ]

            )

            /

            max(

                metrics[
                "invocations"
                ],

                1

            )

            *

            100,

            1

        )

    }

    return func.HttpResponse(

        json.dumps(
            response
        ),

        mimetype=
        "application/json"

    )

@app.route(

    route="event",

    methods=["POST"]

)

def send_event(req):

    logging.info(

        "Custom event triggered"

    )

    return func.HttpResponse(

        json.dumps({

            "success":True

        }),

        mimetype=
        "application/json"

    )
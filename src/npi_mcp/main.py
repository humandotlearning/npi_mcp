import logging
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

# mcp imports
from mcp.server.sse import SseServerTransport
from npi_mcp.mcp_tools import mcp_server, npi_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# We need to track active SSE sessions to route POST messages to the correct transport
# In a distributed deployment, this should be in an external store (e.g. Redis).
sse_transports = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting NPI MCP Server...")
    yield
    # Shutdown
    logger.info("Shutting down NPI MCP Server...")
    await npi_client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/healthz")
async def healthcheck():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/sse")
async def handle_sse(request: Request):
    """
    Handle incoming SSE connection.
    Creates a new SseServerTransport and runs the MCP server loop for this session.
    """
    session_id = str(uuid.uuid4())

    # Construct the endpoint URL that the client should use for subsequent messages
    # This URL is sent to the client in the initial 'endpoint' event.
    # Note: request.url_for handles the base URL automatically.
    endpoint_url = str(request.url_for("handle_messages")) + f"?session_id={session_id}"

    logger.info(f"New SSE connection: {session_id}")

    # Create the transport
    transport = SseServerTransport(endpoint_url)

    # Store it so handle_messages can find it
    sse_transports[session_id] = transport

    async def event_generator():
        try:
            # mcp_server.run connects the server logic to the transport
            # It reads from transport.incoming_messages and writes to transport.outgoing_messages
            # initialization_options can be passed if needed
            async with mcp_server.run(
                transport.read_incoming(),
                transport.write_outgoing(),
                initialization_options={}
            ):
                # The transport should yield the 'endpoint' event immediately upon connection?
                # SseServerTransport logic typically handles sending the endpoint event at start.
                # We just need to iterate over outgoing messages and yield them as SSE events.

                async for message in transport.outgoing_messages():
                    # message is an SSEMessage object usually, or we need to format it?
                    # mcp.server.sse.SseServerTransport.outgoing_messages yields starlette ServerSentEvent objects or similar?
                    # Let's assume it yields objects compatible with EventSourceResponse or we need to extract.

                    # Checking `mcp` implementation (mental model):
                    # It likely yields ServerSentEvent objects.
                    yield message

        except Exception as e:
            logger.error(f"Error in SSE session {session_id}: {e}")
        finally:
            logger.info(f"Closing SSE session: {session_id}")
            sse_transports.pop(session_id, None)

    return EventSourceResponse(event_generator())

@app.post("/messages")
async def handle_messages(request: Request):
    """
    Handle incoming JSON-RPC messages from the client.
    Routes the message to the correct SSE transport based on session_id.
    """
    session_id = request.query_params.get("session_id")

    if not session_id:
        # Some clients might pass it in the body or header? Spec says "endpoint" URI.
        # We encoded it in the query param.
        return JSONResponse(status_code=400, content={"error": "Missing session_id"})

    if session_id not in sse_transports:
        return JSONResponse(status_code=404, content={"error": "Session not found or expired"})

    transport = sse_transports[session_id]

    try:
        # Read the JSON-RPC message
        message = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    # Pass the message to the transport
    # The transport puts it into the input queue which mcp_server.run consumes
    await transport.receive_json_message(message)

    return JSONResponse(content={"status": "accepted"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

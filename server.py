import asyncio
import websockets
import logging

# Setup basic logging to see connections in the terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChatServer")

# Keep track of all active connections
CLIENTS = set()

async def broadcast(message, sender):
    """Sends a message to everyone except the original sender."""
    if CLIENTS:
        # Create a list of tasks to send the message to all other clients
        await asyncio.gather(
            *[client.send(message) for client in CLIENTS if client != sender],
            return_exceptions=True
        )

async def handler(websocket):
    """Handles the lifecycle of a single websocket connection."""
    # Register new client
    CLIENTS.add(websocket)
    logger.info(f"New connection established. Total clients: {len(CLIENTS)}")
    
    try:
        # Wait for messages from this client
        async for message in websocket:
            logger.info(f"Received: {message}")
            # Broadcast the message to others
            await broadcast(message, websocket)
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Unregister client on disconnect
        CLIENTS.remove(websocket)
        logger.info(f"Connection closed. Total clients: {len(CLIENTS)}")

async def main():
    # Listen on 0.0.0.0 to allow connections from any IP on the local network
    # Port 8765 is a common choice for examples, usually open on local networks
    async with websockets.serve(handler, "0.0.0.0", 8765):
        logger.info("Chat Server started on ws://0.0.0.0:8765")
        logger.info("Ensure your firewall allows incoming traffic on port 8765.")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")

import asyncio
import websockets
import sys
import json
import aioconsole

async def receive_messages(websocket):
    """Listens for messages from the server and prints them."""
    try:
        async for message in websocket:
            try:
                # Parse the JSON protocol
                data = json.loads(message)
                user = data.get("user", "Unknown")
                text = data.get("text", "")
                print(f"\n[{user}]: {text}")
            except json.JSONDecodeError:
                # Fallback for raw text messages
                print(f"\n{message}")
            
            print("> ", end="", flush=True)
    except websockets.exceptions.ConnectionClosed:
        print("\nDisconnected from server.")

async def send_messages(websocket, nickname):
    """Reads user input and sends it to the server wrapped in JSON."""
    while True:
        text = await aioconsole.ainput("> ")
        if text.strip():
            # Create the 'envelope' (Protocol)
            payload = {
                "user": nickname,
                "text": text
            }
            await websocket.send(json.dumps(payload))

async def main():
    # 1. Get Nickname first!
    nickname = await aioconsole.ainput("Enter your nickname: ")
    if not nickname.strip():
        nickname = "Anonymous"

    # Get server IP from command line argument, default to localhost
    server_ip = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    uri = f"ws://{server_ip}:8765"
    
    print(f"Connecting to {uri} as {nickname}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Type your messages below. Press Ctrl+C to exit.")
            
            # Run sender and receiver concurrently
            await asyncio.gather(
                receive_messages(websocket),
                send_messages(websocket, nickname)
            )
    except ConnectionRefusedError:
        print("Could not connect to the server. Is it running and reachable?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")

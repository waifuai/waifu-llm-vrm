# src/pywaifu/godot.py
import json
import socket
import threading
try:
    import godot_rl
    GODOT_RL_AVAILABLE = True
except ImportError:
    GODOT_RL_AVAILABLE = False


class GodotConnector:
    """
    Handles communication between Python and Godot.
    """

    def __init__(self, project_path: str, port: int = None, auto_start: bool = True, headless: bool = True):
        """
        Initializes the Godot connector.

        Args:
            project_path: Path to the Godot project directory.
            port: Optional port for communication.
            auto_start: Whether to automatically start Godot.
            headless: Whether to run Godot in headless mode.
        """
        self.project_path = project_path
        self.port = port
        self.auto_start = auto_start
        self.headless = headless
        self.callbacks = {}
        self._stop_event = threading.Event() #for stopping receiving loop
        if GODOT_RL_AVAILABLE:
            self._init_godot_rl()
        else:
            self._init_socket()

    def _init_godot_rl(self):
        """Initializes communication using godot-rl."""
        self.env = godot_rl.make(self.project_path, port=self.port, show_window=not self.headless)

    def _init_socket(self):
        """Initializes communication using custom sockets (fallback)."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.port is None:
            self.port = 9000 #Default
        self._connect_thread = None
        self._receive_thread = None

    def connect(self) -> None:
        """Establishes the connection to Godot."""
        if GODOT_RL_AVAILABLE:
            return
        else:
          self._connect_thread = threading.Thread(target=self._connect_socket)
          self._connect_thread.start()

    def _connect_socket(self):
        """Connect to Godot."""
        try:
           self.sock.connect(('localhost', self.port))
           print(f"Connected to Godot on port {self.port}")
           self._receive_thread = threading.Thread(target=self._receive_loop)
           self._receive_thread.start()
        except ConnectionRefusedError:
           raise GodotError(f"Could not connect to Godot on port {self.port}.  Is Godot running and listening?")


    def _receive_loop(self):
        """Continuosly receive messages."""
        buffer = ""
        while not self._stop_event.is_set():
            try:
                data = self.sock.recv(1024)
                if not data:
                    print("Godot disconnected.")
                    break

                buffer += data.decode()
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    try:
                        parsed_message = json.loads(message)
                        self._handle_event(parsed_message)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON received: {message}")
            except socket.error as e:
                if not self._stop_event.is_set(): #Avoid reporting error on disconnect.
                    print(f"Socket error: {e}")
                break

    def disconnect(self) -> None:
        """Closes the connection."""
        if GODOT_RL_AVAILABLE:
            self.env.close()
        else:
            self._stop_event.set()
            if self._receive_thread:
                self._receive_thread.join()
            if self.sock:
                self.sock.close()
            print("Disconnected from Godot.")


    def send(self, data: dict) -> None:
        """Sends data (serialized to JSON) to Godot."""
        if GODOT_RL_AVAILABLE:
            self.env.step(data)  # Placeholder - adapt to godot-rl
        else:
            message = json.dumps(data) + "\n"
            try:
                self.sock.sendall(message.encode())
            except socket.error as e:
                raise GodotError(f"Error sending data to Godot: {e}")

    def receive(self) -> dict:
        """Receives data (deserialized from JSON) from Godot."""
        #Receiving is handled by _receive_loop
        return {}

    def register_callback(self, event: str, callback: callable) -> None:
        """
        Registers a callback for a Godot event.
        """
        self.callbacks[event] = callback

    def rpc(self, func_name: str, *args) -> any:
        """Calls a function in Godot (Remote Procedure Call)."""
        if GODOT_RL_AVAILABLE:
            print("RPC using godot-rl - to be implemented")
            return None
        else:
            data = {"type": "rpc", "function": func_name, "args": args}
            self.send(data)
            return None #No return value.


    def _handle_event(self, event_data: dict) -> None:
        """Handles an event received from Godot."""
        event_type = event_data.get("type")
        if event_type in self.callbacks:
            self.callbacks[event_type](event_data)
        else:
            print(f"Unhandled event type: {event_type}")


class GodotError(Exception):
    """Custom exception for Godot connection errors."""
    pass
# rules.py

import logging
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# --- Basic Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)


# ==============================================================================
# Rule Definitions and State Management
# ==============================================================================

# --- Rule 1: Unsigned Executables ---
# Common user-writable directories where executables should not typically run from.
# This list can be expanded based on the operating system.
USER_DIRECTORIES: Tuple[str, ...] = (
    # Linux/macOS
    "/home/",
    "/Users/",
    "/tmp/",
    "/var/tmp/",
    # Windows
    "C:\\Users\\",
    "C:\\Windows\\Temp\\",
)

# --- Rule 2: Suspicious Parent-Child Processes ---
# A set of known suspicious (parent, child) process relationships.
SUSPICIOUS_PROCESS_PAIRS: Set[Tuple[str, str]] = {
    # Office applications spawning shells are highly suspicious
    ("winword.exe", "cmd.exe"),
    ("winword.exe", "powershell.exe"),
    ("excel.exe", "cmd.exe"),
    ("excel.exe", "powershell.exe"),
    ("powerpnt.exe", "cmd.exe"),
    # Common system processes that should not be spawning shells
    ("lsass.exe", "cmd.exe"),
    ("services.exe", "cmd.exe"),
    ("svchost.exe", "powershell.exe"),
    # Web servers spawning shells
    ("w3wp.exe", "cmd.exe"),
    ("httpd.exe", "sh"),
    ("nginx.exe", "cmd.exe"),
}

# --- Rule 3: High-Frequency Outbound Connections (Stateful) ---

class ConnectionMonitor:
    """
    A stateful class to track and detect high-frequency network connections from nodes.
    """
    def __init__(self, time_window_seconds: int = 60, threshold: int = 100):
        self.time_window = timedelta(seconds=time_window_seconds)
        self.threshold = threshold
        # Stores connection timestamps for each node_id
        self._connections: Dict[int, deque[datetime]] = {}
        logger.info(
            f"ConnectionMonitor initialized: window={time_window_seconds}s, threshold={threshold} conns"
        )

    def check_connection(self, event: Dict[str, Any]) -> bool:
        """
        Records a new connection and checks if the frequency threshold has been breached.

        Returns:
            True if the threshold is breached, False otherwise.
        """
        node_id = event.get("node_id")
        if not isinstance(node_id, int):
            return False

        now = datetime.utcnow()
        if node_id not in self._connections:
            self._connections[node_id] = deque()

        # Add the new connection timestamp
        self._connections[node_id].append(now)

        # Prune old timestamps that are outside the time window
        while self._connections[node_id] and (now - self._connections[node_id][0] > self.time_window):
            self._connections[node_id].popleft()

        # Check if the count exceeds the threshold
        current_count = len(self._connections[node_id])
        if current_count > self.threshold:
            logger.warning(
                f"High-frequency connection detected for node_id={node_id}. "
                f"Count={current_count} in the last {self.time_window.seconds}s."
            )
            return True

        return False

# Instantiate a global monitor to maintain state across function calls
connection_monitor = ConnectionMonitor(time_window_seconds=60, threshold=150)


# ==============================================================================
# Individual Rule Functions
# ==============================================================================
# Each rule is a self-contained function that returns a rule name if triggered,
# or None if not. This makes the system easy to extend.

def _rule_unsigned_executable_in_user_dir(event: Dict[str, Any]) -> Optional[str]:
    """Detects unsigned executables running from user-writable directories."""
    if event.get("event_type") != "process_creation":
        return None

    is_signed = event.get("details", {}).get("is_signed")
    process_path = event.get("details", {}).get("process_path")

    # Rule triggers if the executable is explicitly not signed and has a path
    if is_signed is False and process_path:
        if any(process_path.startswith(d) for d in USER_DIRECTORIES):
            logger.warning(
                f"RULE TRIGGERED: Unsigned executable '{process_path}' "
                f"running from a user directory."
            )
            return "UNSIGNED_EXEC_IN_USER_DIR"
    return None


def _rule_suspicious_parent_child_process(event: Dict[str, Any]) -> Optional[str]:
    """Detects known suspicious parent-child process relationships."""
    if event.get("event_type") != "process_creation":
        return None

    details = event.get("details", {})
    parent_process = details.get("parent_process_name", "").lower()
    child_process = details.get("process_name", "").lower()

    if (parent_process, child_process) in SUSPICIOUS_PROCESS_PAIRS:
        logger.warning(
            f"RULE TRIGGERED: Suspicious parent-child process relationship: "
            f"Parent='{parent_process}', Child='{child_process}'."
        )
        return "SUSPICIOUS_PARENT_CHILD_PROCESS"
    return None


def _rule_high_frequency_outbound_connections(event: Dict[str, Any]) -> Optional[str]:
    """Detects an abnormally high rate of outbound network connections from a single node."""
    if event.get("event_type") != "network_connection":
        return None

    # This rule is stateful and relies on the ConnectionMonitor instance
    if connection_monitor.check_connection(event):
        return "HIGH_FREQUENCY_OUTBOUND_CONNECTIONS"
    return None


# --- Rule Registry ---
# A list of all rule functions to be evaluated. To add a new rule,
# simply define a new function and add it to this list.
ALL_RULES: List[Callable[[Dict[str, Any]], Optional[str]]] = [
    _rule_unsigned_executable_in_user_dir,
    _rule_suspicious_parent_child_process,
    _rule_high_frequency_outbound_connections,
]


# ==============================================================================
# Main Evaluation Engine
# ==============================================================================

def evaluate_event(event: Dict[str, Any]) -> List[str]:
    """
    Evaluates a single event against all registered security rules.

    Args:
        event: A dictionary representing the security event. Expected keys vary
               by `event_type` but may include 'node_id', 'event_type', 'details'.

    Returns:
        A list of strings, where each string is the name of a triggered rule.
        Returns an empty list if no rules are triggered.
    """
    if not isinstance(event, dict) or "event_type" not in event:
        logger.error(f"Invalid event format received: {event}")
        return []

    logger.info(f"Evaluating event for node_id={event.get('node_id')}, type={event.get('event_type')}")

    triggered_rules = []
    for rule_function in ALL_RULES:
        try:
            result = rule_function(event)
            if result:
                triggered_rules.append(result)
        except Exception as e:
            logger.error(f"Error evaluating rule '{rule_function.__name__}': {e}", exc_info=True)

    if triggered_rules:
        logger.warning(f"Event triggered {len(triggered_rules)} rules: {triggered_rules}")
    else:
        logger.info("No rules triggered for this event.")

    return triggered_rules
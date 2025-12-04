import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from delay_logic import calculate_reply_delay

print("Testing Delay Calculation (using src/delay_logic.py):")

# Case 1: Very Active conversation (10 seconds ago)
last_active = datetime.now(timezone.utc) - timedelta(seconds=10)
delay_active = calculate_reply_delay(last_active)
print(f"Gap: 10s -> Delay: {delay_active:.2f}s (Expected 7-11s)")

# Case 1b: Moderately Active conversation (5 mins ago)
last_mod = datetime.now(timezone.utc) - timedelta(minutes=5)
delay_mod = calculate_reply_delay(last_mod)
print(f"Gap: 5m -> Delay: {delay_mod:.2f}s (Expected 7-20s)")

# Case 2: Short break (15 mins ago)
last_short = datetime.now(timezone.utc) - timedelta(minutes=15)
delay_short = calculate_reply_delay(last_short)
print(f"Gap: 15m -> Delay: {delay_short:.2f}s (Expected 60-300s)")

# Case 3: Long break (2 hours ago)
last_long = datetime.now(timezone.utc) - timedelta(hours=2)
delay_long = calculate_reply_delay(last_long)
print(f"Gap: 2h -> Delay: {delay_long:.2f}s (Expected 600-900s)")

# Case 4: New user
delay_new = calculate_reply_delay(None)
print(f"Gap: None -> Delay: {delay_new:.2f}s (Expected 180-420s)")

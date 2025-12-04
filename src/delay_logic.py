import random
from datetime import datetime

def calculate_reply_delay(last_interaction: datetime = None) -> float:
    """
    Calculates the delay before replying based on the time since the last interaction.
    
    Args:
        last_interaction: datetime object of the last message from the user (timezone aware).
                          None if new user.
                          
    Returns:
        Delay in seconds (float).
    """
    if not last_interaction:
        # New user or no history -> 10-30 seconds delay (Reduced for testing, was 180-420)
        return random.uniform(10, 30)

    # Ensure timezone awareness compatibility
    now_dt = datetime.now().astimezone()
    if last_interaction.tzinfo is None:
        last_interaction = last_interaction.astimezone()
        
    gap = (now_dt - last_interaction).total_seconds()
    
    if gap > 3600: # > 1 hour
        return random.uniform(600, 900) # 10-15 mins
    elif gap > 600: # > 10 mins
        return random.uniform(60, 300) # 1-5 mins
    elif gap < 20: # Very active conversation
        return random.uniform(7, 11) # 7-11 seconds
    else:
        return random.uniform(7, 20) # 7-20 seconds (Normal active)

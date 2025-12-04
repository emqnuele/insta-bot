# 🤖 Bea - Human-Like Instagram AI Agent

**Bea** is a sophisticated AI agent designed to automate Instagram Direct Messages with a focus on **human realism**. Unlike standard bots that reply instantly and mechanically, Bea simulates human behavior through dynamic delays, message batching, and a rich, consistent persona powered by **Google GenAI**.

Built by **[Emanuele Faraci](https://emanuelefaraci.com)**.

![Bea Architecture](assets/bea_architecture.png)
---

## 🚀 Key Features

### 🧠 Advanced AI Persona
- **Powered by Gemini**: Uses Google's model for fast, nuanced, and context-aware responses.
- **Deepfake Persona**: Loads a detailed psychological profile from `system_instruction.txt`, allowing your ai persona to maintain a consistent personality, backstory, and communication style (slang, lowercasing, emojis).
    - *Note*: The specific persona instructions for "Bea" are **not included** in this release. You must create your own `system_instruction.txt` file in the root directory to define your bot's personality.
- **Contextual Memory**: Remembers the last 25 messages of conversation for each user, ensuring continuity.

### ⏱️ Human-Like Behavior Engine
- **Dynamic Delays**: Bea doesn't reply instantly. The delay logic (`src/delay_logic.py`) calculates response times based on the conversation flow:
    - **Active Chat (< 20s gap)**: Replies in **7-11 seconds**.
    - **Normal Chat**: Replies in **7-20 seconds**.
    - **Short Break (> 10m)**: Takes **1-5 minutes** to reply.
    - **Long Break (> 1h)**: Takes **10-15 minutes** to reply.
    - **New Users**: Simulates a busy human by waiting **10-30 seconds** (configurable) before the first reply.
- **Typing Simulation**: Simulates "typing" time proportional to the length of the message being sent.

### ⚡ High-Performance Architecture
- **Concurrent Processing**: Uses a **Thread Pool** to handle multiple conversations simultaneously. Bea can "type" to User A while processing a new message from User B, ensuring no one is blocked.
- **Smart Batching**: If a user sends multiple short messages in a row (e.g., "Hey", "You there?", "???"), Bea waits (buffer window) and combines them into a single prompt. This saves API calls and gives the AI better context.
    - *Example*: User sends "Ciao" then "Come stai?". Bea sees this as one message: "Ciao\nCome stai?" and replies once, coherently.
- **Natural Message Splitting**: To mimic human chatting habits, the bot avoids sending walls of text. If the AI generates a long response, it is automatically split into multiple shorter messages (by newlines! You have to explicit it in the system instruction.).
    - *Realism*: Instead of one big block, the user sees: "Ciao" -> *typing...* -> "Come stai?". This creates a natural, engaging rhythm indistinguishable from a real person.
- **In-Flight Tracking**: Prevents duplicate replies by tracking messages currently being processed, even if the network is slow or Instagram retries delivery.

## 🛠️ Tech Stack

- **Python 3.10+**
- **[Instagrapi](https://github.com/adw0rd/instagrapi)**: For Instagram Private API interaction.
- **Google GenAI SDK**: For LLM integration.
- **Threading & Concurrency**: For non-blocking multitasking.

## 🏗️ Architecture & Deep Dive

### 1. The Brain: `AIClient` & `MessageRouter`
- **`src/ai_client.py`**: Wraps the Google GenAI SDK. It loads the **System Instruction** (the persona definition) and manages the chat session. It injects the last 25 messages of history into every prompt to ensure the AI remembers context.
- **`src/message_router.py`**: Acts as the gatekeeper. It decides whether a message should be answered by the AI or handled internally (e.g., commands like `/tqmmy`). It also filters out link-only messages to prevent spam processing.

### 2. The Nervous System: `StateStore` & `HistoryStore`
- **`src/state_store.py`**: A **thread-safe** persistence layer. It saves the IDs of every processed message to `data/state.json`. This prevents the bot from replying to the same message twice, even if the bot crashes and restarts. It uses a `threading.Lock` to ensure multiple threads don't corrupt the file.
- **`src/history_store.py`**: Manages the conversation history for each user in individual JSON files (`data/history/<user_id>.json`). It stores not just text, but also **timestamps**, which are crucial for calculating realistic delays.

### 3. The Heartbeat: `DelayLogic`
- **`src/delay_logic.py`**: This is where the "human" behavior is calculated. It determines how long to wait before replying based on the **gap** since the last interaction:
    - **< 20s (Active)**: 7-11s delay (Simulates immediate attention).
    - **> 10m (Short Break)**: 1-5m delay (Simulates doing something else).
    - **> 1h (Long Break)**: 10-15m delay (Simulates being away from phone).
    - **New User**: 10-30s delay (Simulates checking who the new person is).

### 4. The Engine: `main.py` & Concurrency
The main loop is designed to be **non-blocking**:
1.  **Fetch & Buffer**: It fetches messages from Instagram. If a user sends multiple messages quickly (e.g., "Hi", "You there?"), they are collected into a **Buffer** for 10 seconds.
2.  **Schedule**: Once the buffer window closes, a reply is **Scheduled** for a future time calculated by `DelayLogic`.
3.  **In-Flight Tracking**: To prevent duplicates, messages currently being processed are tracked in an `inflight_ids` set. If Instagram sends them again (network retry), they are ignored.
4.  **Concurrent Execution**: When a scheduled reply is due, it is submitted to a **ThreadPoolExecutor** (5 workers). This allows the bot to "type" and send messages to 5 different users simultaneously without pausing the main loop.

## 📂 Project Structure

```
insta-bot/
├── src/
│   ├── main.py           # Orchestrator: Main loop, buffering, and thread pool
│   ├── ai_client.py      # Brain: Google Gemini integration
│   ├── ig_client.py      # Hands: Instagrapi wrapper
│   ├── history_store.py  # Memory: JSON-based chat history
│   ├── state_store.py    # Safety: Thread-safe processed message tracker
│   ├── delay_logic.py    # Soul: Algorithms for human-like delays
│   └── message_router.py # Logic: Routing commands vs AI
├── data/                 # Persistence: Sessions and chat logs
├── tests/                # Verification: Unit and integration tests
├── system_instruction.txt # Persona: The psychological profile
└── requirements.txt      # Dependencies
```

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/emqnuele/insta-bot.git
    cd insta-bot
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate  # Windows
    source venv/bin/activate # Mac/Linux
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    Create a `.env` file with your credentials:
    ```env
    IG_USERNAME=your_instagram_username
    IG_PASSWORD=your_instagram_password
    AI_API_KEY=your_google_gemini_api_key
    # PROXY_URL=http://user:pass@host:port (Optional but recommended)
    ```

5.  **Run the Bot**:
    ```bash
    python src/main.py
    ```

## 🧪 Testing

The project includes a comprehensive test suite to verify logic without risking the Instagram account.

### Core Logic Tests
- **`tests/test_realistic_delay.py`**: Verifies the `DelayLogic` algorithm, ensuring delays fall within expected ranges for different conversation gaps (Active, Short Break, Long Break, New User).
- **`tests/test_batching.py`**: Simulates a stream of incoming messages to verify that the **Batching** logic correctly groups messages within the 10s window and triggers processing only when the window closes.
- **`tests/test_dedup.py`**: Verifies the **In-Flight Tracking** system. Simulates re-fetching the same message while it is currently being processed to ensure it is ignored and not replied to twice.
- **`tests/test_timestamp_filter.py`**: Verifies that the bot ignores messages sent *before* it started up, preventing "Phantom Replies" to old conversations.

### Integration Tests
- **`tests/test_concurrency.py`**: Verifies the **Thread Pool**. Submits multiple dummy tasks that sleep for 2 seconds and asserts that they complete in ~2 seconds total (parallel) rather than 6+ seconds (sequential).
- **`tests/test_genai_integration.py`**: A real integration test that connects to Google Gemini (using the API key) to verify that the persona is loaded correctly and the AI generates valid responses.

### How to Run
Run any test using python:
```bash
python tests/test_realistic_delay.py
```

---

*Disclaimer: This project is for educational purposes. Automating Instagram accounts may violate their Terms of Service. Use responsibly.*

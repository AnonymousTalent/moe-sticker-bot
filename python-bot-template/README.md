# Secure Telegram Bot & Dispatch System Template

This project provides a secure and scalable Python template for quickly launching Telegram bots and a backend dispatch system for order processing and revenue splitting. It is designed to keep sensitive tokens and credentials stored safely in local environment files.

This template is designed to run in any standard Python environment, including servers, development machines, Termux, or Pydroid 3.

## ✨ Features

- **Secure by Default**: Sensitive data like Bot Tokens and API keys are stored locally in a `.env` file, which is ignored by Git to prevent accidental exposure.
- **Scalable Bot Management**: Easily add or remove bots by editing the `config.json` file without changing the code.
- **Asynchronous Bot**: The `main.py` bot uses `asyncio` for better performance, suitable for handling multiple bots or high-load tasks.
- **Dispatch & Revenue System**: A complete Flask-based backend (`dispatch_system.py`) to handle webhooks, process orders, and automatically split revenue.
- **Core Dispatcher Logic**: Includes a foundational `dispatch_task` function that is called for every new order, ready for future expansion.
- **Payout Management**: Includes endpoints to list pending payouts and generate CSV files for batch bank transfers.
- **Easy Deployment**: Comes with a `requirements.txt` file for one-click dependency installation.

## 🚀 Quick Start

Follow these steps to set up and run the bot and the dispatch system.

### 1. Install Dependencies

It is highly recommended to use a virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt
```

### 2. Configure the Services

This project contains two main services: the Telegram Bot (`main.py`) and the Dispatch System (`dispatch_system.py`).

#### A. For the Telegram Bot (`main.py`)

1.  **Copy the config example**:
    ```bash
    cp config.json.example config.json
    ```

2.  **Edit `config.json`**: Open the file and replace the placeholder tokens with your actual Telegram Bot tokens.
    ```json
    {
        "StormHawk_bot": "YOUR_REAL_BOT_TOKEN_HERE",
        "StormMedic_bot": "ANOTHER_REAL_BOT_TOKEN_HERE"
    }
    ```

3.  **Set the Target Chat**: Open `main.py` and change the `TARGET_CHAT_ID` variable to the user or channel where you want to send messages.

#### B. For the Dispatch System (`dispatch_system.py`)

1.  **Create the environment file**: Copy the example file to create your own local environment configuration.
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file**: Open the new `.env` file and fill in your credentials. This file is kept private and should not be committed to Git.
    ```dotenv
    # Telegram Bot Credentials (for notifications)
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    TELEGRAM_CHAT_ID="YOUR_TARGET_CHAT_ID_FOR_NOTIFICATIONS"

    # --- Payout Account Settings ---
    # Main account for the system owner (CTBC Bank)
    BANK_CTBC_CODE="822"
    BANK_CTBC_ACCOUNT="484540302460"

    # Payout account for teams/developers (Post Office)
    BANK_POST_CODE="700"
    BANK_POST_ACCOUNT="00210091602429"

    # Account for system's share of revenue
    SYSTEM_PAYOUT_ACCOUNT="700-ZZZZZZZZZZ"
    ```

### 3. Run the Services

You can run the bot and the dispatch system in separate terminal sessions.

#### To run the Telegram Bot:

```bash
python main.py
```
If configured correctly, you will see startup messages in your terminal, and your target chat will receive a notification from each bot.

#### To run the Dispatch System Server:

```bash
python dispatch_system.py
```
This will start a Flask server, typically on `http://0.0.0.0:5001`. The server is now ready to accept webhook requests.

## ⚙️ Dispatch System API Endpoints

The `dispatch_system.py` server provides the following API endpoints:

-   `POST /webhook`: The main endpoint to receive new order data. It processes the order, saves it to the database, splits the revenue, triggers the core dispatcher, and sends a Telegram notification.
-   `GET /list_payouts`: Returns a JSON list of all payout records that are currently in 'pending' status.
-   `GET /generate_payout_file`: Generates and returns a `payouts_batch.csv` file, formatted for batch transfers (e.g., at a Post Office), containing all pending payouts.

## 🔧 Future Expansion

You can build upon this template by:
- Adding new automated commands to the bot.
- Integrating more third-party APIs into the dispatch system.
- Developing a frontend interface to interact with the API.
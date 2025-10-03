import requests
import os
import logging
import sqlite3
from flask import Flask, request, jsonify, Response
from datetime import datetime
import csv
from io import StringIO
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database Initialization ---
def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE,
            customer_name TEXT,
            pickup_address TEXT,
            delivery_address TEXT,
            amount REAL,
            status TEXT,
            platform TEXT,
            team_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME
        )
    """)

    # Revenue table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revenue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            total_amount REAL,
            owner_share REAL,
            team_share REAL,
            system_share REAL,
            date DATE,
            FOREIGN KEY (order_id) REFERENCES orders (order_id)
        )
    """)

    # Payouts table for tracking transfers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            recipient_type TEXT,      -- 'owner', 'team', or 'system'
            recipient_account TEXT,   -- Bank account number
            amount REAL,
            status TEXT DEFAULT 'pending', -- 'pending' or 'processed'
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# --- Core Functions ---
def send_telegram_notification(message: str):
    """Sends a notification to the configured Telegram chat."""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not bot_token or not chat_id:
            logger.error("Telegram credentials (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID) are not configured.")
            return False

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram notification: {e}")
        return False

def calculate_revenue_split(amount, owner_ratio=0.70, team_ratio=0.20, system_ratio=0.10):
    """Calculates the revenue split based on predefined ratios."""
    return {
        "owner": amount * owner_ratio,
        "team": amount * team_ratio,
        "system": amount * system_ratio,
        "total": amount
    }

def save_order(order_data):
    """Saves or replaces an order in the database."""
    try:
        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO orders
            (order_id, customer_name, pickup_address, delivery_address,
             amount, status, platform, team_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_data.get('order_id'),
            order_data.get('customer_name'),
            order_data.get('pickup_address'),
            order_data.get('delivery_address'),
            order_data.get('amount'),
            order_data.get('status'),
            order_data.get('platform'),
            order_data.get('team_id')
        ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error in save_order: {e}")
        return False

def save_revenue(order_id, revenue_split):
    """Saves the calculated revenue split to the database."""
    try:
        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO revenue
            (order_id, total_amount, owner_share, team_share, system_share, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            revenue_split['total'],
            revenue_split['owner'],
            revenue_split['team'],
            revenue_split['system'],
            datetime.now().date()
        ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Revenue save error: {e}")
        return False

def save_payouts(order_id, revenue_split):
    """Creates payout records for each party based on the revenue split."""
    try:
        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()

        # Get payout accounts from standardized environment variables
        owner_account = os.getenv("BANK_CTBC_ACCOUNT")
        team_account = os.getenv("BANK_POST_ACCOUNT")
        system_account = os.getenv("SYSTEM_PAYOUT_ACCOUNT")

        if not all([owner_account, team_account, system_account]):
            logger.error("Payout accounts (BANK_CTBC_ACCOUNT, BANK_POST_ACCOUNT, SYSTEM_PAYOUT_ACCOUNT) are not configured in .env")
            return False

        payouts_data = [
            (order_id, "owner", owner_account, revenue_split["owner"]),
            (order_id, "team", team_account, revenue_split["team"]),
            (order_id, "system", system_account, revenue_split["system"]),
        ]

        cursor.executemany("""
            INSERT INTO payouts (order_id, recipient_type, recipient_account, amount)
            VALUES (?, ?, ?, ?)
        """, payouts_data)

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Payout save error: {e}")
        return False

def dispatch_task(order_data):
    """
    Placeholder for the core dispatcher logic.
    For now, it just logs the task that would be dispatched.
    """
    team_id = order_data.get('team_id')
    order_id = order_data.get('order_id')
    logger.info(f"Dispatching task for order '{order_id}' to team '{team_id}'.")
    # In the future, this could be expanded to:
    # - Find available resources for the team.
    # - Send the task via a message queue or direct API call.
    # - Update the order status in the database.
    return True

# --- API Endpoints ---
@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handles incoming order data from webhooks."""
    try:
        data = request.get_json()
        required_fields = ['order_id', 'customer_name', 'amount', 'team_id']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        order_data = {
            'order_id': data['order_id'],
            'customer_name': data['customer_name'],
            'pickup_address': data.get('pickup_address', ''),
            'delivery_address': data.get('delivery_address', ''),
            'amount': float(data['amount']),
            'status': data.get('status', 'received'),
            'platform': data.get('platform', 'unknown'),
            'team_id': data['team_id']
        }

        if save_order(order_data):
            revenue_split = calculate_revenue_split(order_data['amount'])
            save_revenue(order_data['order_id'], revenue_split)
            save_payouts(order_data['order_id'], revenue_split)

            # Dispatch the task to the appropriate team
            dispatch_task(order_data)

            message = f"""
📦 *New Order Received:* `#{order_data['order_id']}`
- - - - - - - - - - - - - - - - -
👤 *Customer:* {order_data['customer_name']}
💰 *Amount:* ${order_data['amount']:.2f}
🏢 *Team:* {order_data['team_id']}
📍 *Platform:* {order_data['platform']}
- - - - - - - - - - - - - - - - -
💵 *Revenue Split:*
  •  *Owner:* `${revenue_split['owner']:.2f}` (70%)
  •  *Team:* `${revenue_split['team']:.2f}` (20%)
  •  *System:* `${revenue_split['system']:.2f}` (10%)
            """
            send_telegram_notification(message)
            return jsonify({
                "status": "success",
                "order_id": order_data['order_id'],
                "revenue_split": revenue_split
            }), 201
        else:
            return jsonify({"error": "Failed to save order"}), 500

    except (ValueError, TypeError) as e:
        logger.error(f"Webhook data error: {e}")
        return jsonify({"error": f"Invalid data format: {e}"}), 400
    except Exception as e:
        logger.error(f"Webhook internal error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/list_payouts', methods=['GET'])
def list_payouts():
    """Lists all payout records with 'pending' status."""
    try:
        conn = sqlite3.connect("orders.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payouts WHERE status = 'pending'")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])
    except sqlite3.Error as e:
        logger.error(f"List payouts error: {e}")
        return jsonify({"error": "Failed to fetch payouts"}), 500

@app.route('/generate_payout_file', methods=['GET'])
def generate_payout_file():
    """Generates a CSV file for pending payouts."""
    try:
        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()
        cursor.execute("SELECT recipient_account, amount FROM payouts WHERE status = 'pending'")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "No pending payouts to generate.", 404

        output = StringIO()
        writer = csv.writer(output)
        # Header for Post Office batch transfer format
        writer.writerow(["郵局代號", "帳號", "金額", "姓名", "ID"])
        for account, amount in rows:
            # Placeholder for name and ID, as they are not stored
            writer.writerow(["700", account, int(amount), "收款人", ""])

        output.seek(0)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=payouts_batch.csv"}
        )
    except Exception as e:
        logger.error(f"Payout file generation error: {e}")
        return jsonify({"error": "Failed to generate payout file"}), 500

if __name__ == '__main__':
    # Set host to '0.0.0.0' to be accessible from the network
    app.run(host='0.0.0.0', port=5001, debug=True)
# Pukla guma

GSM proxy discord bot.

Send a $-prefixed message to a channel whose name is a valid phone number to send a text message to that number.
The prefix will be stripped.

TODO: Incoming texts will be sent to the channel named after the phone number.

TODO: support voice calls

## Usage

```bash
python -m virtualenv venv && source venv/bin/activate  # (Optional)
pip install -r requirements.txt
echo "00386123123" > admin_number.env  # Used to send a test SMS on startup
echo "xxxxxxx" > token.env  # Discord API token
echo "$" > magic_prefix.env  # Prefix for sending SMS (default: $, keep secret if using webhooks)
python main.py on  # Power the LTE module (if not manually powered)
python main.py unlock 1234  # Unlock SIM card (if not already unlocked)
python main.py run  # Start the discord bot
```

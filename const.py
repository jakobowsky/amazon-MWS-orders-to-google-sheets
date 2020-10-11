import os
from dotenv import load_dotenv

load_dotenv()

# Credentials
MWS_ACCESS_KEY = os.environ["MWS_ACCESS_KEY"]
MWS_SECRET_KEY = os.environ["MWS_SECRET_KEY"]
MWS_SELLER_ID = os.environ["MWS_SELLER_ID"]

GOOGLE_SHEET_KEY = os.environ["GOOGLE_SHEET_KEY"]

# Amazon marketplace IDs
US = "ATVPDKIKX0DER"

# Amazon regions
AMAZON_NA_REGION = "Amazon NA"
CANADA = "A2EUQ1WTGCTBG2"
MEXICO = "A1AM78C64UM0Y8"

NA_MARKETPLACES = [
    CANADA,
    MEXICO,
    US,
]

# Amazon order status
ORDER_STATUS = ["Unshipped", "Shipped", "PartiallyShipped"]

# Google sheets config
AMAZON_WORKSHEET_NAME = "Amazon"


# Google Sheets Columns
COL_DATE = "Purchase date"
COL_ORDER_ID = "Order ID"
COL_ORDER_STATUS = "Order Status"
COL_EMAIL = "Email"
COL_TOTAL_PRICE = "Total Price"

COLUMNS = [COL_DATE, COL_ORDER_ID, COL_ORDER_STATUS, COL_EMAIL, COL_TOTAL_PRICE]

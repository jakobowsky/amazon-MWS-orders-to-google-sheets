import mws
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import const
from datetime import datetime, timedelta
from dateutil.parser import parse
from collections import OrderedDict


class GoogleSheets:
    def __init__(self, credentials_file, sheet_key, worksheet_name):
        self.credentials_file = credentials_file
        self.sheet_key = sheet_key
        self.worksheet_name = worksheet_name
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        self.sheet_object = self._get_sheet_object()

    def _get_sheet_object(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_file, self.scope
        )
        client = gspread.authorize(credentials)
        return client.open_by_key(self.sheet_key).worksheet(self.worksheet_name)

    def write_header_if_doesnt_exist(self, columns):
        """
        columns = list of columns - header of sheet
        """
        data = self.sheet_object.get_all_values()
        if not data:
            self.sheet_object.insert_row(columns)

    def append_rows(self, rows):
        """
        rows = list of lists - amazon
        """
        last_row_number = len(self.sheet_object.col_values(1)) + 1
        self.sheet_object.insert_rows(rows, last_row_number)

    def get_last_date(self):
        last_date = self.sheet_object.col_values(1)[-1]  # col 1 = PurchaseDate
        if last_date == const.COL_DATE or last_date == "":
            return datetime.now() - timedelta(days=5)

        return parse(last_date) + timedelta(seconds=10)


class AmazonOrders:
    def __init__(
        self, access_key, secret_key, account_id, marketplaces_ids, order_status, region
    ):
        self.access_key = access_key
        self.secret_key = secret_key
        self.account_id = account_id
        self.marketplaces_ids = marketplaces_ids
        self.order_status = order_status
        self.region = region
        self.sleep_time = 20
        self.mws_orders = self._build_mws_orders()

    def _build_mws_orders(self):
        return mws.Orders(
            access_key=self.access_key,
            secret_key=self.secret_key,
            account_id=self.account_id,
            region=self.region,
        )

    def get_orders(self, last_date):
        """
        last_date - last_date from google sheet
        """
        orders_data = []
        orders = self.mws_orders.list_orders(
            marketplaceids=self.marketplaces_ids,
            created_after=last_date.isoformat(),
            orderstatus=self.order_status,
        ).parsed

        try:
            if type(orders["Orders"]["Order"]) != list:
                orders_data += [orders["Orders"]["Order"]]
            else:
                orders_data += orders["Orders"]["Order"]
        except KeyError:
            print("No new orders...")
            return []
        i = 1
        while True:

            if i > 5:
                print("More than 5 requests, sleeping for 60 seconds...")
                time.sleep(60)

            if "NextToken" in orders:
                print("Next Token...")
                token = orders["NextToken"]["value"]
                orders = self.mws_orders.list_orders(next_token=token).parsed
                orders_data += orders["Orders"]["Order"]
                i += 1
            else:
                break

        print("Got :", len(orders_data), " reports...")
        return orders_data


class AmazonScript:
    def __init__(self):
        self.google_sheets = GoogleSheets(
            "client_secret.json", const.GOOGLE_SHEET_KEY, const.AMAZON_WORKSHEET_NAME
        )
        self.na_mws_orders = AmazonOrders(
            const.MWS_ACCESS_KEY,
            const.MWS_SECRET_KEY,
            const.MWS_SELLER_ID,
            const.NA_MARKETPLACES,
            const.ORDER_STATUS,
            "US",
        )

    def parse_orders(self, orders):
        parsed_orders = []
        for order in orders:
            parsed_orders.append(self.parse_single_order(order))
        return parsed_orders

    def parse_single_order(self, order):
        purchase_date = order["PurchaseDate"]["value"]
        order_id = order["AmazonOrderId"]["value"]
        order_status = order["OrderStatus"]["value"]

        order_total_price = order["OrderTotal"]["Amount"]["value"]
        email = self.get_order_email(order)
        row = OrderedDict()
        row[const.COL_DATE] = purchase_date
        row[const.COL_ORDER_ID] = order_id
        row[const.COL_ORDER_STATUS] = order_status
        row[const.COL_EMAIL] = email
        row[const.COL_TOTAL_PRICE] = order_total_price

        return row

    def get_order_email(self, order):
        if "BuyerEmail" in order:
            return order["BuyerEmail"]["value"]
        else:
            return "Unknown"

    def insert_rows_into_sheet(self, rows):
        ready_rows = [list(row.values()) for row in rows]
        self.google_sheets.append_rows(ready_rows)

    def run(self):
        self.google_sheets.write_header_if_doesnt_exist(const.COLUMNS)
        last_date = self.google_sheets.get_last_date()
        print("Last Date: ", last_date)

        print("Getting NA orders...")
        orders = self.na_mws_orders.get_orders(last_date)

        parsed_orders = self.parse_orders(orders)
        self.insert_rows_into_sheet(parsed_orders)

        print("DONE")


def main():
    amazon = AmazonScript()
    amazon.run()


if __name__ == "__main__":
    main()
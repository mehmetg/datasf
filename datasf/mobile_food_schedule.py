from datasf.socrata_client import SocrataClient
from colorama import (
    Fore,
    Style,
)
from typing import (
    Tuple,
    List,
)
from datetime import datetime
import pytz
import logging

LOGGER = logging.getLogger(__name__)

# Since the tool will be looking at SF/CA data the assumption
# is the times reported are in US/Pacific timezone
# Using this will ensure we'll get the right timezone even
# the client's system clock is not in the correct time zone
SF_TZ = pytz.timezone("US/Pacific")


class MobileFoodSchedule(object):
    SERVER = "data.sfgov.org"
    DATASET_NAME = "mobile_food_schedule"
    DATASET_ID = "jjew-r69b"
    DATASET_ALIAS = "mfs"
    WIDTH = 200
    FIELDS = ("applicant", "location")
    HEADERS = ("NAME", "ADDRESS")

    def __init__(self):
        self.offset = 0

    @classmethod
    def build_mobile_food_schedule_query(cls, day: int, time: str, page_size, page_offset) -> str:
        return f"SELECT {', '.join(cls.FIELDS)} WHERE (dayorder={day} AND start24<='{time}' AND end24 > '{time}') " \
               f"ORDER BY applicant LIMIT {page_size} OFFSET {page_offset}"

    @staticmethod
    def get_date() -> Tuple[int, str]:
        now = datetime.now(tz=SF_TZ)
        # change Sunday to be day 0 as per API spec
        day = (now.weekday() + 1) % 7
        time_24h = now.strftime("%H:%M")
        return day, time_24h

    @classmethod
    def add_parsers(cls, subparsers, base_parser) -> None:
        today, now = cls.get_date()
        mfs_parser = subparsers.add_parser(cls.DATASET_NAME, aliases=[cls.DATASET_ALIAS],
                                           help="Interacts with mobile food schedule dataset", parents=[base_parser])
        mfs_parser.add_argument("--day", type=int, default=today, required=False,
                                help="Day of the week 0: Sunday, ..., 7: Monday, default: today")
        mfs_parser.add_argument("--time", type=str, default=now, required=False,
                                help="Time of the day in 24hr format: HH:MM")


    @classmethod
    def format_output(cls, data: List[dict]) -> str:
        if data is None:
            return None
        # column width is total width / number of column headers
        col_width = cls.WIDTH // len(cls.HEADERS)
        # Build the headers by left justifying them to column width
        output = []

        # takes a data record and extracts the fields from it and after left justifying it
        # to col width joins them to a single line for printing
        # the line below has uses 2 generators one for the individual fields
        # (entry[f].ljust(col_width) for f in cls.FIELDS)
        # and one for the lines
        # (("".join((entry[f].ljust(col_width) for f in cls.FIELDS))) for entry in data)
        # the use of these generators makes the string concatenation faster and more memory efficient
        # it is harder to read but much more efficient which is important for larger datasets
        return "\n".join(
            # generates lines for each data entry
            (("".join(
                # generates colums from fields
                (entry[f].ljust(col_width) for f in cls.FIELDS)
            )) for entry in data)
        )

    def get(self, day: int, time: str, page_size: int, page_offset: int) -> List[str]:
        self.offset = 0
        with SocrataClient(server=self.SERVER, dataset_id=self.DATASET_ID) as client:
            self.offset = page_offset
            while True:
                q = self.build_mobile_food_schedule_query(day=day, time=time, page_size=page_size,
                                                          page_offset=self.offset)
                LOGGER.debug("Query: %s", q)
                results = client.get(query=q)
                # collect results yield a generator for retrieval
                yield self.format_output(results)
                self.offset += page_size
                if results is None or len(results) < page_size:
                    # if results is None then we must have triggered throttling
                    # A warning message will be shown and user will be asked to use a token
                    break

    def print_interactive(self, day: int, time: str, page_size: int, page_offset: int) -> List[str]:
        # zips headers with fields and feeds it to the formatter

        print(self.format_output([dict(zip(self.FIELDS, self.HEADERS))]))
        for batch in self.get(day=day, time=time, page_size=page_size, page_offset=page_offset):
            print(batch)
            resp = input(f"Please hit {Fore.LIGHTGREEN_EX}enter{Style.RESET_ALL} to continue, {Fore.RED}q + enter{Style.RESET_ALL} to abort.")
            if resp.strip() == 'q':
                break

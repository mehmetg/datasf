import logging
import os
from argparse import (
    ArgumentParser,
    Namespace,
)
from typing import (
    List,
)

from datasf.mobile_food_schedule import MobileFoodSchedule

logging.basicConfig(level=logging.getLevelName(os.getenv("LOG_LEVEL", "WARNING")))
LOGGER = logging.getLogger(__name__)

DATA_SETS = {
    MobileFoodSchedule.DATASET_NAME: MobileFoodSchedule.DATASET_ID,
    # add more categories
}


def process_args(args: List[str] = []) -> Namespace:
    parser = ArgumentParser(description="Tool to interact with Data SF data sets")
    subparsers = parser.add_subparsers(dest="dataset_name")
    base_parser = ArgumentParser(add_help=False)
    base_parser.add_argument("--page-size", type=int, default=10, required=False,
                             help="Number of results to show per page, default: 10")
    base_parser.add_argument("--page-offset", type=int, default=0, required=False,
                             help="Results to skip: default: 0")
    MobileFoodSchedule.add_parsers(subparsers=subparsers, base_parser=base_parser)
    subparsers.required = True
    return parser.parse_args(namespace=base_parser.parse_args(args))


def main() -> None:
    args = process_args()
    LOGGER.debug(args)
    # decide which data accessor to use we can use
    accessors = [MobileFoodSchedule]

    for accessor in accessors:
        if args.dataset_name in (accessor.DATASET_NAME, accessor.DATASET_ALIAS):
            data_accessor = accessor()
            break
    else:
        raise NotImplementedError(f"Dataset {args.dataset_name} is not supported")

    # this check is needed to handle class specific issues
    # if we extend this tool we can create an interface to make these checks redundant and unify supported methods
    if isinstance(data_accessor, MobileFoodSchedule):
        data_accessor.print_interactive(day=args.day, time=args.time, page_size=args.page_size,
                                        page_offset=args.page_offset)
    else:
        # for now if it's not in the supported class we bail
        raise NotImplemented(f"Dataset {type(data_accessor)} is not supported")


if __name__ == '__main__':
    main()

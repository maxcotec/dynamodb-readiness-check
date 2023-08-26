import argparse
import os
import logging.config
import logging
import sys
from datetime import date, datetime

import boto3

from readiness_check import DynamoDBReadiness

try:
    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
except KeyError as e:
    raise ModuleNotFoundError("Please provide AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")


def parse_arguments():
    """ parse the arguments of the script """
    parser = argparse.ArgumentParser(description='readiness check')

    # Required Arguments
    args_parse = parser.add_argument_group(title='required arguments')
    args_parse.add_argument('--table-name', help='name of the source table to check data for.')
    args_parse.add_argument('--date', help='check if given date date is available.')
    args_parse.add_argument('--aws-region', help='aws region', default='eu-west-1')

    # Parse the args and check the parameters are valid
    parsed_args = parser.parse_args()

    # Check date format is valid iso (yyyy-mm-dd) and store as date object
    try:
        parsed_args.date = date.fromisoformat(parsed_args.date)
    except ValueError:
        parsed_args.error('--date needs to be in iso format (yyyy-mm-dd)')

    return parsed_args


def init_logger():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
    })
    logging.basicConfig(format='%(asctime)s %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    return logging.getLogger(__name__)


if __name__ == "__main__":
    logger = init_logger()
    args = parse_arguments()

    logger.info("Setting aws boto3 session")
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=args.aws_region
    )

    logger.info("initializing dynamoDb readiness class")
    db = DynamoDBReadiness("readiness-states", boto3_session=session)

    logger.info("Checking readiness state")
    result = db.check_ready(args.table_name, date=args.date)
    sys.exit(0 if result else 1)


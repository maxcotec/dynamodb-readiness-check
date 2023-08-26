import logging
from datetime import date
from typing import Optional

import boto3


class DynamoDBReadiness:
    """Helper class for interacting with a DynamoDB readiness table.

    Used by pipelines for determining when tables are ready to be used.
    """
    _boto3_session: boto3.Session = None
    _dynamodb_table: str = None

    def __init__(self,
                 dynamodb_table: str,
                 region_name: str = "eu-west-1",
                 boto3_session: Optional[boto3.Session] = None) -> None:
        """Initialise the DynamoDBReadiness helper.

        :param dynamodb_table: DynamoDB table table to use for the readiness operations
        :param region_name: DynamodDB table region
        :param boto3_session: A boto3 session to use (Optional)
        """
        self.logger = logging.getLogger(__name__)
        self._boto3_session = boto3_session or boto3.Session(region_name=region_name)
        self._dynamodb_table = dynamodb_table

    def check_ready(self, table: str, date: date) -> bool:
        """Check if the table is ready for the given date.
        Returns boolean, depending on whether the table is ready.

        :param table: Table to check the state for
        :param date: Date to check the state for
        """
        is_ready = False
        table_lowercase = table.lower()
        date_str = date.strftime("%Y-%m-%d")
        self.logger.info(f"Checking state: table={table_lowercase}, date={date_str}")

        dynamodb_table = self._get_dynamodb_table_resource()
        response = dynamodb_table.get_item(Key={'name': table, 'date': date_str})
        item = response.get('Item')

        if item:
            is_ready = True if item['date'] == date_str else False

        status_string = f"Resource `{table_lowercase}` for date {date_str} is"
        self.logger.debug(f"{status_string} ready" if is_ready else f"{status_string} not ready.")
        return is_ready

    def _get_dynamodb_table_resource(self) -> boto3.session.Session.resource:
        """Get a boto3 resource for the DynamoDB table being used.

        :return: DynamoDB table resource
        """
        aws_client = self._boto3_session.resource("dynamodb")
        return aws_client.Table(self._dynamodb_table)


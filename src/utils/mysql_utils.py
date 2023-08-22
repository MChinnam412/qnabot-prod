import os
import pickle
from datetime import datetime

import mysql.connector
from starlette.config import Config

from src.utils.logger_utils import Logger

logger = Logger()
logging = logger.get_logger()
config = Config("configs/properties.conf")


class MySQLConnection:
    """
    connection and querying the database
    """
    mydb = None
    cursor = None

    def __init__(self):
        """
        connecting to MySQL database
        """
        try:
            
            self.mydb = mysql.connector.connect(
                host=os.environ.get("MYSQL_HOST"),
                port=int(os.environ.get("MYSQL_PORT")),
                database=os.environ.get("MYSQL_DB"),
                user=os.environ.get("MYSQL_USER"),
                password=os.environ.get("MYSQL_PASSWORD"),
            )
            self.table_name = os.environ.get("MYSQL_TABLE_NAME")
            self.cursor = self.mydb.cursor()
            logging.info("Successfully connected to MySQL")
        except Exception as ex:
            if config.get("MYSQL_HOST") is None:
                config.get("MYSQL_HOST")
            if config.get("MYSQL_PORT") is None:
                print("MYSQL_PORT none")
            if config.get("MYSQL_DB") is None:
                print("MYSQL_DB")
            if config.get("MYSQL_PASSWORD") is None:
                print("MYSQL_PASSWORD")
            logging.error(f"Error connecting to MySQL: {ex}")

    def get_conversation_data(self, unique_id):
        """
        retrieve conversation if the sessionId exists
        :param unique_id:
        :return:
        """
        try:
            query_table = f"select conversation from {self.table_name} where sessionId = %s ;"
            self.cursor.execute(query_table, [unique_id])
            output = []
            for row in self.cursor.fetchall():
                output.append(row)
            if len(output) > 0:
                output = pickle.loads(output[0][0])
            else:
                output = None
            logging.info("Successfully able to fetch data from database")
            return output
        except Exception as ex:
            logging.error(f"Error while fetching data from database: {ex}")
        return None

    def update_record(self, args):
        """
        updating conversation wrt sessionId
        :param unique_id:
        :param record:
        :return:
        """
        try:
            update_query = f"UPDATE {self.table_name} SET update_timestamp=%s, conversation = %s WHERE sessionId = %s;"
            self.cursor.execute(update_query, args)  # (update_timestamp, conversation, sessionId))
            self.mydb.commit()
            logging.info("Successfully updated record in database")
        except Exception as ex:
            logging.error(f"Error while updating record: {ex}")
        return

    def insert_data(self, args):
        """
        inserting data into database if sessionId doesn't exist
        :param args:
        :return:
        """
        try:
            if self.mydb is None or self.mydb.is_closed() or self.cursor is None:
                self.__init__()
            sql_query = f"INSERT INTO {self.table_name} (sessionId, start_timestamp, update_timestamp, conversation) VALUES (%s, %s, %s, %s);"
            self.cursor.execute(sql_query, args)
            self.mydb.commit()
            logging.info("Successfully inserted the conversation data into the database")
        except Exception as ex:
            logging.error(f"Error inserting data the data to the database: {ex}")
        return

    def close_connection(self):
        try:
            self.cursor.close()
            self.mydb.close()
            logging.info("Successfully closed connection to MySQL")
        except Exception as ex:
            logging.error(f"Error closing connection to MySQL: {ex}")


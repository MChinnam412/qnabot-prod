import pickle
from datetime import datetime

from langchain.memory import ConversationBufferMemory

from src.__init__ import DEFAULT_GENERIC_OUTPUT, URLS
from src.azure_qna_maker import QuestionAnswering
from src.openaI_code import OpenAIQuestionAnswering
from src.utils.logger_utils import Logger
from src.utils.mysql_utils import MySQLConnection
import os

logger = Logger()
logging = logger.get_logger()


class GenericQnaAnswering:
    """
    combining both OpenAI and Azure QnA Maker
    """
    openai_instance = None
    azure_qna_maker = None
    sessionId_exists = False
    mysql_instance = None
    current_timestamp = None
    mysql_timestamp = None

    def __init__(self, ):
        """
        loading OpenAI, Azure QnA Maker, MySQL connections
        """
        try:
            # To use OpenAI uncomment these lines
            # self.openai_instance = OpenAIQuestionAnswering(URLS)
            # self.openai_instance.load_chain()
            self.azure_qna_maker = QuestionAnswering()
            self.mysql_instance = MySQLConnection()
            logging.info("Successfully initialized OpenAI")
        except Exception as ex:
            logging.error(f"Error while initializing OpenAI or Azure QnA Maker: {ex}")

    def get_session_id_exists(self, sessionId):
        """
        check in sql if session exists and retrieve memory
        :param sessionId:
        :return:
        """
        output = None
        try:
            output = self.mysql_instance.get_conversation_data(sessionId)
            return output
        except Exception as ex:
            logging.info(f"Error while checking if session exists: {ex}")
        return None

    def get_current_timestamp(self):
        """
        generting timestamp for logging purposes
        As well as for generating sessionId
        :return:
        """
        try:
            self.current_timestamp = datetime.now().strftime("%m/%d/%YT%H:%M:%S.%f")
            self.mysql_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except Exception as ex:
            print(f"Error while generating timestamp: {ex}")

    def get_answer(self, sessionId, question):
        """
        checking input question
        :param question:
        :return:
        """
        try:
            self.sessionId_exists = False
            memory = ConversationBufferMemory()
            self.get_current_timestamp()

            # checking if session exists and querying db
            # If session doesn't exists creating new sessionId
            if sessionId is not None:
                memory_cache = self.get_session_id_exists(sessionId)
                if memory_cache is not None:
                    self.sessionId_exists = True
                    memory = memory_cache
            else:
                join_question = "".join(question.split())
                sessionId = str(hash(self.current_timestamp + join_question))
            output = self.azure_qna_maker.get_output(question)

            # To use Open AI Un-comment these lines
            # if output["answer"] == "No answer found":
                # output = self.openai_instance.query_data(question)
            output["sessionId"] = sessionId
            output["timestamp"] = self.current_timestamp

            memory.save_context({"input": question}, {"output": output["answer"]})
            #converting the memory to pickle to save in mysql
            bin_pickle = pickle.dumps(memory)
            if self.sessionId_exists:
                # If sessionId exists only updating the timestamp and ConversationBufferMemory
                self.mysql_instance.update_record([self.mysql_timestamp, bin_pickle, sessionId])
            else:
                self.mysql_instance.insert_data([sessionId, self.mysql_timestamp, self.mysql_timestamp, bin_pickle])
            return output
        except Exception as ex:
            logging.info("Error while running output for QnA Maker & OpenAI")
        return DEFAULT_GENERIC_OUTPUT



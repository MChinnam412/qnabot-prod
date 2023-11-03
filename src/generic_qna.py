import pickle
from datetime import datetime

from langchain.memory import ConversationBufferMemory
from starlette.config import Config

from src.__init__ import DEFAULT_GENERIC_OUTPUT, URLS
from src.azure_qna_maker import QuestionAnswering
from src.openaI_code import OpenAIQuestionAnswering
from src.utils.logger_utils import Logger
from src.utils.mysql_utils import MySQLConnection

config = Config("configs/properties.conf")

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
            # self.openai_instance = OpenAIQuestionAnswering(URLS[:1])
            # self.openai_instance.load_chain()
            self.azure_qna_maker = QuestionAnswering(config.get('AZURE_QNA_MAKER_CONFIDENCE', float, 0.5))
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
            logging.error(f"Error while checking if session exists: {ex}")
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
            logging.error(f"Error while generating timestamp: {ex}")

    def convert_to_html(self, data):
        """
        converting output from QnA Maker to html
        :param sessionId:
        :return:
        """
        try:
            data = data.strip()
            split_data = data.split("\n")
            output_data = []
            is_list = False
            for d in split_data:
                d = d.strip()
                if len(d) > 0:
                    if "* " in d:
                        # Checking for list
                        d = d.replace("*", "")
                        d = d.strip()
                        d = "<li>" + d + "</li>"
                        if not is_list:
                            # start of list
                            d = "<ul>" + d
                            is_list = True
                    elif is_list:
                        # end of list
                        output_data[-1] = output_data[-1] + "</ul>"
                        is_list = False
                    if len(d) > 0:
                        if ":" in d and ("More Information" in d or "Link" in d):
                            # checking for Source urls
                            temp = d.split(":")
                            o = f'<a href="{":".join(temp[1:]).strip()}" target="_blank"><u>{temp[0].strip()}</u></a><br><br>'
                            d = o
                        if "<" not in d:
                            d += "<br>"
                        output_data.append(d)
            output_data[-1] = output_data[-1].replace("<br>", "")
            return "".join(output_data)
        except Exception as ex:
            logging.error(f"Error while converting to html: {ex}")
        return data

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
            if output["answer"] == "No answer found":
                output["prompts"] = ["About Company", "Services Portfolio", "Case Studies", "Contact Us"]
                output["answer"] = "Kindly make a selection from the provided options"
            # if output["answer"] == "No answer found":
            # output = self.openai_instance.query_data(question)
            output["sessionId"] = sessionId
            output["timestamp"] = self.current_timestamp

            # convert the output data to html
            output["answer"] = self.convert_to_html(output["answer"])

            memory.save_context({"input": question}, {"output": output["answer"]})
            # converting the memory to pickle to save in mysql
            bin_pickle = pickle.dumps(memory)
            if self.sessionId_exists:
                # If sessionId exists only updating the timestamp and ConversationBufferMemory
                self.mysql_instance.update_record([self.mysql_timestamp, bin_pickle, sessionId])
            else:
                self.mysql_instance.insert_data([sessionId, self.mysql_timestamp, self.mysql_timestamp, bin_pickle])
            return output
        except Exception as ex:
            logging.error(f"Error while running output for QnA Maker & OpenAI: {ex}")
        return DEFAULT_GENERIC_OUTPUT

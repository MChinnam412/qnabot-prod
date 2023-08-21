import copy

from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.core.credentials import AzureKeyCredential
from starlette.config import Config

from src.__init__ import DEFAULT_OUTPUT_QnA_MAKER
from src.utils.logger_utils import Logger
import os
logger = Logger()
logging = logger.get_logger()
config = Config("configs/properties.conf")

class QuestionAnswering:
    """
    Question Answering using Azure QnA Maker API
    """
    # You should load this from config file as it's just for testing we have directly update it
    # It isn't a good practice when you scaling it as an API

    # azure endpoint
    #endpoint = config.get('AZURE_QNA_MAKER_URL', str, None)
    AZURE_QNA_MAKER_URL=os.getenv('AZURE_QNA_MAKER_URL')
    endpoint = AZURE_QNA_MAKER_URL

    # azure credentials
    #credential = AzureKeyCredential(config.get('AZURE_QNA_MAKER_CREDENTIALS', str, None))
    AZURE_QNA_MAKER_CREDENTIALS=os.getenv('AZURE_QNA_MAKER_CREDENTIALS')
    credential = AzureKeyCredential(AZURE_QNA_MAKER_CREDENTIALS)

    # project name
    #knowledge_base_project = config.get('AZURE_QNA_MAKER_KNOWLEDGE_BASE', str, None)
    AZURE_QNA_MAKER_KNOWLEDGE_BASE=os.getenv('AZURE_QNA_MAKER_KNOWLEDGE_BASE')
    knowledge_base_project = AZURE_QNA_MAKER_KNOWLEDGE_BASE


    # It's the default value
    deployment = config.get('AZURE_QNA_MAKER_DEPLOYMENT', str, None)

    # It would be updated once we connect to Azure QnAmaker API
    client = None

    # we are setting default confidence please feel free to fine-tune
    confidence = None
    
    import os
    print(f"AZURE_QNA_MAKER_URL -env:{os.getenv('AZURE_QNA_MAKER_URL')}")
    
    print(f"AZURE_QNA_MAKER_CREDENTIALS -env:{os.getenv('AZURE_QNA_MAKER_CREDENTIALS')}")
    
    print(f"AZURE_QNA_MAKER_KNOWLEDGE_BASE -env:{os.getenv('AZURE_QNA_MAKER_KNOWLEDGE_BASE')}")

    def __init__(self, confidence=0.5):
        """
        Azure client
        :param confidence:
        """
        try:
            self.client = QuestionAnsweringClient(self.endpoint, self.credential)
            self.confidence = confidence
            logging.info("Successully connected to azure qa client")
        except Exception as ex:
            logging.error(f"Error while connecting to Azure: {ex}")

    def extract_output(self, output):
        """
        Pre-processing extracted output from Azure QnAmaker API
        :param output:
        :return:
        """
        all_answers = []
        default_json = {"answer": "N/A", "prompts": [], "confidence": 0.0, "source": "N/A", "source_url": "N/A"}
        try:
            # if you want only the one with max confidence when there are multiple answers
            # max_confidence = self.confidence
            for answer in output.answers:
                if answer.confidence >= self.confidence:
                    # creating a copy so they aren't using same variable
                    temp_json = copy.deepcopy(default_json)

                    temp_json["answer"] = str(answer.answer).strip()
                    temp_json["confidence"] = answer.confidence
                    temp_json["source"] = answer.metadata.get("source", "N/A")
                    temp_json["source_url"] = answer.metadata.get("source_url", "N/A")
                    if temp_json["source_url"] != "N/A":
                        temp_json["source_url"] = temp_json["source_url"].replace("_com", ".com").replace("@", "/")
                    # Checking if you have any prompts
                    prompt_output = answer.dialog.prompts
                    if len(prompt_output) > 0:
                        temp_answer = ""
                        for prompt in prompt_output:

                            # appending points wrt header wrt streamlit to make it better on UI
                            temp_answer = str(prompt.display_text).strip()
                            if len(temp_answer) > 0:
                                ## If no prompt output don't append it to the final answer
                                temp_json["prompts"].append(temp_answer)
                    all_answers.append(temp_json)
            logging.info("Successfully extracted output\n")
            return all_answers
        except Exception as ex:
            logging.error(f"Error while extracting output: {ex}")
        return all_answers

    def get_output(self, question):
        """
        Retrieving the output of a question
        :param question:
        :return:
        """
        final_answer = copy.deepcopy(DEFAULT_OUTPUT_QnA_MAKER)
        try:
            if self.client is None:
                final_answer["answer"] = "Error while connecting to Azure bot"
                return final_answer
            if type(question) != str:
                final_answer["answer"] = "Enter a valid intput"
                return final_answer
            question = question.strip()
            if len(question) == 0:
                final_answer["answer"] = "enter a valid input"
                return final_answer
            output = self.client.get_answers(
                question=question,
                project_name=self.knowledge_base_project,
                deployment_name=self.deployment
            )
            logging.info("Successfully retrieved output from azure environment")
            all_answers = self.extract_output(output)
            max_conf = -1
            if all_answers:
                for answer in all_answers:
                    if answer["confidence"] > max_conf:
                        max_conf = answer["confidence"]
                        final_answer = answer
                    elif answer["confidence"] == max_conf and answer["source"] == "service":
                        final_answer = answer
            return final_answer
        except Exception as ex:
            logging.error(f"Error getting accessing answer: {ex}")
        return final_answer


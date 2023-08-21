"""
querying chroma db
# for chromadb installation export HNSWLIB_NO_NATIVE=1
"""
import copy
import json
import os
import time

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import url_selenium, WebBaseLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from starlette.config import Config

from src.__init__ import template, DEFAULT_OUTPUT_OpenAI
from src.utils.logger_utils import Logger

logger = Logger()
logging = logger.get_logger()
config = Config("configs/properties.conf")


class OpenAIQuestionAnswering:
    """
    OpenAI Question Answering description
    """
    OPENAI_API_KEY = None
    urls = []
    all_documents = []
    embeddings = None
    chain = None
    db = None
    prompt = None

    def __init__(self, urls=[]):
        """
        setting OpenAI environment variables
        :param urls:
        """
        try:
            self.OPENAI_API_KEY = config.get('OPENAI_API_KEY', str, None)
            os.environ["OPENAI_API_KEY"] = self.OPENAI_API_KEY
            self.urls = urls
            self.embeddings = OpenAIEmbeddings()
            self.prompt = PromptTemplate(template=template, input_variables=["context", "question"])
            logging.info("Successfully initialized OpenAI Key Environment variable")
        except Exception as ex:
            logging.error(f"Error while setting OpenAI Key Environment variable: {ex}")
        return

    def load_urls(self):
        """
        loading the data using document loaders
        ref: https://python.langchain.com/docs/integrations/document_loaders/url
        :return:
        """
        try:
            if len(self.urls) == 0:
                logging.info("No urls available")
                return
            case_studies_exists = False
            case_studies_url = "http://fissionlabs.com/case-studies"
            if case_studies_url in self.urls:
                self.urls.remove(case_studies_url)
                case_studies_exists = True
            if len(self.urls) > 0:
                loader = url_selenium.SeleniumURLLoader(urls=self.urls)
                self.all_documents.extend(copy.deepcopy(loader.load()))
            if case_studies_exists:
                loader = WebBaseLoader(urls=self.urls)
                self.all_documents.extend(copy.deepcopy(loader.load()))
                self.urls.append(case_studies_url)
            logging.info(f"Successfully data: {len(self.all_documents)}")
        except Exception as ex:
            logging.error(f"Error while loading data: {ex}")
        return

    def load_chromadb(self):
        """
        loading chroma db on-time
        :return:
        """
        try:
            start = time.time()
            if self.urls and not self.all_documents:
                self.load_urls()
                logging.info(f"Time taken to load data documents from urls: {time.time() - start}")
                start = time.time()
            if self.all_documents:
                self.db = Chroma.from_documents(self.all_documents, self.embeddings)
                logging.info(f"Time taken to load data documents in chromdb: {time.time() - start}")
            else:
                logging.info(f"There are no documents")
        except Exception as ex:
            logging.error(f"Error while loading chromdb: {ex}")

    def load_chain(self):
        """
        loading data and embedding to chromadb
        :return:
        """
        try:
            start = time.time()
            if self.urls and not self.all_documents:
                self.load_urls()
                logging.info(f"time taken to load data documents from urls: {time.time() - start}")
                start = time.time()
            if len(self.all_documents) == 0:
                logging.info(f"we don't have any documents to connect to openai")
                return
            if self.db is None:
                self.load_chromadb()
            chain_type_kwargs = {"prompt": self.prompt}
            self.chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(temperature=0),
                chain_type="stuff",
                retriever=self.db.as_retriever(),
                chain_type_kwargs=chain_type_kwargs,
            )
            logging.info("Successfully loaded data to chromadb and connected to langchain")
            logging.info(f"time taken to create chroma db and chain: {time.time() - start} seconds")
        except Exception as ex:
            logging.error(f"Error while loading ConversationBufferMemory, RetrievalQA  or connecting to OpenAI: {ex}")
        return

    def query_data(self, query):
        """
        Querying on the input chain
        :param query:
        :return:
        """
        final_output = copy.deepcopy(DEFAULT_OUTPUT_OpenAI)
        try:
            start = time.time()
            if self.urls == 0:
                logging.info("No urls exists")
                return final_output
            if self.all_documents == 0:
                logging.info("Not able to load document using langchain Selenium loader")
                return final_output
            if self.db is None:
                logging.info("Error while creating chromadb database")
                return
            if self.chain is None:
                logging.info("Not able to connect to OpenAI")
                return final_output
            response = self.chain.run(query)
            output = json.loads(response)
            if output["confidence_score"]<0.7:
                output["answer"] = "No answer found"
            output["confidence"] = 1.0
            output["prompts"] = []
            output["source"] = "OpenAI"
            if "source_url" not in output or output.get("source_url", "") == "":
                return final_output
            logging.info(f"time taken to run query on all documents using OpenAI: {time.time() - start}")
            return output
        except Exception as ex:
            logging.error(f"Error while querying the data check you OpenAI key: {ex}")
        return final_output

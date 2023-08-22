"""
main method for starting the rest-api
# for chromadb installation export HNSWLIB_NO_NATIVE=1
"""
import copy
import os
import uvicorn
from fastapi import FastAPI
from starlette.config import Config
from fastapi.middleware.cors import CORSMiddleware
from __init__ import DEFAULT_OUTPUT
from src.generic_qna import GenericQnaAnswering
from src.source_data import InputRequest
from src.utils.logger_utils import Logger

config = Config("configs/properties.conf")
log = Logger()
logging = log.get_logger()

generic_qna = GenericQnaAnswering()

app = FastAPI()
origins=["*"]
app.add_middleware(CORSMiddleware,allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],allow_headers=["*"])

# DEFAULT_OUTPUT = {"status":"200","message":"success", "sessionId": None, "question": None,"answer": "Not Found",
#                   "prompts": [], "confidence":1.0, "source_url": "N/A", "source":None, "timestamp": None}

@app.get("/")
async def check_service():
    """
    Checking if service is up and running
    :return:
    """
    logging.info("Checking if service is up and running")
    return {"status": 200, "message": "New Service is up and running"}


@app.post("/question_answering")
async def question_answering(request: InputRequest):
    """
    Question answering using Azure QnA Maker API
    :param request:
    :return:
    """
    output = copy.deepcopy(DEFAULT_OUTPUT)
    try:
        if request.session_id is not None:
            output["session_id"] = request.session_id
        if request.question is not None and len((request.question).strip()) > 1:
            output["question"] = request.question
            request.question = request.question.strip()
            final_output = generic_qna.get_answer(request.session_id, request.question)
            if len(final_output) > 0:
                for key, val in final_output.items():
                    output[key] = val
        else:
            output["message"] = "Please enter some question?"
        logging.info("Question answering using Azure QnA Maker API")
        return output
    except Exception as ex:
        output['status'] = 400
        output['message'] = f"Error while processing input: {ex}"
        logging.error(f"Error please give valid input: {ex}")
        return output


# if __name__ == "__main__":
#     uvicorn.run(app, host=config.get("HOST", str, default="0.0.0.0"), port=config.get("PORT", int, default=8000),
#                 workers=config.get("WORKERS", int, default=1))

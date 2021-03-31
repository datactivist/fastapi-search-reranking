import os
import json
import numpy as np
from enum import Enum

import reranking
import sqlQuery

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional

model_list = {}


class Add_Search_Query(BaseModel):

    conversation_id: str
    user_search: str
    date: str

    class Config:
        schema_extra = {
            "example": {
                "conversation_id": "51ad8b6a-6924-4c79-a22b-de013e5fe25e",
                "user_search": "barrage électrique",
                "date": "2021-03-16 14:31:18",
            }
        }


class Feedback(int, Enum):
    chosen = 1
    notchosen = -1
    unknown = 0


class Result_Feedback(BaseModel):

    result_url: str
    result_title: str
    feedback: Feedback


class Add_Result_Feedback_Query(BaseModel):

    conversation_id: str
    user_search: str
    data: List[Result_Feedback]

    class Config:
        schema_extra = {
            "example": {
                "conversation_id": "51ad8b6a-6924-4c79-a22b-de013e5fe25e",
                "user_search": "barrage électrique",
                "data": [
                    {
                        "result_url": "syncb021eba-fr-120066022-jdd-627db3a0-9448-4631-81b9-2f13f67b8557",
                        "result_title": "Usines hydroélectriques concédées en Provence Alpes Côte d'Azur",
                        "feedback": 1,
                    },
                    {
                        "result_url": "sync9c8f975-fr-120066022-jdd-fb022239-2083-4d31-9fc0-369117139336",
                        "result_title": "Enveloppes Approchées d'Inondations Potentielles des cours d'eau de Provence-Alpes-Côte d'Azur",
                        "feedback": -1,
                    },
                    {
                        "result_url": "sync8ff00ed-fr-120066022-jdd-f8590eb7-286a-4d7f-b5f2-6246ba0c6485",
                        "result_title": "Tronçons de cours d'eau court-circuités en Provence Alpes Côte d'Azur",
                        "feedback": -1,
                    },
                    {
                        "result_url": "sync970f901-fr-120066022-jdd-58e01586-f290-42ee-940e-dbeece6a1d39",
                        "result_title": "Ouvrages de retenue d'eau en Provence Alpes Côte d'Azur",
                        "feedback": 1,
                    },
                ],
            }
        }


class Search_Reranking_Query(BaseModel):

    """
    Structure for the reranking query
    """

    # TODO

    pass


class ResultList(BaseModel):

    """
    Structure for reranking query's results
    """

    # TODO

    pass


# Launch API
app = FastAPI()


@app.post("/search_reranking", response_model=List[ResultList])
async def manage_query_reranking(query: Search_Reranking_Query):

    # TODO

    return []


@app.post("/add_search")
async def add_search(search: Add_Search_Query):
    """
    ## Function
    Store user search
    ## Parameter
    ### Required
    - **conversation_id**: Rasa ID of the conversation
    - **user_search**: search terms entered by the user
    - **date**: date of the search [yy-mm-dd hh:mm:ss]
    """

    sqlQuery.add_new_search_query(
        search.conversation_id, search.user_search, search.date, True
    )


@app.post("/add_feedback")
async def add_results_feedback(feedbacks: Add_Result_Feedback_Query):
    """
    ## Function
    Store user feedbacks of the results
    ## Parameter
    ### Required
    - **user_search**: Search of the user
    - **data**: List of results for that search and their feedback
        - **result_url**: url of the result
        - **result_title**: title of the result
        - **feedback**: Feedback of the user
    """

    for feedback in feedbacks.data:
        sqlQuery.add_proposed_result_feedback(
            feedbacks.conversation_id,
            feedbacks.user_search,
            feedback.result_url,
            feedback.result_title,
            feedback.feedback,
            True,
        )


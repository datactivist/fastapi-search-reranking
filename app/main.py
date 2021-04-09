import os
import json
import numpy as np
from enum import Enum

import reranking
import sql_query

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


class Group(BaseModel):

    name: str
    description: Optional[str]


class Result(BaseModel):

    title: str
    url: str
    description: str
    owner_org: Optional[str]
    owner_org_description: Optional[str]
    maintainer: Optional[str]
    dataset_publication_date: Optional[str]
    dataset_modification_date: Optional[str]
    metadata_creation_date: Optional[str]
    metadata_modification_date: Optional[str]
    tags: Optional[List[str]]
    groups: Optional[List[Group]]


class Result_Feedback(BaseModel):

    result: Result
    feedback: Feedback


class Add_Result_Feedback_Query(BaseModel):

    conversation_id: str
    user_search: str
    feedbacks_list: List[Result_Feedback]

    class Config:
        schema_extra = {
            "example": {
                "conversation_id": "51ad8b6a-6924-4c79-a22b-de013e5fe25e",
                "user_search": "barrage électrique",
                "feedbacks_list": [
                    {
                        "result": {
                            "title": "Usines hydroélectriques concédées en Provence Alpes Côte d'Azur",
                            "url": "syncb021eba-fr-120066022-jdd-627db3a0-9448-4631-81b9-2f13f67b8557",
                            "description": "Description 1",
                        },
                        "feedback": 1,
                    },
                    {
                        "result": {
                            "title": "Enveloppes Approchées d'Inondations Potentielles des cours d'eau de Provence-Alpes-Côte d'Azur",
                            "url": "sync9c8f975-fr-120066022-jdd-fb022239-2083-4d31-9fc0-369117139336",
                            "description": "Description 2",
                        },
                        "feedback": -1,
                    },
                    {
                        "result": {
                            "title": "Tronçons de cours d'eau court-circuités en Provence Alpes Côte d'Azur",
                            "url": "sync8ff00ed-fr-120066022-jdd-f8590eb7-286a-4d7f-b5f2-6246ba0c6485",
                            "description": "Description 3",
                        },
                        "feedback": -1,
                    },
                    {
                        "result": {
                            "title": "Ouvrages de retenue d'eau en Provence Alpes Côte d'Azur",
                            "url": "sync970f901-fr-120066022-jdd-58e01586-f290-42ee-940e-dbeece6a1d39",
                            "description": "Description 4",
                        },
                        "feedback": 1,
                    },
                ],
            }
        }


class API_Hostname(str, Enum):
    datasud = "datasud"
    others = "Other"


class Results_List(BaseModel):

    api_hostname: API_Hostname
    results_list: List[Result]


class Search_Reranking_Query(BaseModel):

    """
    Structure for the reranking query
    """

    data: List[Results_List]
    conversation_id: str
    user_search: str
    use_feedback: Optional[bool] = True
    use_metadata: Optional[bool] = False

    class Config:
        schema_extra = {
            "example": {
                "conversation_id": "51ad8b6a-6924-4c79-a22b-de013e5fe25e",
                "user_search": "barrage électrique",
                "data": [
                    {
                        "api_hostname": "datasud",
                        "results_list": [
                            {
                                "title": "Usines hydroélectriques concédées en Provence Alpes Côte d'Azur",
                                "url": "syncb021eba-fr-120066022-jdd-627db3a0-9448-4631-81b9-2f13f67b8557",
                                "description": "Description 1",
                                "tags": ["tag1", "tag2", "tag3"],
                                "groups": [
                                    {
                                        "name": "group1",
                                        "description": "group_description1",
                                    },
                                    {
                                        "name": "group2",
                                        "description": "group_description2",
                                    },
                                ],
                            },
                            {
                                "title": "Enveloppes Approchées d'Inondations Potentielles des cours d'eau de Provence-Alpes-Côte d'Azur",
                                "url": "sync9c8f975-fr-120066022-jdd-fb022239-2083-4d31-9fc0-369117139336",
                                "description": "Description 2",
                            },
                            {
                                "title": "Tronçons de cours d'eau court-circuités en Provence Alpes Côte d'Azur",
                                "url": "sync8ff00ed-fr-120066022-jdd-f8590eb7-286a-4d7f-b5f2-6246ba0c6485",
                                "description": "Description 3",
                                "tags": ["tag1", "tag3", "tag4"],
                            },
                            {
                                "title": "Ouvrages de retenue d'eau en Provence Alpes Côte d'Azur",
                                "url": "sync970f901-fr-120066022-jdd-58e01586-f290-42ee-940e-dbeece6a1d39",
                                "description": "Description 4",
                            },
                        ],
                    }
                ],
            }
        }


# Launch API
app = FastAPI()


@app.post("/search_reranking", response_model=List[Result])
async def manage_query_reranking(query: Search_Reranking_Query):

    """
    ## Function
    Take the results of one or multiple searches and rerank the results
    
    ### Required parameters
    - **conversation_id**: rasa id of the conversation
    - **user_search**: search of the user
    - **data**: list of results_list
    - A **result list** is comprised of the API hostname from which the results have been gathered, and the list of results
    - A **result** has 3 required attributes:
        - **title**: title of the result
        - **url**: url of the result
        - **description**: description of the result
    - A **result** can have these optional attributes, defaulted to empty:
        - **owner_org**: organization that created the datased
        - **owner_org_description**: a description of that organization
        - **maintainer**: organization maintaining the dataset
        - **dataset_publication_date**: date of publication of the dataset
        - **dataset_modification_date**: date of last modification of the dataset
        - **metadata_creation_date**: date of creation of the metadatas
        - **metadata_modification_date**: date of last modification of the metadatas
        - **tags**: list of strings for each tag
        - **groups**: list of group
            - A **group** must have a **name** attribute as string, and optionally a **description**
    
    ### Optional parameters
    - **use_feedback**: if True, use feedback for reranking, default to True
    - **use_metadata**: if True, do nothing for now, default to False
    """

    output_data = reranking.rerank_results(
        query.conversation_id,
        query.user_search,
        query.data,
        query.use_feedback,
        query.use_metadata,
    )

    return output_data


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

    sql_query.add_new_search_query(
        search.conversation_id, search.user_search, search.date
    )


@app.post("/add_feedback")
async def add_results_feedback(feedbacks: Add_Result_Feedback_Query):
    """
    ## Function
    Store user feedbacks of the results
    ## Parameter
    ### Required
    - **user_search**: Search of the user
    - **feedbacks_list**: List of results_feedback
    - A **results_feedback** has two attributes:
        - **feedback**: Feedback of the user with value -1, 0, or 1
        - A **result** with 3 required attributes:
            - **title**: title of the result
            - **url**: url of the result
            - **description**: description of the result
        - A **result** can have these optional attributes, defaulted to empty:
            - **owner_org**: organization that created the datased
            - **owner_org_description**: a description of that organization
            - **maintainer**: organization maintaining the dataset
            - **dataset_publication_date**: date of publication of the dataset
            - **dataset_modification_date**: date of last modification of the dataset
            - **metadata_creation_date**: date of creation of the metadatas
            - **metadata_modification_date**: date of last modification of the metadatas
            - **tags**: list of strings for each tag
            - **groups**: list of group
                - A **group** must have a **name** attribute as string, and optionally a **description**
    """

    sql_query.update_proposed_result_feedback(
        feedbacks.conversation_id, feedbacks.user_search, feedbacks.feedbacks_list
    )


import json
import numpy as np
from enum import Enum
from pathlib import Path

import sqlQuery

data_path = Path("data")


def compute_feedback_score(conversation_id, user_search, result_url):

    """
    Compute the feedback score

    Input:  conversation_id: id of the conversation
            user_search: keyword entered by the user
            result_url: proposed result to the user

    Output: Feedback score, default value to -1 if no feedbacks available
    """

    # get feedback for that particular search_id -> result_url sequence (TODO: check for similar search?)
    feedbacks = sqlQuery.get_feedback_for_reranking(
        conversation_id, user_search, result_url
    )

    if len(feedbacks) > 0:
        # Normalize mean of all feedbacks (-1->1 to 0->1)
        feedback_score = (np.mean(feedbacks) - (-1)) / (1 - (-1))
    else:
        # Default value if no feedbacks available
        feedback_score = -1

    return feedback_score


def use_feedback(conversation_id, user_search, result_url_list):

    """
    Get feedback score for each result url in url_list

    Input:  conversation_id: id of the conversation
            user_search: keyword entered by the user
            result_url_list: list of proposed result to the user

    Output: list of tupe, (result_url, feedback_score)
    """

    new_list = []

    for result_url in result_url_list:

        feedback_score = compute_feedback_score(
            conversation_id, user_search, result_url
        )

        new_list.append((result_url, new_sim))

    return new_list


def sort_array_of_tuple_with_second_value(array):

    """
    Return an array of tuple sorted by second key values
    """

    array.sort(key=second_key_from_tuple, reverse=True)

    return array


def remove_second_key_from_array_of_tuple(array):

    return [array[i][0] for i in range(len(array))]

import json
import numpy as np
from enum import Enum
from pathlib import Path

import sql_query

data_path = Path("data")


def second_key_from_tuple(tuple):
    """
    Return second value of a tuple, used for sorting array of dimension [n, 2] on the second value
    """

    return tuple[1]


def sort_array_of_tuple_with_second_value(array):

    """
    Return an array of tuple sorted by second key values
    """

    array.sort(key=second_key_from_tuple, reverse=True)

    return array


def remove_second_key_from_array_of_tuple(array):

    return [array[i][0] for i in range(len(array))]


def compute_feedback_score(conversation_id, user_search, result):

    """
    Compute the feedback score

    Input:  conversation_id: id of the conversation
            user_search: keyword entered by the user
            result: proposed result to the user

    Output: Feedback score, default value to 0 if no feedbacks available
    """

    # get feedback for that particular search_id -> result_url sequence (TODO: check for similar search?)

    feedbacks = sql_query.get_feedback_for_reranking(user_search, result)

    if feedbacks != None and len(feedbacks) > 0:
        # Normalize mean of all feedbacks (-1->1 to 0->1)
        feedback_score = (np.mean(feedbacks) - (-1)) / (1 - (-1))
    else:
        # Default value if no feedbacks available
        feedback_score = 0

    return feedback_score


def add_feedback_score_to_results(conversation_id, user_search, results_list):

    """
    Get feedback score for each result in result_list

    Input:  conversation_id: id of the conversation
            user_search: keyword entered by the user
            results_list: list of proposed result to the user

    Output: list of type ((result_url, result_title), feedback_score)
    """

    new_list = []

    for result in results_list:

        feedback_score = compute_feedback_score(conversation_id, user_search, result)

        print(feedback_score, result.title)

        new_list.append((result, feedback_score))

    return new_list


def add_reranking_to_db(
    conversation_id, user_search, data, final_data, flag_feedback, flag_metadata
):

    methods_used = ""
    if flag_feedback:
        methods_used += "feedback"
    if flag_metadata:
        methods_used += " metadata"

    for i, result in enumerate(final_data):

        old_rank = 0

        for j, old_result in enumerate(data):

            if result == old_result:

                old_rank = j

        sql_query.add_proposed_result(
            conversation_id=conversation_id,
            search=user_search,
            result=result,
            feedback=0,
            old_rank=old_rank,
            new_rank=i,
            methods_used=methods_used,
        )


def rerank_results(conversation_id, user_search, data, use_feedback, use_metadata):

    feedback_data = []

    flag_feedback = 0
    flag_metadata = 0

    if use_feedback:

        flag_feedback = 1

        for result_list in data:

            if (
                result_list.api_hostname == "datasud"
            ):  # TODO Gérer plusieurs listes de résultats en entrée

                feedback_data = add_feedback_score_to_results(
                    conversation_id, user_search, result_list.results_list
                )
                feedback_data = sort_array_of_tuple_with_second_value(feedback_data)
                feedback_data = remove_second_key_from_array_of_tuple(feedback_data)

    else:

        feedback_data = data

    if use_metadata:

        flag_metadata = 1

        final_data = feedback_data  # TODO Gérer d'autre méthode de reranking

    else:

        final_data = feedback_data

    add_reranking_to_db(
        conversation_id,
        user_search,
        data[0].results_list,
        final_data,
        flag_feedback,
        flag_metadata,
    )

    return final_data

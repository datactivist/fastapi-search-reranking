import sqlite3
import numpy as np

# TODO Tags / Groups

database = "data/user_reranking_feedback.db"

attributes = [
    "title",
    "url",
    "description",
    "owner_org",
    "owner_org_description",
    "maintainer",
    "dataset_publication_date",
    "dataset_modification_date",
    "metadata_creation_date",
    "metadata_modification_date",
]

# Parameter: Database pointer, sql command, and the data used for the command
# Function: Run the sql command
def run_sql_command(cursor, sql_command, data):

    try:
        if data is not None:
            cursor.execute(sql_command, data)
        else:
            cursor.execute(sql_command)

        record = cursor.fetchall()

        return record

    except sqlite3.Error as error:

        for param in data:
            if type(param) == str:
                sql_command = sql_command.replace("?", '"' + str(param) + '"', 1)
            else:
                sql_command = sql_command.replace("?", str(param), 1)

        print(
            "\nError while running this command: \n",
            sql_command,
            "\n",
            error,
            "\nData: ",
            data,
            "\n",
        )
        return None


def get_tags_id(cursor, tags):

    """
    Input:  cursor: connection to database
            tags: list of string

    Output: list of ID of each tag from database
    """

    return None


def get_groups_id(cursor, groups):

    """
    Input:  cursor: connection to database
            groups: list of string

    Output: list of ID of each tag from database
    """

    return None


def build_query_data(result):

    """
    Input:  result: object of type main.result

    Output: result in the form of a list of parameters for an SQL query
    """

    params = []

    for attribute in result:
        # tags and groups are added separately
        if attribute[0] != "tags" and attribute[0] != "groups":
            params.append(attribute[1])

    return params


def build_query_where(result):

    """
    Input:  result: object of type main.result

    Output: string with the format attribute1 = ? AND attribute2 = ? etc...
    """

    str_query = ""

    for attribute in result:
        # tags and groups are not checked
        if attribute[0] != "tags" and attribute[0] != "groups":
            if attribute[1] == None:
                str_query += " " + attribute[0] + " IS NULL AND"
            elif type(attribute[1]) == str:
                str_query += " " + attribute[0] + ' = "' + attribute[1] + '" AND'
            else:
                str_query += " " + attribute[0] + " = " + attribute[1] + " AND"

    return str_query[: len(str_query) - 4]


def add_new_result_to_DB(cursor, result):

    """
    Add result in the database

    Input:  cursor: connection to database
            result: object of type main.Result

    Output: ID of the newly created result
    """

    attribute_query = "(" + ", ".join(attributes) + ")"
    value_query = "(" + "?, " * (len(attributes) - 1) + "?)"
    sqlite_add_result_to_db_query = (
        "INSERT INTO result" + attribute_query + " VALUES" + value_query + ";"
    )

    data = build_query_data(result)

    record = run_sql_command(cursor, sqlite_add_result_to_db_query, data)

    print(record)

    return record


def get_result_ID(cursor, result):

    """
    Input:  cursor: connection to database
            result: object of type main.Result
    
    Output: ID of the result if it exist in the database, or create a new entry and return the new ID
    """

    sqlite_get_result_ID_query = (
        "SELECT id FROM result WHERE" + build_query_where(result) + ";"
    )

    record = run_sql_command(cursor, sqlite_get_result_ID_query, None)

    test = sqlite_get_result_ID_query

    if record != None and len(record) > 0:
        return record[0][0]

    add_new_result_to_DB(cursor, result)

    data = build_query_data(result)

    return run_sql_command(cursor, sqlite_get_result_ID_query, data)


# Function: Add a new search entry in the database
def add_new_search_query(conversation_id, user_search, date):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        sqlite_insert_search_query = (
            "INSERT INTO search(conversation_id, user_search, date) VALUES(?, ?, ?);"
        )
        run_sql_command(
            cursor, sqlite_insert_search_query, (conversation_id, user_search, date),
        )

        sqliteConnection.commit()

        cursor.close()
        sqliteConnection.close()

    except sqlite3.Error as error:
        print("-ADD_NEW_SEARCH_QUERY-\nError while connecting to sqlite", error, "\n")


# Function: Add the proposed result in the database
def add_proposed_result(
    conversation_id, search, result, feedback, old_rank, new_rank, methods_used,
):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_id = get_search_id_from_conv_id_and_search(
            cursor, conversation_id, search
        )

        if search_id is not None:

            result_id = get_result_ID(cursor, result)

            if result_id is not None:

                check_reranking_entry_exist_already = "SELECT id from search_reranking_feedback WHERE search_id = ? AND result_id = ?;"

                record = run_sql_command(
                    cursor, check_reranking_entry_exist_already, (search_id, result_id)
                )

                if record is not None and len(record) > 0:
                    return

                else:

                    sqlite_insert_result_feedback_query = "INSERT INTO search_reranking_feedback(search_id, old_rank, new_rank, result_id, feedback, methods_used) VALUES(?, ?, ?, ?, ?, ?);"

                    run_sql_command(
                        cursor,
                        sqlite_insert_result_feedback_query,
                        (
                            search_id,
                            old_rank,
                            new_rank,
                            result_id,
                            feedback,
                            methods_used,
                        ),
                    )

            sqliteConnection.commit()

        cursor.close()
        sqliteConnection.close()

    except sqlite3.Error as error:
        print("-ADD_FEEDBACK_RESULT\nError while connecting to sqlite", error, "\n")


# Function: Update the proposed result feedback in the database
def update_proposed_result_feedback(conversation_id, search, feedbacks_list):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_id = get_search_id_from_conv_id_and_search(
            cursor, conversation_id, search
        )

        if search_id is not None:

            for fback in feedbacks_list:

                result_id = get_result_ID(cursor, fback.result)

                if result_id is not None:

                    sqlite_update_result_query = "UPDATE search_reranking_feedback SET feedback = ? WHERE search_id = ? AND result_id = ?"

                    run_sql_command(
                        cursor,
                        sqlite_update_result_query,
                        (fback.feedback, search_id, result_id),
                    )

            sqliteConnection.commit()

        cursor.close()
        sqliteConnection.close()

    except sqlite3.Error as error:
        print("-ADD_FEEDBACK_RESULT\nError while connecting to sqlite", error, "\n")


# Return the search_id corresponding to these parameters
def get_search_id_from_conv_id_and_search(cursor, conversation_id, user_search):

    try:

        sqlite_get_search_id_query = "SELECT id FROM search where conversation_id = ? and user_search = ? ORDER BY id DESC;"

        record = run_sql_command(
            cursor, sqlite_get_search_id_query, (conversation_id, user_search)
        )

        if record != None and len(record) > 0:
            return record[0][0]
        else:
            return None

    except sqlite3.Error as error:
        print("-GET_SEARCH_ID-\nError while connecting to sqlite", error, "\n")


def get_search_ids_from_search(cursor, user_search):

    try:

        sqlite_get_search_id_query = (
            "SELECT id FROM search where user_search = ? ORDER BY id DESC;"
        )

        record = run_sql_command(cursor, sqlite_get_search_id_query, [user_search])

        if record != None and len(record) > 0:
            search_ids = []
            for search_id in record:
                search_ids.append(search_id[0])
            return search_ids
        else:
            return None

    except sqlite3.Error as error:
        print("-GET_SEARCH_ID-\nError while connecting to sqlite", error, "\n")


def get_feedback_for_reranking(user_search, result):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_ids = get_search_ids_from_search(cursor, user_search)

        print("search_ids", search_ids)

        if search_ids != None and len(search_ids) > 0:

            result_id = get_result_ID(cursor, result)

            sqlite_get_feedback_query = "SELECT feedback FROM search_reranking_feedback where search_id IN ({}) and result_id = ?;".format(
                ", ".join(["?"] * len(search_ids))
            )

            return run_sql_command(
                cursor, sqlite_get_feedback_query, search_ids + [result_id]
            )

        else:

            return []

    except sqlite3.Error as error:
        print("-GET_FEEDBACK-\nError while connecting to sqlite", error, "\n")

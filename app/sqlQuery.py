import sqlite3
import numpy as np

database = "data/user_reranking_feedback.db"

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
        print(
            "\nError while running this command: \n",
            sql_command,
            "\n",
            data,
            "\n",
            error,
            "\n",
        )
        return None


def check_proposed_result_already_exist(cursor, search_id, result_url):

    sqlite_check_proposed_result_exist_query = "SELECT id FROM search_reranking_feedback WHERE search_id = ? and result_url = ?"

    record = run_sql_command(
        cursor, sqlite_check_proposed_result_exist_query, (search_id, result_url),
    )

    return record


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
    conversation_id,
    search,
    result_url,
    result_title,
    feedback,
    old_rank,
    new_rank,
    flag_feedback,
    flag_metadata,
):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_id = get_search_id_from_conv_id_and_search(
            cursor, conversation_id, search
        )

        if search_id is not None:

            record = check_proposed_result_already_exist(cursor, search_id, result_url)

            if not len(record) > 0:

                sqlite_insert_result_query = "INSERT INTO search_reranking_feedback(search_id, old_rank, new_rank, result_url, result_title, feedback, feedbacks_used, metadatas_used) VALUES(?, ?, ?, ?, ?, ?, ?, ?);"

                run_sql_command(
                    cursor,
                    sqlite_insert_result_query,
                    (
                        search_id,
                        old_rank,
                        new_rank,
                        result_url,
                        result_title,
                        feedback,
                        flag_feedback,
                        flag_metadata,
                    ),
                )

                sqliteConnection.commit()

        cursor.close()
        sqliteConnection.close()

    except sqlite3.Error as error:
        print("-ADD_FEEDBACK_RESULT\nError while connecting to sqlite", error, "\n")


# Function: Update the proposed result feedback in the database
def update_proposed_result_feedback(
    conversation_id, search, result_url, result_title, feedback,
):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_id = get_search_id_from_conv_id_and_search(
            cursor, conversation_id, search
        )

        if search_id is not None:

            record = check_proposed_result_already_exist(cursor, search_id, result_url)

            if len(record) > 0:

                sqlite_update_result_query = (
                    "UPDATE search_reranking_feedback SET feedback = ? WHERE id = ?"
                )

                run_sql_command(
                    cursor, sqlite_update_result_query, (feedback, record[0][0])
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


def get_feedback_for_reranking(user_search, result_url):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_ids = get_search_ids_from_search(cursor, user_search)

        if search_ids != None and len(search_ids) > 0:

            sqlite_get_feedback_query = "SELECT feedback FROM search_reranking_feedback where search_id IN ({}) and result_url = ?;".format(
                ", ".join(["?"] * len(search_ids))
            )

            return run_sql_command(
                cursor, sqlite_get_feedback_query, search_ids + [result_url]
            )

        else:

            return []

    except sqlite3.Error as error:
        print("-GET_FEEDBACK-\nError while connecting to sqlite", error, "\n")

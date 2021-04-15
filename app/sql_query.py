import sqlite3
import numpy as np

# TODO Tags / Groups

database = "data/user_reranking_feedback.db"

attributes = [
    "title",
    "url",
    "description",
    "portail",
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

        if data is not None:
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


def add_new_tag(cursor, tag, portail):

    """
    Add a new tag to the table result_tag

    Input:  cursor: connection to database
            tag: string

    Output: return newly created tag's id
    """

    sqlite_add_tag_query = "INSERT INTO result_tag(name, portail) VALUES (?, ?);"

    run_sql_command(cursor, sqlite_add_tag_query, (tag, portail))
    return get_tag_id(cursor, tag, portail)


def get_tag_id(cursor, tag, portail=None):

    """
    Input:  cursor: connection to database
            tag: string

    Output: return db ID of the tag in input
            return None if tag not found
    """

    if portail is not None:
        sqlite_get_tag_id_query = (
            "SELECT id FROM result_tag WHERE name = ? and portail = ?;"
        )
        tag_id = run_sql_command(cursor, sqlite_get_tag_id_query, [tag, portail])
    else:
        sqlite_get_tag_id_query = "SELECT id FROM result_tag WHERE name = ?;"
        tag_id = run_sql_command(cursor, sqlite_get_tag_id_query, [tag])

    if tag_id is not None and len(tag_id) > 0:
        return tag_id[0][0]
    return None


def get_result_tags_ids(cursor, result_id):

    """
    Input:  cursor: connection to database
            result_id: id of the result in the db

    Output: return IDs of every tags linked to the result
    """

    sqlite_get_tags_ids_query = (
        "SELECT tag_id FROM link_results_tags WHERE result_id = ?;"
    )

    tags_ids = run_sql_command(cursor, sqlite_get_tags_ids_query, [result_id])

    if tags_ids is not None and len(tags_ids) > 0:
        output_list = []
        for tag_id in tags_ids:
            output_list.append(tag_id[0])
        return output_list
    else:
        return None


def add_new_tag_result_link(cursor, result_id, tag, portail):

    tag_id = get_tag_id(cursor, tag, portail)

    if tag_id is None:
        tag_id = add_new_tag(cursor, tag, portail)

    sql_check_add_tag_result_exist_query = (
        "SELECT result_id FROM link_results_tags WHERE result_id = ? AND tag_id = ?;"
    )

    link_id = run_sql_command(
        cursor, sql_check_add_tag_result_exist_query, (result_id, tag_id)
    )

    if link_id is not None and len(link_id) > 0:
        return

    sql_add_tag_result_link_query = (
        "INSERT INTO link_results_tags(result_id, tag_id) VALUES(?, ?);"
    )

    run_sql_command(cursor, sql_add_tag_result_link_query, (result_id, tag_id))


def add_new_group(cursor, group, portail):

    """
    Add a new group to the table result_group

    Input:  cursor: connection to database
            group: object of type main.group

    Output: return newly created group's id
    """

    sqlite_add_group_query = (
        "INSERT INTO result_group(name, description, portail) VALUES (?, ?, ?);"
    )

    run_sql_command(
        cursor, sqlite_add_group_query, [group.name, group.description, portail]
    )
    return get_group_id(cursor, group, portail)


def get_group_id(cursor, group, portail=None):

    """
    Input:  cursor: connection to database
            group: object of type main.group

    Output: return db ID of the group in input
            return None if group not found
    """

    if group.description is not None:
        sqlite_get_group_id_query = (
            "SELECT id FROM result_group WHERE name = ? and description = ?"
        )
    else:
        sqlite_get_group_id_query = (
            "SELECT id FROM result_group WHERE name = ? and description IS ?"
        )

    if portail is not None:
        sqlite_get_group_id_query += " and portail = ?;"
        group_id = run_sql_command(
            cursor, sqlite_get_group_id_query, [group.name, group.description, portail]
        )
    else:
        sqlite_get_group_id_query += ";"
        group_id = run_sql_command(
            cursor, sqlite_get_group_id_query, [group.name, group.description]
        )

    if group_id is not None and len(group_id) > 0:
        return group_id[0][0]
    return None


def get_result_groups_ids(cursor, result_id):

    """
    Input:  cursor: connection to database
            result_id: id of the result in the db

    Output: return IDs of every groups linked to the result
    """

    sqlite_get_groups_ids_query = (
        "SELECT group_id FROM link_results_groups WHERE result_id = ?;"
    )

    groups_ids = run_sql_command(cursor, sqlite_get_groups_ids_query, [result_id])

    if groups_ids is not None and len(groups_ids) > 0:
        output_list = []
        for group_id in groups_ids:
            output_list.append(group_id[0])
        return output_list
    else:
        return None


def add_new_group_result_link(cursor, result_id, group, portail):

    group_id = get_group_id(cursor, group, portail)

    if group_id is None:
        group_id = add_new_group(cursor, group, portail)

    sql_check_add_group_result_exist_query = "SELECT result_id FROM link_results_groups WHERE result_id = ? AND group_id = ?;"

    link_id = run_sql_command(
        cursor, sql_check_add_group_result_exist_query, (result_id, group_id)
    )

    if link_id is not None and len(link_id) > 0:
        return

    sql_add_group_result_link_query = (
        "INSERT INTO link_results_groups(result_id, group_id) VALUES(?, ?);"
    )

    run_sql_command(cursor, sql_add_group_result_link_query, (result_id, group_id))


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


def build_query_where(result, ignore_portail=False):

    """
    Input:  result: object of type main.result

    Output: string with the format attribute1 = ? AND attribute2 = ? etc...
    """

    str_query = ""
    ignored_attributes = ["tags", "groups", "portail"]

    for attribute in result:
        # tags and groups are not checked
        if attribute[0] not in ignored_attributes:
            if attribute[1] == None:
                str_query += " " + attribute[0] + " IS NULL AND"
            elif type(attribute[1]) == str:
                str_query += " " + attribute[0] + ' = "' + attribute[1] + '" AND'
            else:
                str_query += " " + attribute[0] + " = " + attribute[1] + " AND"

    if ignore_portail:
        return str_query[: len(str_query) - 4] + ";"
    else:
        return str_query + ' portail = "' + result.portail + '"'


def add_new_result_to_DB(cursor, result):

    """
    Add result in the database

    Input:  cursor: connection to database
            result: object of type main.Result

    Output: return newly created result's id
    """

    attribute_query = "(" + ", ".join(attributes) + ")"
    value_query = "(" + "?, " * (len(attributes) - 1) + "?)"
    sqlite_add_result_to_db_query = (
        "INSERT INTO result" + attribute_query + " VALUES" + value_query + ";"
    )

    data = build_query_data(result)

    run_sql_command(cursor, sqlite_add_result_to_db_query, data)

    result_id = get_result_ID(cursor, result, True)

    if result.tags is not None:
        for tag in result.tags:
            add_new_tag_result_link(cursor, result_id, tag, result.portail)

    if result.groups is not None:
        for group in result.groups:
            add_new_group_result_link(cursor, result_id, group, result.portail)

    return result_id


def get_result_ID(cursor, result, ignore_tag_and_groups=False):

    """
    Input:  cursor: connection to database
            result: object of type main.Result
            ignore_tag_and_groups: wether or not to ignore tags and groups attributes
            ignore_portail: wether or not to ignore the portail attribute
    
    Output: ID of the result if it exist in the database
            return None if result not found
    """

    sqlite_get_result_ID_query = (
        "SELECT id FROM result WHERE" + build_query_where(result) + ";"
    )

    result_ids = run_sql_command(cursor, sqlite_get_result_ID_query, None)

    if result_ids is not None and len(result_ids) > 0:

        if ignore_tag_and_groups:

            return result_ids[len(result_ids) - 1][0]

        else:

            for r_ids in result_ids:

                result_id = r_ids[0]

                result_tag_ids = get_result_tags_ids(cursor, result_id)
                if result_tag_ids is not None:
                    result_tag_ids = sorted(result_tag_ids)

                result_group_ids = get_result_groups_ids(cursor, result_id)
                if result_group_ids is not None:
                    result_group_ids = sorted(result_group_ids)

                if result.tags is not None:
                    tag_ids = [
                        get_tag_id(cursor, tag, result.portail) for tag in result.tags
                    ]
                    if None in tag_ids:
                        return None
                    else:
                        tag_ids = sorted(tag_ids)
                else:
                    tag_ids = None

                if result.groups is not None:
                    group_ids = [
                        get_group_id(cursor, group, result.portail)
                        for group in result.groups
                    ]
                    if None in group_ids:
                        return None
                    else:
                        group_ids = sorted(group_ids)
                else:
                    group_ids = None

                if tag_ids == result_tag_ids and group_ids == result_group_ids:
                    return result_id

    return None


# Function: Add a new search entry in the database
def add_new_search_query(conversation_id, user_search, portail, date):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        sqlite_insert_search_query = "INSERT INTO search(conversation_id, user_search, portail, date) VALUES(?, ?, ?, ?);"
        run_sql_command(
            cursor,
            sqlite_insert_search_query,
            (conversation_id, user_search, portail, date),
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

            if result_id is None:

                result_id = add_new_result_to_DB(cursor, result)

            else:

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


def update_proposed_result_feedback(conversation_id, search, feedbacks_list):

    """
    Update the feedback in search_reranking_feedback table

    Input:  conversation_id: id of the conversation where the search was done
            search: search entered by the user
            feedbacks_list: list of feedback of type (result, feedback) by the user who made that search      
    """

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_id = get_search_id_from_conv_id_and_search(
            cursor, conversation_id, search
        )

        if search_id is not None:

            for fback in feedbacks_list:

                result_id = get_result_ID(cursor, fback.result)

                if result_id is None:

                    result_id = add_new_result_to_DB(cursor, fback.result)

                else:

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


def get_search_id_from_conv_id_and_search(
    cursor, conversation_id, user_search, portail=None
):

    """
    Input:  conversation_id: id of the conversation the search was done
            user_search: search entered by the user
            portail: if you want to use a particular portail

    Output: search_id corresponding to the couple (conversation_id, user_search)        
    """

    try:

        if portail == None:
            sqlite_get_search_id_query = "SELECT id FROM search where conversation_id = ? and user_search = ? ORDER BY id DESC;"
            record = run_sql_command(
                cursor, sqlite_get_search_id_query, (conversation_id, user_search)
            )
        else:
            sqlite_get_search_id_query = "SELECT id FROM search where conversation_id = ? and user_search = ? and portail = ? ORDER BY id DESC;"
            record = run_sql_command(
                cursor,
                sqlite_get_search_id_query,
                (conversation_id, user_search, portail),
            )

        if record != None and len(record) > 0:
            return record[0][0]
        else:
            return None

    except sqlite3.Error as error:
        print("-GET_SEARCH_ID-\nError while connecting to sqlite", error, "\n")


def get_search_ids_from_search(cursor, user_search, portail=None):

    """
    Input:  user_search: search entered by the users
            portail: if you want to use a particular portail

    Output: List of search_id corresponding to the string user_search by different users 
    """

    try:

        if portail == None:
            sqlite_get_search_id_query = (
                "SELECT id FROM search where user_search = ? ORDER BY id DESC;"
            )
            record = run_sql_command(cursor, sqlite_get_search_id_query, [user_search])

        else:
            sqlite_get_search_id_query = "SELECT id FROM search where user_search = ? and portail = ? ORDER BY id DESC;"
            record = run_sql_command(
                cursor, sqlite_get_search_id_query, (user_search, portail)
            )

        if record != None and len(record) > 0:
            search_ids = []
            for search_id in record:
                search_ids.append(search_id[0])
            return search_ids
        else:
            return None

    except sqlite3.Error as error:
        print("-GET_SEARCH_ID-\nError while connecting to sqlite", error, "\n")


def get_feedback_for_reranking(user_search, result, portail=None):

    """
    Input:  user_search: search entered by the user
            result: object of type main.Result

    Output: List of feedbacks corresponding to the couple (user_search, result)        
    """

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_ids = get_search_ids_from_search(cursor, user_search, portail)

        if search_ids != None and len(search_ids) > 0:

            result_id = get_result_ID(cursor, result)

            if result_id is None:
                return []

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

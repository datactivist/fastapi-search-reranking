import sqlite3
import numpy as np

database = "data/user_reranking_feedback.db"

attributes = [
    "title",
    "url",
    "description",
    "portal",
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


def add_new_tag(cursor, tag, portal):

    """
    Add a new tag to the table result_tag

    Input:  cursor: connection to database
            tag: string

    Output: return newly created tag's id
    """

    sqlite_add_tag_query = "INSERT INTO result_tag(name, portal) VALUES (?, ?);"

    run_sql_command(cursor, sqlite_add_tag_query, (tag, portal))
    return get_tag_id(cursor, tag, portal)


def get_tag_id(cursor, tag, portal=None):

    """
    Input:  cursor: connection to database
            tag: string

    Output: return db ID of the tag in input
            return None if tag not found
    """

    if portal is not None:
        sqlite_get_tag_id_query = (
            "SELECT id FROM result_tag WHERE name = ? and portal = ?;"
        )
        tag_id = run_sql_command(cursor, sqlite_get_tag_id_query, [tag, portal])
    else:
        sqlite_get_tag_id_query = "SELECT id FROM result_tag WHERE name = ?;"
        tag_id = run_sql_command(cursor, sqlite_get_tag_id_query, [tag])

    if tag_id is not None and len(tag_id) > 0:
        return tag_id[0][0]
    return None


def get_tag_name(cursor, tag_id):

    """
    Input:  cursor: connection to database
            tag_id: int

    Output: return tag name of the id in input
            return None if tag not found
    """

    sqlite_get_tag_name_query = "SELECT name FROM result_tag WHERE id = ?;"
    tag_name = run_sql_command(cursor, sqlite_get_tag_name_query, [tag_id])

    if tag_name is not None and len(tag_name) > 0:
        return tag_name[0][0]
    return None


def get_result_tags_list(cursor, result_id):

    """
    Input:  
        cursor: connection to database
        result_id: int

    Output: 
        return list of tag name linked to the result in input
        return None if the result has no tags linked
    """

    slite_get_tags_link_list = (
        "SELECT * from link_results_tags WHERE result_id = " + str(result_id)
    )
    tags_link_list = run_sql_command(cursor, slite_get_tags_link_list, None)
    return (
        [get_tag_name(cursor, tag_link[1]) for tag_link in tags_link_list]
        if tags_link_list is not None
        else None
    )


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


def add_new_tag_result_link(cursor, result_id, tag, portal):

    tag_id = get_tag_id(cursor, tag, portal)

    if tag_id is None:
        tag_id = add_new_tag(cursor, tag, portal)

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


def add_new_group(cursor, group, portal):

    """
    Add a new group to the table result_group

    Input:  cursor: connection to database
            group: object of type main.group

    Output: return newly created group's id
    """

    sqlite_add_group_query = (
        "INSERT INTO result_group(name, description, portal) VALUES (?, ?, ?);"
    )

    run_sql_command(
        cursor, sqlite_add_group_query, [group.name, group.description, portal]
    )
    return get_group_id(cursor, group, portal)


def get_group_id(cursor, group, portal=None):

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

    if portal is not None:
        sqlite_get_group_id_query += " and portal = ?;"
        group_id = run_sql_command(
            cursor, sqlite_get_group_id_query, [group.name, group.description, portal]
        )
    else:
        sqlite_get_group_id_query += ";"
        group_id = run_sql_command(
            cursor, sqlite_get_group_id_query, [group.name, group.description]
        )

    if group_id is not None and len(group_id) > 0:
        return group_id[0][0]
    return None


def get_group_data(cursor, group_id):

    """
    Input:  cursor: connection to database
            group_id: int

    Output: return group name and description of the id in input
            return None if group not found
    """

    sqlite_get_group_data_query = (
        "SELECT name, description FROM result_group WHERE id = ?;"
    )
    group_data = run_sql_command(cursor, sqlite_get_group_data_query, [group_id])

    if group_data is not None and len(group_data) > 0:
        return group_data[0]
    return None


def get_result_groups_list(cursor, result_id):

    """
    Input:  
        cursor: connection to database
        result_id: int

    Output: 
        return list of groups linked to the result in input
        return None if the result has no groups linked
    """

    slite_get_groups_link_list = (
        "SELECT * from link_results_groups WHERE result_id = " + str(result_id)
    )
    groups_link_list = run_sql_command(cursor, slite_get_groups_link_list, None)
    return (
        [get_group_data(cursor, group_link[1]) for group_link in groups_link_list]
        if groups_link_list is not None
        else None
    )


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


def add_new_group_result_link(cursor, result_id, group, portal):

    group_id = get_group_id(cursor, group, portal)

    if group_id is None:
        group_id = add_new_group(cursor, group, portal)

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


def build_query_where(result, ignore_portal=False):

    """
    Input:  result: object of type main.result

    Output: string with the format attribute1 = ? AND attribute2 = ? etc...
    """

    str_query = ""
    ignored_attributes = ["tags", "groups", "portal"]

    for attribute in result:
        # tags and groups are not checked
        if attribute[0] not in ignored_attributes:
            if attribute[1] == None:
                str_query += " " + attribute[0] + " IS NULL AND"
            elif type(attribute[1]) == str:
                str_query += " " + attribute[0] + ' = "' + attribute[1] + '" AND'
            else:
                str_query += " " + attribute[0] + " = " + attribute[1] + " AND"

    if ignore_portal:
        return str_query[: len(str_query) - 4] + ";"
    else:
        return str_query + ' portal = "' + result.portal + '"'


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
            add_new_tag_result_link(cursor, result_id, tag, result.portal)

    if result.groups is not None:
        for group in result.groups:
            add_new_group_result_link(cursor, result_id, group, result.portal)

    return result_id


def get_result_ID(cursor, result, ignore_tag_and_groups=False):

    """
    Input:  cursor: connection to database
            result: object of type main.Result
            ignore_tag_and_groups: wether or not to ignore tags and groups attributes
            ignore_portal: wether or not to ignore the portal attribute
    
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
                        get_tag_id(cursor, tag, result.portal) for tag in result.tags
                    ]
                    if None in tag_ids:
                        return None
                    else:
                        tag_ids = sorted(tag_ids)
                else:
                    tag_ids = None

                if result.groups is not None:
                    group_ids = [
                        get_group_id(cursor, group, result.portal)
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


def get_result_from_ID(cursor, result_id):

    """
    Input:  cursor: connection to database
            result_id: id of the result
    
    Output: content of the result
            return None if result not found
    """

    sqlite_get_result_data_query = "SELECT * from result WHERE id = " + str(result_id)
    result = run_sql_command(cursor, sqlite_get_result_data_query, None)

    return (
        {
            "title": result[0][1],
            "url": result[0][2],
            "description": result[0][3],
            "portal": result[0][4],
            "owner_org": result[0][5],
            "owner_org_description": result[0][6],
            "maintainer": result[0][7],
            "dataset_publication_date": result[0][8],
            "dataset_modification_date": result[0][9],
            "metadata_creation_date": result[0][10],
            "metadata_modification_date": result[0][11],
            "tags": get_result_tags_list(cursor, result_id),
            "groups": [
                {"name": group[0], "description": group[1]}
                for group in get_result_groups_list(cursor, result_id)
            ],
        },
    )


# Function: Add a new search entry in the database
def add_new_search_query(conversation_id, user_search, portal, date):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        sqlite_insert_search_query = "INSERT INTO search(conversation_id, user_search, portal, date) VALUES(?, ?, ?, ?);"
        run_sql_command(
            cursor,
            sqlite_insert_search_query,
            (conversation_id, user_search, portal, date),
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


def add_search_target_feedback(cursor, search_id, search_target):

    try:
        sqlite_add_search_target_feedback_query = (
            "INSERT INTO search_target_feedback(search_id, search_target) VALUES(?, ?);"
        )

        run_sql_command(
            cursor, sqlite_add_search_target_feedback_query, (search_id, search_target),
        )
    except sqlite3.Error as error:
        print(
            "-ADD_SEARCH_TARGET_RESULT\nError while connecting to sqlite", error, "\n"
        )


def update_proposed_result_feedback(
    conversation_id, search, search_target, feedbacks_list
):

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

        add_search_target_feedback(cursor, search_id, search_target)

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
    cursor, conversation_id, user_search, portal=None
):

    """
    Input:  conversation_id: id of the conversation the search was done
            user_search: search entered by the user
            portal: if you want to use a particular portal

    Output: search_id corresponding to the couple (conversation_id, user_search)        
    """

    try:

        if portal == None:
            sqlite_get_search_id_query = "SELECT id FROM search where conversation_id = ? and user_search = ? ORDER BY id DESC;"
            record = run_sql_command(
                cursor, sqlite_get_search_id_query, (conversation_id, user_search)
            )
        else:
            sqlite_get_search_id_query = "SELECT id FROM search where conversation_id = ? and user_search = ? and portal = ? ORDER BY id DESC;"
            record = run_sql_command(
                cursor,
                sqlite_get_search_id_query,
                (conversation_id, user_search, portal),
            )

        if record != None and len(record) > 0:
            return record[0][0]
        else:
            return None

    except sqlite3.Error as error:
        print("-GET_SEARCH_ID-\nError while connecting to sqlite", error, "\n")


def get_search_ids_from_search(cursor, user_search, portal=None):

    """
    Input:  user_search: search entered by the users
            portal: if you want to use a particular portal

    Output: List of search_id corresponding to the string user_search by different users 
    """

    try:

        if portal == None:
            sqlite_get_search_id_query = (
                "SELECT id FROM search where user_search = ? ORDER BY id DESC;"
            )
            record = run_sql_command(cursor, sqlite_get_search_id_query, [user_search])

        else:
            sqlite_get_search_id_query = "SELECT id FROM search where user_search = ? and portal = ? ORDER BY id DESC;"
            record = run_sql_command(
                cursor, sqlite_get_search_id_query, (user_search, portal)
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


def get_feedback_for_reranking(user_search, result, portal=None):

    """
    Input:  user_search: search entered by the user
            result: object of type main.Result

    Output: List of feedbacks corresponding to the couple (user_search, result)        
    """

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_ids = get_search_ids_from_search(cursor, user_search, portal)

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


def extract_database_feedbacks():

    """
    Return a copy of the database content in JSON format
    """

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        sqlite_get_search_list_query = "SELECT * FROM search"

        database_copy = []

        search_list = run_sql_command(cursor, sqlite_get_search_list_query, None)

        for search in search_list:

            sqlite_get_search_data_query = (
                "SELECT * from search_reranking_feedback WHERE search_id = "
                + str(search[0])
            )
            search_data_list = run_sql_command(
                cursor, sqlite_get_search_data_query, None
            )

            feedbacks = []

            for data in search_data_list:

                feedbacks.append(
                    {
                        "result": get_result_from_ID(cursor, data[4])[0],
                        "old_rank": data[2],
                        "new_rank": data[3],
                        "feedback": data[5],
                        "methods_used": data[6],
                    }
                )

            database_copy.append(
                {
                    "user_search": search[2],
                    "portal": search[3],
                    "date": search[4],
                    "feedbacks": feedbacks,
                }
            )

        return database_copy

    except sqlite3.Error as error:
        print("-Extract_Feedbacks-\nError while connecting to sqlite:", error, "\n")
        return []

from pathlib import Path
import json
import numpy as np

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
    "tags",
    "groups",
]

attribute_query = " = ? AND ".join(attributes) + " = ?:"
sqlite_get_result_ID_query = "SELECT id FROM result WHERE " + attribute_query

print(sqlite_get_result_ID_query)

#!/usr/bin/env python3
""" Module for using PyMongo """


def top_students(mongo_collection):
    """ top_students.
    """
    return mongo_collection.aggregate([
        {
            "$project": {
                "name": "$name",
                "averageScore": {"$avg": "$topics.score"}
            }
        },
        {"$sort": {"averageScore": -1}}
    ])

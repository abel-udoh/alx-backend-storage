#!/usr/bin/env python3
""" Lists all documents in a collection """

import pymongo


def list_all(mongo_collection):
    """ Return a list of all documents in a collection or an empty list
    """
    return [each for each in mongo_collection.find()]

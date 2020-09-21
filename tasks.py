#!/usr/bin/env python3
import argparse
from src.services.api import get_github
from src.database import db
from pymongo import UpdateOne


def update(parameter_list):
    data = get_github("/repos/ironhack-datalabs/datamad0820/pulls")
    operations = []

    for pr in data:
        github_user = pr.get('user', None)
        if github_user:
            operation = UpdateOne({'github_id': github_user['id']}, {
                "$set": {
                    'username': github_user['login'],
                    'github_id': github_user['id'],
                    'url': github_user['url']
                }

            }, upsert=True)

            operations.append(operation)

    db['students'].bulk_write(operations)


def main():
    parser = argparse.ArgumentParser(description='Task for calling github api')

    parser.add_argument('--merge', dest='merge',
                        help='File to merge.')

    parser.add_argument('--update', dest='update', action="store_true",
                        help='Update DB.')

    args = parser.parse_args()

    if args.update:
        update(args.update)


if __name__ == "__main__":
    main()

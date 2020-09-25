#!/usr/bin/env python3
import argparse
from src.services.api import get_github
from src.database import db
from pymongo import UpdateOne
import re
import datetime


def update_users():
    data, links = get_github(
        "/repos/ironhack-datalabs/datamad0820/pulls?state=all", return_links=True)
    operations = []

    while links.get('next', None):
        for pr in data:
            github_user = pr.get('user', None)
            if github_user:
                operation = UpdateOne({'github_id': github_user['id']}, {
                    "$set": {
                        'student_name': github_user['login'],
                        'github_id': github_user['id'],
                        'url': github_user['url'],
                        'html_url': github_user['html_url']
                    }

                }, upsert=True)

                operations.append(operation)
        match = re.search(r'page=(\d+)',  links.get('next')['url'])
        if match:
            page = match.group(1)
            url = f"/repos/ironhack-datalabs/datamad0820/pulls?state=all&page={page}"
            data, links = get_github(url, return_links=True)
        else:
            return
    db['students'].bulk_write(operations)


def update_labs():
    data, links = get_github(
        "/repos/ironhack-datalabs/datamad0820/pulls?state=all", return_links=True)
    operations = []

    while links.get('next', None):
        for pr in data:
            lab_name = re.findall(r'\[(.+)\]', pr.get('title'))
            if len(lab_name):
                operation = UpdateOne({'title': lab_name[0]}, {
                    "$set": {
                        'title': lab_name[0]
                    }

                }, upsert=True)
                operations.append(operation)

        db['labs'].bulk_write(operations)
        print(len(operations), 'DOCUMENTS ADDED')

        match = re.search(r'page=(\d+)',  links.get('next')['url'])
        if match:
            page = match.group(1)
            url = f"/repos/ironhack-datalabs/datamad0820/pulls?state=all&page={page}"
            data, links = get_github(url, return_links=True)
        else:
            return


def parse_comments():
    prs = db['pull_requests'].find()
    operations = []
    for pr in prs:
        comments = get_github(
            f"/repos/ironhack-datalabs/datamad0820/issues/{pr['number']}/comments")
        for comment in comments:
            image = re.findall(r'!\[image\]\((.*)\)', comment.get('body'))
            image_href = re.findall(r'img src=\"(.*)\" ', comment.get('body'))
            operation = UpdateOne({'number': pr['number']},
                                  {
                '$push': {'images': {'$each': [*image, *image_href]}}
            })
            operations.append(operation)
    db['pull_requests'].bulk_write(operations)


def get_last_commit():
    prs = db['pull_requests'].find()
    operations = []
    for pr in prs:
        commits = get_github(
            f"/repos/ironhack-datalabs/datamad0820/pulls/{pr['number']}/commits")

        date = commits[-1]['commit']['committer']['date']
        last_commit = datetime.datetime.strptime(
            date, '%Y-%m-%dT%H:%M:%SZ')
        operation = UpdateOne({'number': pr['number']},
                              {
            '$set': {'last_commit': last_commit}
        })
        operations.append(operation)
    db['pull_requests'].bulk_write(operations)


def update_PRs():
    data, links = get_github(
        "/repos/ironhack-datalabs/datamad0820/pulls?state=all", return_links=True)
    operations = []
    labs = db['labs'].find()
    cached_labs = {lab['title']: lab['_id'] for lab in labs}
    while links.get('next', None):
        for pr in data:
            lab_name = re.findall(r'\[(.+)\]', pr.get('title'))
            lab_id = None
            if len(lab_name):
                lab_name = lab_name[0]
                lab_id = cached_labs.get(lab_name)
            image = re.findall(r'!\[image\]\((.*)\)', pr.get('body'))
            image_href = re.findall(r'img src=\"(.*)\" ', pr.get('body'))
            github_user = pr.get('user', None)
            closed_at = None if not pr['closed_at'] else datetime.datetime.strptime(
                pr['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
            operation = UpdateOne({'number': pr['number']}, {
                "$set": {
                    'title': pr.get('title'),
                    'html_url': pr.get('html_url'),
                    'images': [*image, * image_href],
                    "number": pr['number'],
                    'lab_id': lab_id,
                    'state': pr['state'],
                    "github_user_id": github_user['id'],
                    "comments_url": pr['comments_url'],
                    "commits_url": pr['commits_url'],
                    'created_at':  datetime.datetime.strptime(
                        pr['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
                    'updated_at':  datetime.datetime.strptime(
                        pr['updated_at'], '%Y-%m-%dT%H:%M:%SZ'),
                    'closed_at': closed_at
                }

            }, upsert=True)
            operations.append(operation)
        db['pull_requests'].bulk_write(operations)
        print(len(operations), 'DOCUMENTS ADDED')
        match = re.search(r'page=(\d+)',  links.get('next')['url'])
        if match:
            page = match.group(1)
            url = f"/repos/ironhack-datalabs/datamad0820/pulls?state=all&page={page}"
            data, links = get_github(url, return_links=True)


def main():
    parser = argparse.ArgumentParser(description='Task for calling github api')

    parser.add_argument('--merge', dest='merge',
                        help='File to merge.')

    parser.add_argument('--updateusers', dest='updateusers', action="store_true",
                        help='Update DB.')
    parser.add_argument('--updatelabs', dest='updatelabs', action="store_true",
                        help='Update DB.')
    parser.add_argument('--updateprs', dest='updateprs', action="store_true",
                        help='Update DB.')
    parser.add_argument('--parsecomments', dest='parsecomments', action="store_true",
                        help='Update DB.')
    parser.add_argument('--lastcommit', dest='lastcommit', action="store_true",
                        help='Update DB.')

    args = parser.parse_args()

    if args.updateusers:
        update_users()
    if args.updatelabs:
        update_labs()
    if args.updateprs:
        update_PRs()
    if args.parsecomments:
        parse_comments()
    if args.lastcommit:
        get_last_commit()


if __name__ == "__main__":
    main()

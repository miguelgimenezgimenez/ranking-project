from config import DBURL
from pymongo import MongoClient, TEXT
client = MongoClient(DBURL)
db = client.get_database()

db['students'].create_index(
    [('github_id', TEXT)], name='search_index', default_language='english')

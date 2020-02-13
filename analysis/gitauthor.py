import pandas as pd
from datetime import datetime


class GitAuthor(object):
    author_groups = None

    def __init__(self, name):
        self.name = name
        self.group = self.author_groups.get_group(name)

    @classmethod
    def get_authors_sorted_by_commit_count(cls):
        authors = cls.author_groups['author_timestamp'].count() \
            .reset_index(name='count') \
            .sort_values(['count'], ascending=False)
        return authors['author_name'].values

    @property
    def first_commit_date(self):
        timestamp = self.group.min().loc['author_timestamp']
        return datetime.utcfromtimestamp(timestamp)

    @property
    def latest_commit_date(self):
        timestamp = self.group.max().loc['author_timestamp']
        return datetime.utcfromtimestamp(timestamp)

    @property
    def lines_removed(self):
        pass

    @property
    def lines_added(self):
        pass

    @property
    def active_days_count(self):
        ts = pd.to_datetime(self.group['author_timestamp'], unit='s', utc=True)
        return ts.dt.normalize().unique().shape[0]

    @property
    def contributed_days_count(self):
        if self.first_commit_date != self.latest_commit_date:
            return (self.latest_commit_date - self.first_commit_date).days
        else:
            return 1

    @property
    def commits_count(self):
        return self.group.count().loc['author_timestamp']

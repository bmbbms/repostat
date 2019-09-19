import time
import os
import datetime
from .gitstatistics import GitStatistics


class GitDataCollector(object):

    def __init__(self, config: dict, project_directory):
        self.stamp_created = time.time()
        self.conf = config
        if not self.conf['project_name']:
            self.projectname = os.path.basename(os.path.abspath(project_directory))
        else:
            self.projectname = self.conf['project_name']

        self.repo_statistics = GitStatistics(project_directory)
        self.analysed_branch = self.repo_statistics.repo.head.shorthand

        # name -> {commits, first_commit_stamp, last_commit_stamp, last_active_day, active_days,
        #  lines_added,
        #  lines_removed}
        self.authors = self.repo_statistics.authors
        self.changes_by_date_by_author = self.repo_statistics.author_changes_history

        self.total_commits = 0
        self.total_files = 0
        self.authors_by_commits = 0

        self.files_by_stamp = {}  # stamp -> files

        # extensions
        self.extensions = {}  # extension -> files, lines

    # dict['author'] = { 'commits': 512 } - ...key(dict, 'commits')
    @staticmethod
    def getkeyssortedbyvaluekey(d, key):
        return [el[1] for el in sorted([(d[el][key], el) for el in d.keys()])]

    def collect(self):
        revs_cached = []
        revs_to_read = []
        # look up rev in cache and take info from cache if found
        # if not append rev to list of rev to read from repo
        for ts, tree_id in self.repo_statistics.get_revisions():
            revs_to_read.append((ts, tree_id))

        # update cache with new revisions and append then to general list
        for ts, rev in revs_to_read:
            diff = self.repo_statistics.get_files_info(rev)
            count = len(diff)
            revs_cached.append((ts, count))

        for (stamp, files) in revs_cached:
            self.files_by_stamp[stamp] = files
        self.total_commits = len(self.files_by_stamp)

        ext_dat = {}
        for p in self.repo_statistics.get_files_info('HEAD'):
            filename = os.path.basename(p.delta.old_file.path)
            basename_ext = filename.split('.')
            ext = basename_ext[1] if len(basename_ext) == 2 and basename_ext[0] else ''
            if len(ext) > self.conf['max_ext_length']:
                ext = ''
            if ext not in ext_dat:
                ext_dat[ext] = {'files': 0, 'lines': 0}
            # unclear what first two entries of the tuple mean, for each file they were equal to 0
            _, _, lines_count = p.line_stats
            ext_dat[ext]['lines'] += lines_count
            ext_dat[ext]['files'] += 1
        self.extensions = ext_dat
        self.total_files = sum(v['files'] for k, v in ext_dat.items())

    def refine(self):
        # authors
        # name -> {place_by_commits, date_first, date_last, timedelta}
        self.authors_by_commits = GitDataCollector.getkeyssortedbyvaluekey(self.authors, 'commits')
        self.authors_by_commits.reverse()  # most first
        for i, name in enumerate(self.authors_by_commits):
            self.authors[name]['place_by_commits'] = i + 1

        for name in self.authors.keys():
            a = self.authors[name]
            date_first = datetime.datetime.fromtimestamp(a['first_commit_stamp'])
            date_last = datetime.datetime.fromtimestamp(a['last_commit_stamp'])
            delta = (date_last - date_first).days
            a['date_first'] = date_first.strftime('%Y-%m-%d')
            a['date_last'] = date_last.strftime('%Y-%m-%d')
            a['timedelta'] = delta
            if 'lines_added' not in a: a['lines_added'] = 0
            if 'lines_removed' not in a: a['lines_removed'] = 0

    def get_author_info(self, author):
        return self.authors[author]

    def get_authors(self, limit=None):
        res = GitDataCollector.getkeyssortedbyvaluekey(self.authors, 'commits')
        res.reverse()
        return res[:limit]

    def get_total_commits(self):
        return self.total_commits

    def get_total_files(self):
        return self.total_files

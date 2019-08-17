from setuptools import setup
from tools.configuration import Configuration

# name with underscore is used here because 'repostat' is already occupied by https://pypi.org/project/repostat/
setup(name='repo_stat',
      version=Configuration.get_release_data_info()['develop_version'],
      description='Desktop git repository analyser and report creator.',
      keywords='git analisys statistics',
      url='https://github.com/vifactor/repostat',
      author='Viktor Kopp',
      author_email='vifactor(at)gmail.com',
      license='GPLv3',
      packages=['analysis', 'tools'],
      install_requires=[
          'cffi==1.11.5',
          'Jinja2>=2.10.1',
          'MarkupSafe==1.0',
          'pygit2>=0.24.2,<=0.28',
          'pytz==2018.5',
          'six>=1.11.0'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=['repostat.py', 'export_repos.py'],
      include_package_data=True,
      zip_safe=False)

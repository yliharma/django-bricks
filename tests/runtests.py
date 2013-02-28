#!/usr/bin/env python
import os
import sys

sys.path.append('..')
tmp = os.environ.get('DJANGO_SETTINGS_MODULE', '')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.test.simple import DjangoTestSuiteRunner

if __name__ == "__main__":
    failures = DjangoTestSuiteRunner().run_tests(['djangobricks',], verbosity=1)
    if failures:
        sys.exit(failures)
    os.environ['DJANGO_SETTINGS_MODULE'] = tmp

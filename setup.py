import os
from distutils.core import setup

APP_NAME = 'djangobricks'
PACKAGES = ['%s.management',]

root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

data_files = []
for dirpath, dirnames, filenames in os.walk(APP_NAME):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        continue
    elif filenames:
        for f in filenames:
            data_files.append(os.path.join(dirpath[len(APP_NAME)+1:], f))

packages = [APP_NAME] + [i % APP_NAME for i in PACKAGES]

setup(
    name=APP_NAME,
    version="%s.%s" % __import__(APP_NAME).VERSION[:2],
    packages=packages, 
    package_data={APP_NAME: data_files},
)
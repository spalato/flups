from setuptools import setup, find_packages

setup(name='FLUPS',
      version='0.1',
      description='Tools for the processing and analysis of FLUPS data.',
      url='',
      author='S. Palato',
      author_email='',
      license='',
      packages=find_packages("src"),
      package_dir={"": "src"},
      zip_safe=False)
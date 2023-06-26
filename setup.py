from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='robot_rumble',
    version='0.0.14',
    packages=["robot_rumble"],
    url='https://github.com/guptat07/Robot-Rumble',
    license='',
    author='Tony Gupta, Anthony Liao, Maya Singh, Kaylee Conrad',
    author_email='kaymconrad@gmail.com',
    description='2D Side-Scroller Game for UF CEN4930 Performant Programming (in Japan!)',
    readme = "README.md",
    install_requires=['arcade>=2.6.17'],
    python_requires='==3.10',
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/plain',

    entry_points =
    {
        "console_scripts":
            [
                "play_robot_rumble = robot_rumble.main:main",
            ],
    },
)

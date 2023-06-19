from setuptools import setup

setup(
    name='Robot-Rumble',
    version='0.1',
    packages=[],
    url='https://github.com/guptat07/Robot-Rumble',
    license='',
    author='Kaylee Conrad',
    author_email='kaymconrad@gmail.com',
    description='2D Side-Scroller Game for UF CEN4930 Performant Programming (in Japan!)',
    install_requires=['arcade'],
    python_requires='==3.10',

    entry_points =
    {
        "console_scripts":
            [
                "play_robot_rumble = main:main",
            ],
    },
)

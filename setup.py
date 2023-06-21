from setuptools import setup

setup(
    name='robot_rumble_package',
    version='0.1.15',
    packages=["robot_rumble_package"],
    url='https://github.com/guptat07/Robot-Rumble',
    license='',
    author='Tony Gupta, Anthony Liao, Maya Singh, Kaylee Conrad',
    author_email='kaymconrad@gmail.com',
    description='2D Side-Scroller Game for UF CEN4930 Performant Programming (in Japan!)',
    install_requires=['arcade>=2.6'],
    python_requires='==3.10',
    include_package_data=True,

    entry_points =
    {
        "console_scripts":
            [
                "play_robot_rumble = robot_rumble_package.main:main",
            ],
    },
)

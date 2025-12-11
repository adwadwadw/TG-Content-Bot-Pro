from setuptools import setup, find_packages

setup(
    name="tg-content-bot-pro",
    version="1.0.0",
    description="Telegram Content Bot Pro - A powerful Telegram bot for content management",
    packages=find_packages(),
    install_requires=[
        "python-decouple>=3.8",
        "pyrogram>=2.0.0", 
        "tgcrypto>=1.2.5",
        "motor>=3.3.2",
        "python-telegram-bot>=20.7",
        "requests>=2.31.0"
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'tg-bot=main.__main__:enhanced_main',
        ],
    },
)
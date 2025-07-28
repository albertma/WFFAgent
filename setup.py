from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wff_agent",
    version="0.05",
    author="WFF Agent Team",
    author_email="contact@wff-agent.com",
    description="一个基于人工智能的股票分析智能助手",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/wff_agent",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "yfinance>=0.2.0",
        "langchain~=0.3.0",
        "langchain-core~=0.3.0",
        "langchain-mcp",
        "langchain-groq",
        "openai>=1.0.0",
        "fastmcp",
        "fastapi>=0.100.0",
        "mcp[cli]",
        "uvicorn>=0.20.0",
        "streamlit>=1.28.0",
        "gradio~=5.27.0",
        "PyQt6>=6.5.0",
        "akshare>=1.12.0",
        "alpha-vantage>=2.3.1",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.8.0",
        "httpx>=0.24.0",
    ],
    extras_require={
        "dev": [
            "pyinstaller>=6.0.0",
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wff-agent=wff_agent.main:main",
            "wff-desktop=wff_agent.build_desktop_app:main",
            "wff-web=wff_agent.web_ui:create_web_ui",
        ],
    },
) 
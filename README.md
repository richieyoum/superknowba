# 🌌 SuperKnowBa
<div align="center"><img src='https://physics.aps.org/assets/36a7bcf2-38a5-4db6-a05f-c0a2ecc5903d/e51_1.png' width=500></div>

## 🎙️ Introduction

Build, manage, and chat with your knowledge base from multiple data sources like CSV, PDF, TXT, DOCX, and more, in just a click of a button.

This application leverages OpenAI's ChatGPT and Meta's FAISS to fetch relevant response to your questions. More options for different model choice and vectorstore choice is on the way!

## Demo
You can test SuperKnowBa demo here: https://superknowba.streamlit.app/
![Screenshot from 2023-07-25 12-57-39](https://github.com/richieyoum/superknowba/assets/43356500/021b3754-6423-4834-94eb-b8edee047c89)

**Warning**: Any data you upload in the demo will persist in the vectorDB! **Do not upload any private information**

## 🧐 How it works
Superknowba accepts a variety of file formats, currently CSV, PDF, TXT, and DOCX.

In the side pannel, you can create a database and upload the files. The texts from the files are then formatted, vectorized and chunked into smaller batches, where they are stored in a vector database.

Once you create a database, you can choose the database to upload another files in the future, or simply chat with the database. This database will persist in your local directory under `superknowba/vectorstores`, meaning that you'll be able to re-use the database everytime you start the application. It automatically scans for any new database you create.

When a user ask a question, superknowba applies similar preprocessing and compares it to the items in vectorstores, which picks the most relevant ones in semantic similarity rankings. This is re-formatted by ChatGPT and is returned as a response.

Note, if you're chatting with a database specifically, it will only be able to answer questions related to the data underneath. For example, it won't be able to answer a question "why is sky blue?" against a database about stock market data. This will be resolved in future iteration.

## 🦾 Installation
1. Clone the repository
2. Install dependencies
    ```
    pip install -r requirements.txt
    ```
3. Now, you can simply run the following to get started!
    ```
    streamlit app.py
    ```

## 🛠️ Upcoming features
- PII Remover option to automatically remove sensitive data according to your needs
- Support for different model, embedding, and vectorDB choice
- Add fallback option for model used
- Speed up CSV loader
- Dedicated VectorDB management page, including CRUD operations for files in each DB
- Parallelization in API calls, based on your choice to speed up the process
- Add caching
- Support for more file formats (url, HTML, youtube, etc.)
- Support to connect with foreign DB

## 🤝 Contributing
Open to pull requests!

You will need to install pre-commit with the provided config with the following
```
pip install pre-commit
pre-commit install
```
4. make pull request

# Overview of Natural Language to SQL

Enterprise data warehouses represent many of the largest technology investments for companies across all industries in the past 20 years. While generative AI has shown a lot of promise in creating novel content and comprehending large corpora of information in unstructured format, how will it improve consumption of the data organizations have invested so much in making useful? These data sources are among the most trusted in an organization and drive decisions at the highest levels of leadership in many cases.

Since its inception in the 70’s, Structure Query Language (SQL) has been the most ubiguitous language to interact with a databases but one still needs a deep understanding of set theory, data types, and foreign key relationships in order to make sense of the data. Generative AI offers a way to bridge this knowledge and skills gap by translating natural language questions into a valid SQL query.

### Personas
The systems and people standing to benefit from this access pattern to databases includes non-technical folks looking to incorporate relational data sources into their process, like customer service agents and call-center associates. Further, technical use cases include Extract-Transform-Load pipelines, existing Retrieval Augmented Generation (RAG) architectures that integrate relational databases, and organizations who are dealing with a data platform too big to reasonably navigate in isolation.

### The Problem
The hardest components of creating an accurate SQL query out of natural language are the same ones we might have struggled with as newcomers to the language. Concepts like identifying foreign key relationships, breaking down the question into smaller, nested queries, and properly joining tables, are among the hardest components of SQL query generation. According to researchers, over 50% of SQL generation tests fail on schema linking and joins alone.

On top of these core components of the query, each database engine has its own syntax that may warrant mastery of in order to write a valid query. Further, in many organizations, there are many overlapping data attributes - a value is aggregated in one table and not aggregated in another, for example - as well as abbreviated column names that require tribal knowledge to use correctly.

### Measuring Success
So how close are we to solving this problem? The community has coalesced around two main leaderboards that rank the most successful approaches with labeled data set: [Spider](https://yale-lily.github.io/spider) and [BIRD](https://bird-bench.github.io/). Both leaderboards prioritize the most important metric for measuring the accuracy of any given approach to solving this problem, called Execution Accuracy (EX). This metric simply compares the generated SQL query to the labeled SQL query to determine if its a match or not. Further, SPIDER measures Exact Set Match Accuracy (EM) – did the returned result set actually answer the question, regardless of how the query was written – and BIRD offers Valid Efficiency Score (VES), a measure how performant the generated SQL query is. You can read more about each benchmark data set on their respective pages.

The Spider and BIRD datasets have proven to be authoritative, robust data sets to benchmark Text-to-SQL techniques, and even fine-tune models with. Throughout this module we will refer to these datasets and their corresponding leaderboards to demonstrate the most robust approaches to Text-to-SQL.

### State of the Art
According to the BIRD leaderboard, the state of the art for the Text-to-SQL problem sits at 60% Execution Accuracy. While that’s still well short of human performance, note that in one year we've moved from the baseline T5 model performing at 7% EM to a year later seeing EM exceed 60%. We’re excited to see how this further improves in the coming year as these models and techniques continue to be researched.

Its important to note these techniques are optimized for a single thing, which is generating the correct SQL query. These leaderboards don't assess some critical aspects to these techniques, most importantly speed. Many of these techniques demonstrate an end-to-end prompt chain speed of well over a few seconds, which many zero-shot business intelligence use cases can't tolerate. Additionally, many of them also make multiple inferences to an LLM to complete the necessary reasoning, which can drive up the cost per query considerably.

### Workshop Content
This workshop is designed to be a progression of Text-to-SQL techniques, starting with robust prompt engineering. All code is in the form of Jupyter Notebooks, hosted in SageMaker Studio. When you're ready to get started, head over to [Setup](./SETUP.md) to begin deployment of the necessary resources for this workshop.


Below is an outline of the workshop content:

* **Module 1: Advanced Prompt Engineering for Text-to-SQL.** Use Amazon Bedrock to implement some of the State-of-the-Art techniques against an Amazon Athena data set and a relational database.
* **Module 2: Retrieval Augmented Generation (RAG) for Text-to-SQL.** Leverage a FAISS in-memory vector store of data set meta data to improve query accuracy.
* **Module 3: Fine-tuning for Text-to-SQL.** Fine-tune a Titan model on the Spider Dataset to improve Text-to-SQL accuracy.
* **Module 4: Introduction to Security for Text-to-SQL.** Guard against prompt injection and SQL injection using these prompt engineering techniques.  

# Module 4: Introduction to GenAI Security in Text to SQL

**Overview of Security for Text to SQL**

In the field of data management and SQL query execution, GenAI security plays a pivotal role in safeguarding databases and ensuring robust security measures. This introduction will dive into three crucial GenAI security topics within the context of Text to SQL, where Natural Language (NL) is translated into SQL queries.

**Outline 3 approaches for security**

	* Approach 1: Avoiding Unsafe SQL Statements
	* Approach 2: Preventing Prompt Injection
	* Approach 3: Hardening Database Permissions

**Approach 1: Avoiding Unsafe SQL Statements**

GenAI Security places a strong emphasis on identifying and preventing unsafe SQL statements, particularly those that involve potentially harmful actions such as 'insert', 'update' or 'delete.' The focus here is on creating a robust framework by Prompt Engineering that actively identifies and restricts the execution of SQL statements that could compromise data integrity or privacy.

We here use Prompt Engineering to prevent unsafe SQL statements from generation or execution. Reference the example notebook for implementation.

**Approach 2: Preventing Prompt Injection**

One of the paramount concerns when handling Text to SQL conversions is the risk of prompt injection, where malicious commands can be inserted within natural language prompts. GenAI Security addresses this vulnerability by proactively preventing such injections, ensuring the integrity of the input data and safeguarding the SQL query execution process. 

For this approach, we will deploy a third party model to prevent prompt injection. Reference the example notebook for implementation. 


**Approach 3: Hardening Database Permissions**

Given that the above approaches might not fully prevent the generation and execution of unsafe SQL statements, it is recommended to restrict the database permissions without relying on the LLM. Specifically, the database roles and permissions can restrict the execution of unsafe SQL statements. Database roles are named collections of permissions granted to users. For each role, permissions can be associated with each table, specifying the set of privileges that dictate what actions the users assigned to that role can perform on that table. We can create a role for the GenAI application database connection which restricts database permissions by only allowing read operations.

There is no example notebook provided for this approach. The appropriate role for a GenAI application database connection should be created based on the use case and the specific security requirements. 



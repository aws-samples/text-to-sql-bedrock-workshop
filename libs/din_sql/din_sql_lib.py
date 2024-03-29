import sys
import json
import boto3
import sqlalchemy as sa
import logging
import botocore
import jinja2 as j
import os

# TODO
# prune imports

# initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
current_dir = os.path.dirname(__file__)

# ANTHROPIC_CLIENT = Anthropic()
JINJA_ENV = j.Environment(
    loader=j.FileSystemLoader(f"{current_dir}/prompt_templates"),
    autoescape=j.select_autoescape(
        enabled_extensions=('jinja'),
        default_for_string=True,
    )
    )

class DIN_SQL:
    def __init__(self, bedrock_model_id):
        
        self.db_un = None
        self.db_pwd = None
        self.db_host = None
        self.db_port = None
        self.db_name = None
        self.db_engine = None
        self.db_connection = None
        self.db_engine_obj = None
        self.sql_dialect = None
        self.model_id = bedrock_model_id # "anthropic.claude-v2"
        self.max_tokens_to_sample = 8000
        self.token_summary = {
            "input_tokens": 0,
            "output_tokens": 0,
        }

        self.bedrock_runtime_boto3_client = boto3.client(
            service_name='bedrock-runtime',
            )
        
        # prompts
        self.example_tag_start = '<example>'
        self.example_tag_end = '</example>'
        self.instructions_tag_start = '<instructions>'
        self.instructions_tag_end = '</instructions>'
        self.schema_linking_prompt = JINJA_ENV.get_template('schema_linking_prompt.txt.jinja')
        self.classification_prompt = JINJA_ENV.get_template('classification_prompt.txt.jinja')
        self.easy_prompt = JINJA_ENV.get_template('easy_prompt.txt.jinja')
        self.medium_prompt = JINJA_ENV.get_template('medium_prompt.txt.jinja')
        self.hard_prompt = JINJA_ENV.get_template('hard_prompt.txt.jinja')
        self.clean_query_prompt = JINJA_ENV.get_template('clean_query_prompt.txt.jinja')

    def athena_connect(self, catalog_name, db_name, s3_prefix, region=None):
        """
        Connects to an athena database.

        catalog_name:   the name of the catalog to connect to
        db_name:        the name of the database to connect to
        s3_prefix:      the prefix of the s3 bucket to use for storing athena results
        """

        region = self.bedrock_runtime_boto3_client.meta.region_name if not region else region
        athena_connection_str = f'awsathena+rest://:@athena.{region}.amazonaws.com:443/{db_name}?s3_staging_dir=s3://{s3_prefix}&catalog_name={catalog_name}'
        try:
            logger.info(f"attempting to connect to athena database with connection string: {athena_connection_str}")
            athena_engine = sa.create_engine(athena_connection_str) 
            self.db_connection = athena_engine.connect()
            self.sql_dialect = 'presto'
            logger.info("connected to database successfully.")
        except sa.exc.SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error: {e}")


    def db_connect(self, db_un, db_pwd, db_host, db_port, db_name, db_engine):
        self.db_un = db_un
        self.db_pwd = db_pwd
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_engine = db_engine
        self.sql_dialect = db_engine
        database_uri = f"{self.db_engine}://{self.db_un}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}"
        logger.info(f"attempting to connect to database with uri: {database_uri}")
        try:
            db_engine_obj = sa.create_engine(
                url=database_uri
            )
            self.db_connection = db_engine_obj.connect()
            logger.info("connected to database successfully.")
        except sa.exc.SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error: {e}")


    def reset_token_calculator(self):
        """
        Resets the token calculator to zero
        """
        self.token_summary = {
            "input_tokens": 0,
            "output_tokens": 0,
        }


    def query(self, sql_string):
        """
        Executes a query and returns the results. Attempts to fix any exceptions and try again.

        sql_string: the sql string to be executed
        returns: the results of the query
        """
        db_error=None
        try:
            logger.info(f"attempting to execute query: \n{sql_string}")
            logger.info(f"cleaned SQL: \n{sa.text(sql_string)}")
            result = self.db_connection.execute(sa.text(sql_string))
            return result.all()
        except sa.exc.SQLAlchemyError as e:
            db_error = e

        if db_error:
            logger.warning(f"Encountered SQLAlchemy error: {db_error}. Attempting to remediate.")
            revised_sql = self.revise_query_with_error(
                sql_query=sql_string, 
                error_message=db_error, 
                sql_tag_start='```sql', 
                sql_tag_end='```'
            )
            try:
                logger.info(f"revised SQL: \n{sa.text(revised_sql)}")
                new_result = self.db_connection.execute(sa.text(revised_sql))
                return new_result.all()
            except sa.exc.SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error on revised query: {e}")
                return f"SQLAlchemy error: {e}"
        
            

    def bedrock_claude_prompt_maker(self, prompt):
        """
        Checks if claude is being used and adds mandatory prompt elements if needed

        prompt: the prompt to be modified
        returns: the modified prompt
        raises: None
        side effects: adds tokens to the token calculator if claude is being used
        """
        if self.model_id.startswith("anthropic.claude"):
            new_prompt = f"\n\nHuman: {prompt}\n\nAssistant: "
            return new_prompt
        else:
            return prompt


    def hard_prompt_maker(self, test_sample_text, database, schema_links, sub_questions, sql_tag_start='```sql', sql_tag_end='```'):
        """
        Creates the hard prompt for a given database.

        :param test_sample_text:    The natural language question
        :param database:            The database name to inspect
        :return:                    The hard prompt.
        :note                       word_in_mouth for claude is: A: Let's think step by step. "{question}" can be solved by knowing the answer to the following sub-question "{sub_questions}". The SQL query for the sub-question "
        """
        prompt = self.hard_prompt.render(
            instruction_tag_start=self.instructions_tag_start,
            instruction_tag_end=self.instructions_tag_end,
            fields = self.find_fields(db_name=database),
            foreign_keys=self.find_foreign_keys(database),
            example_tag_start=self.example_tag_start,
            example_tag_end=self.example_tag_end,
            schema_links=schema_links,
            test_sample_text=test_sample_text,
            sub_questions=sub_questions,
            sql_tag_start=sql_tag_start,
            sql_tag_end=sql_tag_end
        )
        # return self.bedrock_claude_prompt_maker(prompt)
        return prompt


    def medium_prompt_maker(self, test_sample_text, database, schema_links, sql_tag_start='```sql', sql_tag_end='```'):
        """
        Creates the medium prompt for a given database.

        :param test_sample_text:    The natural language question
        :param database:            The database name to inspect
        :return:                    The medium prompt.
        :note                       word_in_mouth for claude is: SQL: {sql_tag_start}
        """
        prompt = self.medium_prompt.render(
            instruction_tag_start=self.instructions_tag_start,
            instruction_tag_end=self.instructions_tag_end,
            fields=self.find_fields(db_name=database),
            foreign_keys=self.find_foreign_keys(database),
            example_tag_start=self.example_tag_start,
            example_tag_end=self.example_tag_end,
            schema_links=schema_links,
            test_sample_text=test_sample_text,
            sql_tag_start=sql_tag_start,
            sql_tag_end=sql_tag_end
        )
        # return self.bedrock_claude_prompt_maker(prompt)
        return prompt


    def easy_prompt_maker(self, test_sample_text, database, schema_links, sql_tag_start='```sql', sql_tag_end='```'):
        """
        Creates the easy prompt for a given database.

        :param test_sample_text:    The natural language question
        :param database:            The database name to inspect
        :return:                    The easy prompt.
        :note                       word_in_mouth for claude is: SQL: {sql_tag_start}
        """
        prompt = self.easy_prompt.render(
            instruction_tag_start=self.instructions_tag_start,
            instruction_tag_end=self.instructions_tag_end,
            fields=self.find_fields(db_name=database),
            example_tag_start=self.example_tag_start,
            example_tag_end=self.example_tag_end,
            schema_links=schema_links,
            test_sample_text=test_sample_text,
            sql_tag_start=sql_tag_start,
            sql_tag_end=sql_tag_end
        )
        # return self.bedrock_claude_prompt_maker(prompt)
        return prompt


    def classification_prompt_maker(self, test_sample_text, database, schema_links):
        """
        Creates the classification prompt for a given database.

        :param test_sample_text:    The natural language question
        :param database:            The database name to inspect
        :return:                    The classification of the query required to answer the question.
        :note:                      word_in_mouth for claude here is: A: Let’s think step by step. 
        """

        prompt = self.classification_prompt.render(
            instruction_tag_start=self.instructions_tag_start,
            instruction_tag_end=self.instructions_tag_end,
            fields=self.find_fields(db_name=database),
            foreign_keys=self.find_foreign_keys(database),
            example_tag_start=self.example_tag_start,
            example_tag_end=self.example_tag_end,
            schema_links=schema_links,
            test_sample_text=test_sample_text,
            classification_start='<label>',
            classification_end='</label>'
        )
        # return self.bedrock_claude_prompt_maker(prompt)
        return prompt


    def schema_linking_prompt_maker(self, test_sample_text, database):
        """
        Creates the schema linking prompt for a given database.

        :param test_sample_text:    The natural language question
        :param database:            The database name to inspect
        :return:                    The schema linking prompt.
        :note                       word_in_mouth for claude here is: A. Let’s think step by step. In the question "{question}", we are asked: 
        """
        prompt = self.schema_linking_prompt.render(
            instruction_tag_start=self.instructions_tag_start,
            instruction_tag_end=self.instructions_tag_end,
            example_tag_start=self.example_tag_start,
            example_tag_end=self.example_tag_end,
            fields=self.find_fields(db_name=database),
            foreign_keys=self.find_foreign_keys(database),
            test_sample_text=test_sample_text,
            schema_links_start='<links>',
            schema_links_end='</links>'
        )
        # return self.bedrock_claude_prompt_maker(prompt)
        return prompt


    def find_foreign_keys(self, db_name):
        """
        Finds the foreign keys of a given database.
        :param db_name: The name of the database.
        :return: A string of the foreign keys.
        """
        inspector = sa.inspect(self.db_connection)
        schemas = inspector.get_schema_names()
        output = "["
        if db_name and db_name in schemas:
            for table_name in inspector.get_table_names(schema=db_name):
                for fk in inspector.get_foreign_keys(table_name):

                    output += (
                        f"{table_name}.{fk['constrained_columns'][0]} = {fk['referred_table']}.{fk['referred_columns'][0]},"
                    )
        else:
            for schema in schemas:
                if schema != 'information_schema':
                    for table_name in inspector.get_table_names(schema=schema):
                        for fk in inspector.get_foreign_keys(table_name):

                            output += (
                                f"{table_name}.{fk['constrained_columns'][0]} = {fk['referred_table']}.{fk['referred_columns'][0]},"
                            )
        
        output = output[:-1] + "]"
        return output if len(output) > 2 else "[]"


    def find_fields(self, db_name=None):
        """
        Finds the fields of a given database.
        :param db_name: The name of the database. 
        :return: A string of the fields.
        """
        inspector = sa.inspect(self.db_connection)
        schemas = inspector.get_schema_names()
        output = ""
        if db_name and db_name in schemas:
            logger.info(f"database name specified and found, inspecting only '{db_name}'")
            tables = inspector.get_table_names(schema=db_name)
            for table_name in tables:
                output += f"Table {table_name}, columns = ["
                for column in inspector.get_columns(table_name, schema=db_name):
                    output += f"{column['name']},"
                output = output[:-1]
                output += "]\n"
        else:
            logger.info(f"No database specified or not found in schemas {schemas}. Inspecting everything.")
            for schema in schemas:
                if schema != 'information_schema':
                    tables = inspector.get_table_names(schema=schema)
                    print(f"Tables:\n{tables}")
                    for table_name in tables:
                        print(f"Processing table:\n{table_name}")
                        output += f"Table {table_name}, columns = ["
                        for column in inspector.get_columns(table_name, schema=schema):
                            output += f"{column['name']},"
                        output = output[:-1]
                        output += "]\n"
        return output if len(output) > 2 else "[]"


    def find_primary_keys(self, db_name=None):
        """
        Finds the primary keys of a given database.
        :param db_name: The name of the database.
        :return: A string of the primary keys.
        """
        inspector = sa.inspect(self.db_connection)
        schemas = inspector.get_schema_names()
        output = ""
        if db_name and db_name in schemas:
            logger.info(f"database name specified and found, inspecting PKs only in '{db_name}'")
            tables = inspector.get_table_names(schema=db_name)
            for table_name in tables:
                logger.info(f"getting PKs for table {table_name}")
                for pk in inspector.get_pk_constraint(table_name, schema=db_name):
                    if type(pk) == dict and 'constrained_columns' in pk.keys():
                        output += f"{table_name}.{pk['constrained_columns'][0]},"
            output = output[:-1]
            output += "]\n"
        else:
            for schema in schemas:
                if schema != 'information_schema':
                    for table_name in inspector.get_table_names(schema=schema):
                        logger.info(f"getting PKs for table {table_name}")
                        for pk in inspector.get_pk_constraint(table_name, schema=schema):
                            if type(pk) == dict and 'constrained_columns' in pk.keys():
                                output += f"{table_name}.{pk['constrained_columns'][0]},"
            output = output[:-1]
            output += "]\n"
        return output if len(output) > 2 else "[]"


    def debugger(self, test_sample_text, database, sql, sql_tag_start='```sql', sql_tag_end='```',sql_dialect='MySQL'):
        """
        Generates a prompt for cleaning the given SQL statement using the given sql_dialect.

        :param test_sample_text:    The test sample text.
        :param database:            The name of the database.
        :param sql:                 The SQL statement.
        :param sql_tag_start:       The start tag for the SQL statement.
        :param sql_tag_end:         The end tag for the SQL statement.
        :param sql_dialect:         The SQL dialect.

        :return: The prompt.
        """
        fields = self.find_fields(db_name=database)
        fields += "Foreign_keys = " + self.find_foreign_keys(database) + "\n"
        fields += "Primary_keys = " + self.find_primary_keys(database)

        prompt = self.clean_query_prompt.render(
            instruction_tag_start=self.instructions_tag_start,
            instruction_tag_end=self.instructions_tag_end,
            example_tag_start=self.example_tag_start,
            example_tag_end=self.example_tag_end,
            revised_qry_start=sql_tag_start,
            revised_qry_end=sql_tag_end,
            sql_dialect=sql_dialect,
            meta_data=fields,
            question=test_sample_text,
            sql_query=sql
        )
        # return self.bedrock_claude_prompt_maker(prompt)
        return prompt


    def llm_generation(self, prompt, stop_sequences=[],word_in_mouth=None):
        """
        Invokes the model with the given prompt

        :param prompt:          prompt for model
        :param stop_sequences:  list of stop sequence strings for model to use
        :param word_in_mouth:   start the assistant's response
        
        returns: model output

        """
        results=None
        try:
            if self.model_id.startswith('anthropic'):

                user_message =  {"role": "user", "content": prompt}
                messages = [user_message]
                if word_in_mouth:
                    messages.append({
                        "role": "assistant",
                        "content": word_in_mouth,
                    })
                response = self.bedrock_runtime_boto3_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "messages": messages,
                        "temperature": 0,
                        "max_tokens": self.max_tokens_to_sample,
                        "stop_sequences": stop_sequences,
                        })
                )
                response_dict = json.loads(response.get('body').read().decode("utf-8"))
                results = response_dict["content"][0]["text"]
            else:
                response = self.bedrock_runtime_boto3_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "inputText": prompt,
                        "textGenerationConfig": {
                            # "maxTokenCount": 4096,
                            # "stopSequences": [],
                            "temperature":0,
                            "topP":1
                            }
                        })
                )
                # need to add to token count for other models
                results = json.loads(response['body'].read())['results'][0]['outputText']
            logger.info(f"Successfully invoked model {self.model_id}")
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error in invoking model {self.model_id}: {e}")
        return results


    def debugger_generation(self, prompt):
        """
        Cleans a SQL statement for any errors based on the syntax requested.
        :param prompt: prompt with SQL statement
        returns: 
        """
        results=None
        try:
            if self.model_id.startswith('anthropic'):
                user_message =  {"role": "user", "content": prompt}
                messages = [user_message]
                response = self.bedrock_runtime_boto3_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "messages": messages,
                        "temperature": 0,
                        "max_tokens": self.max_tokens_to_sample,
                        "stop_sequences": [self.example_tag_end],
                        })
                )
                response_dict = json.loads(response.get('body').read().decode("utf-8"))
                results = response_dict["content"][0]["text"]
            else:
                response = self.bedrock_runtime_boto3_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "inputText": prompt,
                        "textGenerationConfig": {
                            "maxTokenCount": 350,
                            # "stopSequences": [],
                            "temperature":0,
                            # "topP":1
                            }
                        })
                )
                # need to add to token count for other models
                results = json.loads(response['body'].read())['results'][0]['outputText']
            logger.info(f"Successfully invoked model {self.model_id}")
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error in invoking model {self.model_id}: {e}")
        return results


    def revise_query_with_error(self, sql_query, error_message, sql_tag_start='```sql', sql_tag_end='```'):
        """
        Revises a SQL query with an error message.
        :param sql_query: The SQL query to revise.
        :param error_message: The error message to revise the query with.
        :return: The revised SQL query.
        """
        retry_sql = self.llm_generation(
                f"""Human:
                Please provide a new SQL query that correctly fixes the invalid SQL statement below using the SQL Error information.
                Only provide one new SQL query in your response and use begin and end tags of "{sql_tag_start}" and "{sql_tag_end}" respectively:
                Invalid SQL Statement: {sql_query}
                SQL Error: {error_message}

                Assistant:
                """
            )
        logger.info(retry_sql)

        return retry_sql.split(sql_tag_start)[1].split(sql_tag_end)[0]


    def get_sql(self, question, db_name, schema_links, classification):
        """
        Generates SQL for the given question.

        :param question:        The question to generate SQL for.
        :param db_name:         The name of the database.
        :param schema_links:    The schema links.
        :param classification:  The classification of the question.

        :return: The generated SQL.
        """
        logger.info(f"question is classifed as {classification}")
        logger.info(f"question asked: {question}")
        logger.info(f"schema_links: {schema_links}")
        logger.info(f"database name: {db_name}")
        sql_tag_start='```sql'
        sql_tag_end='```'
        SQL = None
        try:
            if classification == 'EASY':
                SQL = self.llm_generation(
                    prompt=self.easy_prompt_maker(
                        test_sample_text=question, 
                        database=db_name, 
                        schema_links=schema_links,
                        sql_tag_start=sql_tag_start,
                        sql_tag_end=sql_tag_end,
                        word_in_mouth=f"SQL: {sql_tag_start}"
                        ),
                    stop_sequences=[self.example_tag_end])
            elif classification == 'NON-NESTED':
                SQL = self.llm_generation(
                    prompt=self.medium_prompt_maker(
                        test_sample_text=question, 
                        database=db_name, 
                        schema_links=schema_links,
                        sql_tag_start=sql_tag_start,
                        sql_tag_end=sql_tag_end),
                    stop_sequences=[self.example_tag_end],
                    word_in_mouth=f"SQL: {sql_tag_start}"
                    )
            elif classification == 'NESTED':
                if classification.find('questions = [') != -1:
                    sub_questions = classification.split('questions = ["')[1].split('"]')[0]
                    SQL = self.llm_generation(
                        prompt=self.hard_prompt_maker(
                            test_sample_text=question, 
                            database=db_name, 
                            schema_links=schema_links,
                            sql_tag_start=sql_tag_start,
                            sql_tag_end=sql_tag_end, 
                            sub_questions=sub_questions),
                        stop_sequences=[self.example_tag_end],
                        word_in_mouth=f'''A: Let's think step by step. "{question}" can be solved by knowing the answer to the following sub-question "{sub_questions}". The SQL query for the sub-question "
                        '''
                        )
                else:
                    logger.info(f"Question was classified as NESTED but no sub_questions were found. Assuming NON-NESTED instead")
                    SQL = self.llm_generation(
                        prompt=self.medium_prompt_maker(
                            test_sample_text=question, 
                            database=db_name, 
                            schema_links=schema_links,
                            sql_tag_start=sql_tag_start,
                            sql_tag_end=sql_tag_end),
                        stop_sequences=[self.example_tag_end],
                        word_in_mouth=f"SQL: {sql_tag_start}"
                        )
            else:
                logger.error(f"Unknown classification: {classification}")
        except Exception as e:
            logger.error(f"Error in generating SQL: {e}")
            SQL = "SELECT"

        try:
            # SQL = SQL.split("SQL: ")[1]
            SQL = SQL.split('```sql')[-1].split('```')[0]
        except Exception as e:
            logger.error(f"SQL slicing error: {e}")
            SQL = "SELECT"
            
        logger.info(f"SQL before debugging: \n{SQL}")
        debugged_SQL = self.debugger_generation(
            prompt=self.debugger(question, db_name, SQL,sql_dialect=self.sql_dialect)
            ).replace("\n", " ")
        SQL = debugged_SQL.split('```sql')[1].split('```')[0].strip()
        return SQL
    
    def find_tables(self,db_name): 
       
        inspector = sa.inspect(self.db_connection)
        schemas = inspector.get_schema_names()
        output = []

        for schema in schemas:
            if schema == db_name:
                for table_name in inspector.get_table_names(schema=schema):
                    output.append(table_name)
        return output  

    def get_schema(self,db_name,input_table_name): 
       
        inspector = sa.inspect(self.db_connection)
        schemas = inspector.get_schema_names()
        output = ""

        for schema in schemas:
            if schema == db_name:
                for table_name in inspector.get_table_names(schema=schema):
                    if  table_name ==  input_table_name :
                        for column in inspector.get_columns(table_name, schema=schema):    
                            output += f"{column['name']}" + "|"                  
          
        return output

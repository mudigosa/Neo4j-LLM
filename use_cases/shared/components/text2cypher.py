class Text2Cypher():
    def __init__(self, llm, database, schema: bool, cypher_examples: str):
        self.llm = llm
        self.database = database
        self.cypher_examples = cypher_examples
        if schema:
            self.schema = database.schema

    def get_system_message(self):
        system = """
        Task: Generate Cypher queries to query a Neo4j graph database.
        Instructions:
        Use only the provided relationship types and properties.
        Do not use any other relationship types or properties that are not provided.
        """
        if self.schema:
            system += f"""
            If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.
            Schema:
            {self.schema}
            """
        if self.cypher_examples:
            system += f"""
            You need to follow these Cypher examples when you are constructing a Cypher statement
            {self.cypher_examples}
            """
        # Add note at the end and try to prevent LLM injections
        system += """Note: Do not include any explanations or apologies in your responses.
                     Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
                     Do not include any text except the generated Cypher statement.
                     """
        return system

    def construct_cypher(self, question):
        messages = [
            {"role": "system", "content": self.get_system_message()},
            {"role": "user", "content": question},
        ]
        cypher = self.llm.generate(messages)
        return cypher

    def run(self, question):
        cypher = self.construct_cypher(question)
        print(cypher)
        try:
            return {"output": self.database.query(cypher),
                    "generated_cypher": cypher}
        except Exception as e:
            print(e)
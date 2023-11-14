from data_analytics.helper.base import BaseGPT


class FileGPT(BaseGPT):
    def __init__(self,user_id,project_id,input_prompt,api_key,namespace,template,model_name,temperature,filter=None, **kwargs):
        super().__init__(user_id=user_id, project_id=project_id, api_key=api_key, model_name=model_name, temperature=temperature, namespace=namespace)
        self.filter=filter
        self.template=template
        self.question=input_prompt
        self.pinecone_index = self._initiate_pinecone_index()

    def _create_prompt(self, question, context_list):
        role=self.template.get("role","")
        goal=self.template.get("goal","")
        examples=self.template.get("examples","")
        output_format=self.template.get("output_format","")

        if examples and output_format:
            prompt = f"{goal} \n####\n EXAMPLES: {examples} \n####\n QUESTION: {question} \n####\n CONTEXT: {context_list} \n####\n OUTPUT FORMAT: {output_format}"
        elif examples:
            prompt = f"{goal} \n####\n EXAMPLES: {examples} \n####\n QUESTION: {question} \n####\n CONTEXT: {context_list}"
        elif output_format:
            prompt = f"{goal} \n####\n QUESTION: {question} \n####\n CONTEXT: {context_list} \n####\n OUTPUT FORMAT: {output_format}"
        else:
            prompt = f"{goal} \n####\n QUESTION: {question} \n####\n CONTEXT: {context_list}"

        messages= [
                    {
                    "role": "system",
                    "content": f"""{role}"""
                    },
                    {
                    "role": "user",
                    "content": f"""{prompt}"""
                    }
                ]
        return messages

    def get_response(self, stream:bool=True):
        embbedding = self._get_embedding(self.question)
        context, metadata = self._query_pinecone(pinecone_index=self.pinecone_index, vector=embbedding, filter=self.filter)
        messages = self._create_prompt(question=self.question, context_list=context)
        if stream:
            for result in self._make_openai_call(messages=messages, metadata=metadata, stream=stream):
                yield result
        else:
            return self._make_openai_call(messages=messages, metadata=metadata, stream=stream)
        
    def get_selected_response(self, chunks, custom_chunk=None, stream:bool=True):
        context_list = [ x['text'] for x in chunks]
        if custom_chunk:
            context_list.append(f"TOPIC: {custom_chunk['topic']}\n\nSUBTOPIC: {custom_chunk['sub_topic']}\n\nTEXT: {custom_chunk['text']}")
            
        messages = self._create_prompt(question=self.question, context_list=context_list)
        if stream:
            for result in self._make_openai_call(messages=messages, metadata=chunks, stream=stream):
                yield result
        else:
            return self._make_openai_call(messages=messages, metadata=chunks, stream=stream)
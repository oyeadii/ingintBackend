import ast
import json
import openai
import pinecone
import requests
from django.conf import settings


class BaseGPT:
    def __init__(self,user_id,project_id,api_key,namespace,model_name,temperature,max_length=None):
        openai.api_key=api_key
        self.api_key=api_key
        self.user_id=user_id
        self.namespace=namespace
        self.model_name=model_name
        self.project_id=project_id
        self.temperature=temperature
        self.max_length=max_length

    def _get_embedding(self, text):
        result = openai.Embedding.create(model=settings.MODEL_EMBEDDING, input=text)
        return [x["embedding"] for x in result["data"]][0]
    
    def _initiate_pinecone_index(self):
        pinecone.init(api_key=settings.PINECONE_KEY, environment=settings.PINECONE_ENV)
        pinecone_index = pinecone.Index(settings.PINECONE_INDEX_NAME)
        return pinecone_index
    
    def _format_metadata(self, metadata):
        result_list = []
        for item in metadata:
            coordinates = item["metadata"].get('coordinates', None)
            if coordinates is not None:
                coordinates = ast.literal_eval(coordinates)

            entry = {
                'chunk_type': "queried",
                'chunk_id': item["metadata"].get('chunk_id', None),
                'page_number': item["metadata"].get('page_number', None),
                'file_name': item["metadata"].get('file_name', None),
                'text': item["metadata"].get('text', None),
                'coordinates': coordinates,
                'text_as_html': item["metadata"].get('text_as_html', None),
                'image_string': item["metadata"].get('image_path', None),
                'selected': True
            }
            result_list.append(entry)
        return result_list
    
    def _query_pinecone(self, pinecone_index, vector, top_k=4, filter=None):
        query_args = {
            'vector': vector,
            'top_k': top_k,
            'include_metadata': True,
            'namespace': self.namespace
        }
        if filter:
            query_args['filter'] = filter

        pinecone_result = pinecone_index.query(**query_args)
        contexts = [x['metadata']['text'] for x in pinecone_result['matches']]
        metadata = self._format_metadata(metadata=pinecone_result["matches"])
        return [contexts, metadata]
    
    def _make_openai_call(self, messages, metadata=None, stream:bool=True):
        request_payload = {
                    'model': self.model_name,
                    'temperature': self.temperature,
                    'messages': messages,
                    'stream': stream,
                }
        if self.max_length:
            request_payload["max_tokens"] = self.max_length

        response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json=request_payload,
                stream=stream,
            )
        if stream == False:
            res=json.loads(response.content.decode('utf-8'))
            res = res['choices'][0].get('message').get('content')
        else:
            for chunk in response.iter_lines():
                if chunk:
                    payloads = chunk.decode().split("\n\n")
                    for payload in payloads:
                        if '[DONE]' in payload:
                            break
                        if payload.startswith("data:"):
                            data = json.loads(payload.replace("data:", ""))
                            yield f"data: {json.dumps(data)}\n\n"
            if metadata:
                yield 'data: [METADATA]\n\n'
                yield f'data: {json.dumps(metadata)}\n\n'
            yield 'data: [DONE]\n\n'

        if stream==False:
            if metadata:
                return res, metadata
            return res
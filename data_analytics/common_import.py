import re
import json
import uuid
import openai
import pinecone
import requests
from django.conf import settings
from langchain.llms.openai import OpenAI
from wordcloud import WordCloud, STOPWORDS
from custom_lib.renderer import DateTimeEncoder
from custom_lib.helper import extract_text_from_file
from user.models import ProjectDataCategory, ProjectData
from custom_llama_index import LLMPredictor,PromptHelper,Document,GPTPineconeIndex


class PineconeManager:
    def __init__(self, openai_api_key):
        openai.api_key=openai_api_key
        pinecone.init(api_key=settings.PINECONE_KEY, environment=settings.PINECONE_ENV)
        self.api_key=openai_api_key
        self.index_name = settings.PINECONE_INDEX_NAME
        self.pinecone_index = self.construct_index()

    def construct_index(self):
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(name=self.index_name, dimension=1536, metric="euclidean", pod_type="p1")
        return pinecone.Index(self.index_name)

    def add_files_to_index(self, text_list, metadata_list, namespace):
        max_input_size = settings.MODEL_MAX_INPUT_SIZE
        num_outputs = settings.MODEL_NUM_OUTPUTS
        max_chunk_overlap = settings.MODEL_MAX_CHUNK_OVERLAP
        chunk_size_limit = settings.MODEL_CHUNK_SIZE_LIMIT
        llm_predictor = LLMPredictor(llm=OpenAI(openai_api_key=self.api_key))
        prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)
        documents = []

        for idx, (text, metadt) in enumerate(zip(text_list, metadata_list)):
            document = Document(text=text, doc_id=metadt["doc_id"], doc_metadata={"file_name": metadt["file_name"], "category_id": metadt["category_id"]})
            documents.append(document)
        index = GPTPineconeIndex(documents,
                                 pinecone_index=self.pinecone_index,
                                 llm_predictor=llm_predictor,
                                 prompt_helper=prompt_helper,
                                 pinecone_kwargs={"namespace": namespace})
        return "success"

    def single_delete(self, file_id, namespace):
        self.pinecone_index.delete(filter={"doc_id": {"$eq": file_id}}, namespace=namespace)
        return "success"

    def complete_delete(self, namespace):
        self.pinecone_index.delete(deleteAll='true', namespace=namespace)
        return "success"

    def update_index_metadata(self, id_list, metadata, namespace):
        for id in id_list:
            self.pinecone_index.update(id=id, namespace=namespace, set_metadata=metadata)
        return "success"


class FileTagger:
    def __init__(self, api_key):
        self.api_key = api_key
        self.stopwords = STOPWORDS
    
    def generate_wordcloud(self, text):
        wordcloud = WordCloud(stopwords=self.stopwords, background_color='white').generate(text)
        word_frequencies = wordcloud.words_
        sorted_words = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)
        num_common_words = 50
        most_common_words = [word for word, count in sorted_words[:num_common_words]]
        return most_common_words
    
    def classify_text(self, text, categories):
        most_common_words = self.generate_wordcloud(text)
        messages = [
            {
                "role": "system",
                "content": "You are a very good text classifier."
            },
            {
                "role": "user",
                "content": f"For the given most common words from a large file check them and classify the file into one of the following categories.\nCATEGORIES: {categories}\nMOST COMMON WORDS: {most_common_words}\nReturn the category and make sure to prefix the requested category with '```' exactly and suffix it with '```' exactly to get the answer."
            }
        ]
     
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': "gpt-3.5-turbo",
                'temperature': 0,
                'messages': messages
            }
        )

        resp = json.loads(response.content)
        resp = resp["choices"][0]["message"]["content"]
        pattern = r"```(.*?)```"
        matches = re.findall(pattern, resp)
        if matches:
            category = matches[0].lower().strip()
            valid_categories = [item.lower().strip() for item in categories]
            if category in valid_categories:
                return category.capitalize()
            else:
                return "Miscellaneous"
        else:
            return "Miscellaneous"


class FileAnalyzer:
    def __init__(self, project, api_key, category_dict, sub_use_case=None):
        self.project = project
        self.api_key = api_key
        self.sub_use_case = sub_use_case
        self.category_dict = category_dict
        self.file_tagger = FileTagger(api_key=api_key)
        self.pinecone_manager = PineconeManager(openai_api_key=self.api_key)
        self.categories = list(ProjectDataCategory.objects.values_list('name', flat=True))

    def analyze_file(self, file, category_id=1, is_general=0, classify=True):
        file_id = str(uuid.uuid4())
        filename = file.name
        file_content = file.read()
        text_content = extract_text_from_file(file_content, filename)

        if classify:
            category = self.file_tagger.classify_text(text=text_content, categories=self.categories[1:])
            tagObj = ProjectDataCategory.objects.filter(name__iexact=category)
            if not tagObj.exists():
                category_id = 1
            else:
                category_id = tagObj.first().id
            
        metadata = {"file_name": filename, "doc_id": file_id, "category_id": category_id}
        fileObj = ProjectData(data_id=file_id, name=filename, category_id=category_id, project=self.project, is_general=is_general)
        fileObj.save()
        self.pinecone_manager.add_files_to_index(text_list=[text_content], metadata_list=[metadata], namespace=self.project.namespace)
        return "success"
    

def upload_project_data(api_key, project, sub_use_case, file_name, data, is_general=0):
        categories = list(ProjectDataCategory.objects.values_list('name', flat=True))
        file_tagger = FileTagger(api_key=api_key)
        category = file_tagger.classify_text(text=str(data), categories=categories[1:])
        tagObj = ProjectDataCategory.objects.filter(name__iexact=category)
        if not tagObj.exists():
            category_id = 1
        else:
            category_id = tagObj.first().id

        dataObj = ProjectData(
            project=project,
            sub_use_case=sub_use_case,
            category_id=category_id,
            name=file_name,
            data_id=str(uuid.uuid4()),
            extra_data=json.dumps(data, cls=DateTimeEncoder),
            is_general=is_general
        )
        return dataObj 
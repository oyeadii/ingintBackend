import json
import numpy as np
import pandas as pd
from django.conf import settings
from user.models import ProjectData
from skimage.measure import label, regionprops
from data_analytics.helper.base import BaseGPT
from data_analytics.prompts.trend_analysis_prompts import TREND_USER_PROMPT


class TrendAnalysisHelper:
    def __init__(self, uploaded_file):
        self.uploaded_file=uploaded_file

    def get_excel_sheets(self):
        xl = pd.ExcelFile(self.uploaded_file)
        return xl.sheet_names
    
    def get_tables(self, sheet_name):
        tables = []
        df = pd.read_excel(self.uploaded_file,sheet_name=sheet_name ,header=None)
        binary_rep = np.array(df.notnull().astype('int'))
        list_of_dataframes = []
        l = label(binary_rep)
        for s in regionprops(l):
            list_of_dataframes.append(df.iloc[s.bbox[0]:s.bbox[2],s.bbox[1]:s.bbox[3]])
        for i in range(len(list_of_dataframes)):
            if len(list_of_dataframes[i])>1:
                tables.append(list_of_dataframes[i])
        for i in range(len(tables)):
            for j in list(tables[i].columns):
                if all(tables[i][j].isnull()) == True:
                    tables[i].drop(j,axis=1,inplace=True)
            tables[i] = tables[i].loc[:,tables[i].isnull().mean()<0.5]
            perc = 75.0 
            min_count =  int(((100-perc)/100)*tables[i].shape[1] + 1)
            tables[i].dropna(axis=0,thresh=min_count,inplace=True)
            tables[i].reset_index(inplace=True)
            tables[i].drop('index',axis=1,inplace=True)
            tables[i].rename(columns=tables[i].iloc[0], inplace = True)
            tables[i].drop(0,axis=0,inplace=True)
        return tables
    
    def get_columns(self, table):
        cols=table.iloc[:,0].values
        return cols
    
    def get_x_axis_columns(self, table):
        cols=table.columns.tolist()
        return cols[1:]

    def get_clean_list(self, table):
        table = table.T
        table.columns = table.iloc[0].values
        table = table.iloc[1:,:]
        table["year"] = list(table.index)
        li = table.to_dict('list')
        return li
    

class TrendGPT(BaseGPT):
    def __init__(self,user_id,project_id,api_key,namespace,model_name,temperature,filter="", **kwargs):
        super().__init__(user_id=user_id, project_id=project_id, api_key=api_key, model_name=model_name, temperature=temperature, namespace=namespace)
        self.filter=filter
        self.pinecone_index = self._initiate_pinecone_index()
        self.content = TREND_USER_PROMPT
    
    def get_context(self, question):
        embbedding = self.get_embedding(question, settings.MODEL_EMBEDDING)[0]
        query_result = self.query_pinecone(embbedding)
        context = query_result[0]
        return context
    
    def _create_prompt(self, question):
        embbedding = self._get_embedding(question)
        context, metadata = self._query_pinecone(pinecone_index=self.pinecone_index, vector=embbedding, filter=self.filter)
        prompt_start = "Context information is below. \n####\n"+"CONTEXT: "
        prompt_end = f"\n\nGiven the context information and not prior knowledge, answer the question: {question}. Provide me in Proper Format and Points such as bullet or numbered or underlining the important words. \n####\nANSWER: "
        # prompt = (prompt_start +f"{context} \n####\n" +prompt_end)
        prompt = f"{context}"
        return prompt

    def run_trend_analysis(self, question, summary, content=None, columns=None):
        prompt= ""
        if columns:
            prompt+=f"Fact/Trend: {summary}"
            question= question.replace("{category}", str(columns))

        prompt +=f"\nContext/Causes:"+ self._create_prompt(question)
        messages= [
                    {
                    "role": "system",
                    "content": content if content!=None else self.content
                    },
                    {
                    "role": "user",
                    "content": f"""{prompt}"""
                    }
                ]
        
        for result in self._make_openai_call(messages=messages):
            yield result

    def run_trend_summary(self, content, file_id, sheet_name, table_id, commentary_type):
        """
            Generate a financial summary report based on the provided data.

            Args:
                self: The instance of the class.
                file_id (int): The ID of the financial data file to analyze.

            Returns:
                A generator yielding data for the financial summary report.

            Description:
            This method retrieves financial data from a database, calculates key metrics, and generates a summary report.
            The report includes historical and forecasted data, highlighting factors impacting EBITDA.
            The output is structured with two sentences, one for historical EBITDA and one for forecasted EBITDA,
            listing the factors impacting EBITDA in descending order of "ppt change" (percentage point change).

            Example:
            -Historically, EBITDA margin has grown over FY20-22A by (+5ppt). Growth appears linked to a reduction
            in staff and member costs (-4ppt), direct costs (-1ppt), and other indirect costs (-1ppt).
            -In the forecast period, EBITDA margin is projected to grow by +6ppt, with reductions across other
            indirect costs (-4ppt), staff and member costs (-2ppt), and direct costs (-1ppt). This will be partially
            offset by an increase in bonus (+5ppt).
        """
        try:
            file_obj = ProjectData.objects.get(id=file_id)
        except ProjectData.DoesNotExist:
            yield f"data:error:No data found\n\n"
        try:
            dt = json.loads(file_obj.extra_data)
            dt = dt["all_data"]
            sheet_data=dt.get(sheet_name,[])
            data_list=[]
            columns=[]
            x_axis_value=[]
            for table in sheet_data:
                if table["table_id"] == table_id:
                    data_list=table.get("data_list", [])
                    columns=table.get("columns", [])
                    x_axis_value=table.get("x_axis_value",[])

            df = pd.DataFrame(data_list)
            columns=columns
            df = df[columns]
            # Add the year column as the index
            df["Year"] = x_axis_value
            df.set_index("Year", inplace=True)
            
            fact = ""
            if commentary_type=='revenue_trends':
                fact += f"Dataframe containing Revenue information over different years: \n{df.to_json()}\n"
            
            percentage_contributions = (df.T / df.sum(axis=1)).T * 100
            # Generate language statements using df.iterrows()
            for index, row in df.iterrows():
                prompt = f"In {index},"
                for col, _ in row.items():
                    prompt += f" {col} was {percentage_contributions.at[index, col]:.2f}%,"
                fact+=prompt
          
            messages= [{
                        "role": "system",
                        "content": content
                        },
                        {
                        "role": "user",
                        "content": f"""Fact: {fact}"""
                        }
                    ]
            
            response = ""
            for payload in self._make_openai_call(messages=messages):
                if '[DONE]' in payload:
                    break
                if payload.startswith("data:"):
                    data = json.loads(payload.replace("data:", ""))
                    response += data["choices"][0].get('delta',{}).get('content','')

            for table in sheet_data:
                if table["table_id"] == table_id:
                    table["summary"] = response

            file_obj.extra_data=json.dumps({"all_data": dt})
            file_obj.save()
            res_str = response.splitlines()
            for sentence in res_str:
                words = sentence.split()
                for word in words:
                    data = json.dumps({'choices': [{'delta': {'content': f"{word} "}}]})
                    yield f'data: {data}\n\n'
                data = json.dumps({'choices': [{'delta': {'content': f"\n"}}]})
                yield f'data: {data}\n\n'
        except TypeError:
            # raise Exception(13002)
            yield f"data:error:Please provide only numeric data in the file to calculate the ppt change.\n\n"
        yield 'data: [DONE]\n\n'
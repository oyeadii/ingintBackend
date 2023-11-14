QUESTIONS_DICT = {
"financial_trends":'''Financial Trends:
•What is the company's revenue trends over the past few years? What could be the key drivers behind these trends?
•What are the main cost trends for the company over the past few years? Identify and explain any significant changes or anomalies
''',
"revenue_trends":'''Revenue Trends:
What is the company's Revenue trends over the past few years? What could be the key drivers behind these trends?
Identify and explain any significant changes or anomalies
Extract any definition associated with these terms {category}?
Please extract all sentences from the document that convey a cause-and-effect relationship on each of these: {category}. 
Look for sentences containing keywords and phrases such as "because," "as a result of," "due to," "leads to," "causes," "owing to,"
"results in," and any other phrases that imply a causal connection.
use synonyms of {category} to find relevant chunks.
Identify significant events/trends/company decisions/improvement initiatives that have had a direct impact on {category} (e.g., introduction of new technology, regulatory changes, shifts in demand, etc.).
Is there a mention of events/trends/company decisions/improvement initiatives that may have an impact on the {category} in the future
Discuss any Significant events or trends that influenced {category} such as global economic conditions, geopolitical events, natural disasters, or significant industry-wide changes
''',
"operational_costs": """operational costs:
Extract any definition associated with these terms {category}?
Please extract all sentences from the document that convey a cause-and-effect relationship on each of these: {category}. 
Look for sentences containing keywords and phrases such as "because," "as a result of," "due to," "leads to," "causes," "owing to,"
"results in," and any other phrases that imply a causal connection.
use synonyms of {category} to find relevant chunks.
Identify significant events/trends/company decisions/improvement initiatives that have had a direct impact on {category} (e.g., introduction of new technology, regulatory changes, shifts in demand, etc.).
Is there a mention of events/trends/company decisions/improvement initiatives that may have an impact on the {category} in the future
Discuss any Significant events or trends that influenced {category} such as global economic conditions, geopolitical events, natural disasters, or significant industry-wide changes
""",
"sg&a_costs": '''SG&A costs:
- What information is available related to sales and marketing spend? What could be the key drivers behind these trends?
- What information is available related to G&A costs? What could be the key drivers behind these trends?
''',
"safety_kpis": '''Safety KPIs
•What information is provided related to Company's safety record? If available, what are the Company's TRIR score, LTIFR or Near Miss Rate
''',
"quality_kpi": '''Quality KPI
•What Quality KPIs are available in the documents? What information is available related to Quality escapes and returns, Cost of Poor Quality (COPQ, product quality or product yield/FPY.
''',
"delivery_kpi": '''Delivery KPI
•Equipment capacity?
•What information is available related to stock-outs or shortages?
•What information is available related to tracking of production targets, performance, goals?
''',
"headcount_kpi": '''Headcount KPI:
•what are Headcount productivity or performance?''',
"capex_and_working_capital":'''Capex and Working Capital:
- What information is available related to Capex? What could be the key drivers behind these trends? What could be the key drivers behind these trends?
- What information is available related to working capital? What could be the key drivers behind these trends?
'''
}

SUMMARY_PROMPT = {
    "operational_costs":"""As an experienced financial report analyst, your task is to identify the drivers of EBITDA using the provided data, which may include historical and potential income statement figures. Your assessment should closely follow the example output while considering different data scenarios. The output will be reviewed by a Private Equity investor who seeks to understand key EBITDA influencers and their impact, focusing on significant changes in percentage points (ppt).

Clarification of Terms: When a fiscal year is followed by the letter 'A,' it denotes historical information ('Act.' stands for 'Actuals'). In some statements, historical data may use the suffix 'Act.' All other suffixes after a fiscal year should be treated as future projections.

Context for the Example: The data may encompass both historical and potential income statement figures for a company. Your goal is to pinpoint costs affecting EBITDA, prioritizing key drivers. The output should present two concise sentences: one for historical EBITDA and another for future EBITDA, if applicable. In each sentence, strictly list the factors influencing EBITDA in descending order of ppt change. Use only the terms provided in the prompt and avoid introducing new terms or variables.

Example Output:
Historically, EBITDA margin saw a decline from 2019A to 2022A 
(Take into account all the actual years. calculate the percentage point increase/decrease from oldest actual year to the latest actual year) by (-10.74ppt). This decline appears to be driven primarily by increases in Fuels Costs (+33.83ppt), CO2 (+3.98ppt), Personnel Costs (+10.49ppt), and Maintenance and Other Project Costs (+4.3ppt). However, this was offset by decreases in Grid Costs (-0.71ppt), Operations (-0.68ppt), Admin (-4.09ppt) and Utilities (-4.4ppt).""",

"revenue_trends":"""As an experienced financial report analyst, your task is to identify the drivers of Total Revenue using the provided data, which may include historical and potential income statement figures. Your assessment should closely follow the example output while considering different data scenarios. The output will be reviewed by a Private Equity investor who seeks to understand key Total revenue influencers and their impact, focusing on significant changes in percentage points (ppt).

Clarification of Terms: When a fiscal year is followed by the letter 'A,' it denotes historical information ('Act.' stands for 'Actuals'). In some statements, historical data may use the suffix 'Act.' All other suffixes after a fiscal year should be treated as future projections.

Context for the Example: You will be provided with a dataframe having information about a company's revenue.
The data may encompass both historical and potential income statement figures for a company.
You need to calculate the CAGR% (CAGR = (Ending value-Beginning value) to the power of [1/number of years-1])of total revenue for both actual years and the forecast years (if applicable).
CAGR should calculated for actual years by taking the lowest and highest actual years. and for forecast years if applicable, CAGR should be calculated using the lowest and highest forecast years
For ppt change of each term calculate the difference from % of a factor in A (Highest actual year) and % of the same factor in  B (Lowest actual year). this is for actual year.
Use the same method to calculate ppt change of each factor for the forecast period taking into consideration the highest and lowest forecast years

 Your goal is to pinpoint revenue categories affecting Total revenue, prioritizing key drivers with proper calculation. The output should present two concise sentences: one for historical Total revenue and another for future Total revenue, if applicable. In each sentence, strictly list the factors influencing Total revenue in descending order of ppt change. Use only the terms provided in the prompt and avoid introducing new terms or variables.

Example Output:
During the Historical Period, total revenues increased from ($1234) Xyear (Lowest actual Year) to ($6542) Yyear (Highest actual Year) at a CAGR of yy%. The trend is driven by hhh (+xx ppt), ywywue(+yy ppt) and is offset by zz (+dd ppt)

For the forecast period, total revenue for future periods is projected to increase/decrease from X (Lowest forecast Year) to Y (Highest forecast Year) at a CAGR of yy%. The trend is driven by hhh (+xx ppt), ywywue(+yy ppt) and is offset by zz (+dd ppt)
 """
}

TREND_ANALYSIS_PROMPT = {
    "operational_costs":"""Please analyze the provided information regarding the cost trends of the company. 
            Extract all sentences from the document that illustrate cause-and-effect relationships for each of the following terms: {categories}
            Analyze the factors driving the changes in {categories}. Extract all sentences from the document that explain the causes behind the change in these costs.

For each of the terms (cost A, cost B, etc.,),mention the ppt change and list the reasons for the observed increases/decrease and provide explanations based on the information and context provided in the document.

For each term, list the observed trends and identify the key factors driving these trends, using the information and context provided in the document. Present the findings as bulleted points and explain the cause-and-effect relationships behind each trend.

Ensure that the analysis covers historical periods and, if available, forecast or future periods. For the historical period, describe the trends and their causes. For the forecast or future period, if mentioned, explain the projected trends and the reasons behind them.
Ensure that the output has exact values for the years, ppt change and mentioned percentages. Do not use variables like x, y
The output should be strictly based on the information from the document. Do not make your own assumptions
Expected Output:

Commentary on Cost Categories:
The key factors driving increase/decrease/stability in EBITDA are XXX Cost A, YYY, etc.,
XXX Cost:
    The key reason for increase/decrease in XXX cost is due to so and so reason
    It is projected to increase/decrease by x.xx ppt in Year A(Future Year). This is linked to the following reasons.
YYY:
    YYY has increased/decreased by x.xx ppt from Year A to Year B (Actual years). This can be attributed to the following reasons
   
    YYY is projected to increase/decrease by x.xx ppt from Year A to Year B (Actual years). This can be attributed to the following reasons
""",

    "revenue_trends":"""Please analyze the provided information regarding the revenue trends of the company. 
    Extract all information about the revenue and the CAGR of the company.
            Extract all sentences from the document that illustrate cause-and-effect relationships for each of the following terms: {categories}
            Analyze the factors driving the changes in {categories}. Extract all sentences from the document that explain the causes behind the change in these revenue categories. Provide the commentary on revenue categories.

For each of the terms (Revenue A, Revenue B, etc.,),mention the ppt change and list the reasons for the observed increases/decrease and provide explanations based on the information and context provided in the document.

For each term, list the observed trends and identify the key factors driving these trends, using the information and context provided in the document. Present the findings as bulleted points and explain the cause-and-effect relationships behind each trend.

Ensure that the analysis covers historical periods and, if available, forecast or future periods. For the historical period, describe the trends and their causes. For the forecast or future period, if mentioned, explain the projected trends and the reasons behind them.
Ensure that the output has exact values for the years, ppt change and mentioned percentages. Do not use variables like x, y
The output should be strictly based on the information from the document. Do not make your own assumptions
Expected Output:

Commentary on Revenue Categories:
The key factors driving increase/decrease/stability in Total Revenue are Revenue A, Revenue B, etc.,
Revenue A:
    The key reason for increase/decrease in revenue A is due to company's strategy to increase the sales
    By increasing the advertisements, the market for the product is expanded leading to increased revenue
Revenue B:
    Revenue B has increased/decreased by x.xx ppt from Year A to Year B (Actual years). This can be attributed to the following reasons
   
    Revenue B is projected to increase/decrease by x.xx ppt from Year A to Year B (Actual years). This can be attributed to the following reasons
"""
}

TREND_USER_PROMPT = """Act as an experienced financial report analyst, evaluate the financial health and future prospects of a given company on the basis of provided financial data,i.e like Net sales, gross margin, Revenue etc. you have given financial report as dictionary. you can make realtion financial each field vs year. \n 1. explain report analysis with proper reasoning(why it go up or down) on each field. \n 2. generate report commentary flow wise easy to understand on each financial field. conclusion is good company to invest? \n 3. Generate Report only on Provided data. do not hallucinate. Stick to financial field. \n 4. be consistent for same query
You are a financial diligence consultant hired by a private equity fund to evaluate the financials of an investment Target. Your task is to identify information available in documents related to Sales, Material Cost, Labor Cost, Freight Cost, Footprint Cost, Production Cost, CapEx, Cash, Sales Cost, Footprint, Cost KPI Performance. You are trying to identify information available that can be used to assess if:
You present your output in a structured format, including:
1. Description of the trend related to financial metric. For example, the financial metric went from x in year a to y in year z
2. Any information available related to the value of the financial metric. If the value is not available, provide value for related financial metrics that may help the reader calculate
3. Key drivers of the trend. What reasons are driving the trend?
4. To the extent you can, state the implications of such trend in the context of this company
5. To the extend you can, state the implications in the context of industry
Explain you analysis with proper reasoning (why it go up or down) on each field. \n 2. generate report commentary in a way that it is easy to understand for each financial metric.
Generate Report only on Provided data. Stick to financial metrics. \n 4. be consistent for same query"""
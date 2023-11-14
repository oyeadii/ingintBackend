import pandas as pd


class AnomalyDetection:
    def __init__(self):
        self.cell_style={ "backgroundColor": "#EC625C", "fontWeight": "bold" }

    def get_num_to_excel_col(self, num):
        letters = []
        while num:
            num, remainder = divmod(num - 1, 26)
            letters.insert(0, chr(65 + remainder))
        return ''.join(letters)
    
    def get_position_list(self, df):
        positions = []
        row_col_list = []
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                if df.iloc[row, col] == 1:
                    cell_address = f"{self.get_num_to_excel_col(col + 1)}{row + 1}"
                    positions.append(cell_address)
                    row_col_list.append({"row":row, "col":col})
        return (positions,row_col_list)
    
    def get_styled_position_list(self, positions):
        styled_positions = [ {"cell": position, "style": self.cell_style} for position in positions ]
        return styled_positions

    def get_diff(self, series):
        numeric_series = pd.to_numeric(series, errors='coerce')
        return numeric_series.diff().fillna(0)

    def get_pct_change(self, series):
        numeric_series = pd.to_numeric(series, errors='coerce')
        return (numeric_series.pct_change() * 100).fillna(0)

    def safe_convert(self, x):
        try:
            return float(x)
        except:
            return x
        
    def safe_comparison(self, value, threshold):
        try:
            return value >= threshold
        except:
            return False
        
    def get_commentary(self, df, row_col_list):
        commentaries_dict = {}
        for row_col in row_col_list:
            column_name = df.columns[row_col["col"]]
            category = df.iloc[row_col["row"], 0]
            cell_value = df.iloc[row_col["row"], row_col["col"]]
            prev_cell_value = df.iloc[row_col["row"], row_col["col"] - 1]
            if category not in commentaries_dict:
                commentaries_dict[category] = []
            commentaries_dict[category].append(f"{prev_cell_value} to {cell_value} in {column_name}")

        commentaries = []
        for category, changes in commentaries_dict.items():
            if len(changes) > 1:
                commentary = f"{category} changed from {' and '.join(changes[:-1])} and {changes[-1]}"
            else:
                commentary = f"{category} changed from {changes[0]}"
            commentaries.append(commentary)
        return commentaries

    def get_anomalies_list(self, df, abs_threshold, pct_threshold, styling=False):
        df1 = df.applymap(self.safe_convert)
        df_diff = df1.apply(self.get_diff, axis=1)
        df_pct = df1.apply(self.get_pct_change, axis=1)

        df_result_diff = df_diff.applymap(lambda x: self.safe_comparison(x, abs_threshold))
        df_result_pct = df_pct.applymap(lambda x: self.safe_comparison(x, pct_threshold))
        df_result = (df_result_diff & df_result_pct).astype(int)

        res = self.get_position_list(df_result)
        anomaly_list = res[0]
        row_col_list = res[1]

        commentary=[]
        if len(row_col_list)!=0:
            commentary=self.get_commentary(df, row_col_list)
        if styling:
            anomaly_list=self.get_styled_position_list(anomaly_list)
        return {"anomaly_list":anomaly_list, "commentary_list":commentary}
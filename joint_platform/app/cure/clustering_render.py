# coding: utf-8

# Author: Mingzhe Du
# Date: 2022-07-11
# Email: mingzhe@nus.edu.sg

import os
import numpy as np
import pandas as pd
from sklearn import datasets

class ClusterRender(object):
    def __init__(self):
        pass
    
    def render_js(self, folder_name, date, datasets):
        input_file = f"./app/cure/static/data/{folder_name}/{date}_filtered.tsv"
        
        tweets_df = pd.read_csv(input_file, sep='\t')

        for group_number in tweets_df["pred"].unique():
            if group_number == -1:
                continue

            dataset = {
                "label": f"Group {group_number}",
                "backgroundColor": None,
                "data": list()
            }
            for instance in tweets_df[tweets_df["pred"] == group_number].itertuples():
                plot = eval(instance.plot)
                dataset["data"].append({
                    "x": float(plot[0]),
                    "y": float(plot[1]),
                    "label": str(f"Group {group_number}: " + instance.text)
                })
                dataset["backgroundColor"] = "#cc0000" if instance.selected == True else "#dedede"
            datasets.append(dataset)


if __name__ == '__main__':
    cr = ClusterRender()
    datasets = list()
    cr.render_js("test", "2022-07-14", datasets)

    print(datasets)
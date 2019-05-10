import json
import pandas as pd
import re

def formatString(input):
    return re.sub(r'[^\x00-\x7F]+', ' ', input)

def load_json(filename):
    with open(filename, 'r') as fp:
        json_ = json.load(fp)
        fp.close()
    return json_

def generateCreatorCSV(projectInfo):
    output_data = []
    keys = ['ProjectId', 'CreatedBy', 'BackedProjectsCount', 'CreatedProjectsCount', 'Description']
    for item in projectInfo:
        tmp = []
        tmp.append(item[keys[0]])
        tmp.append(item[keys[1]])
        for k in keys[2:len(keys) - 1]:
            tmp.append(item['CreatorProfile'][k])
        tmp.append(formatString(item['CreatorProfile'][keys[len(keys) - 1]]))
        output_data.append(tmp)
    pd.DataFrame(output_data).to_excel('creator.xlsx', header= keys, index= False)

if __name__ == '__main__':
    project_info_path = 'projectInfo.json'
    generateCreatorCSV(load_json(project_info_path))




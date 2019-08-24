import json
import pandas as pd
import glob
import re
import dateutil.parser

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
    pd.DataFrame(output_data).to_excel('creator.xlsx', header=keys, index=False)

def convert2urls():
    df = pd.read_csv('projects.csv', thousands=',', encoding= 'ISO-8859-1')
    urls = {}
    for i, link in enumerate(df['ProjectLink'].values):
        urls[i] = link
    with open('urls.json', 'w') as fp:
        json.dump(urls, fp)
        fp.close()

def get_unique_projects(path):
    projects = {}
    data_list = []
    for file_name in [f for f in glob.glob(path + "**/*.json", recursive=True)]:
        data_list.extend(load_json(file_name))
    for project in data_list:
        if project['ProjectId'] not in projects:
            projects[project['ProjectId']] = project
    return projects

def covert2urls_from_daily_files(path):
    projects = {}
    data_list = []
    for file_name in [f for f in glob.glob(path + "**/*.json", recursive=True)]:
        data_list.extend(load_json(file_name))
    for project in data_list:
        if project['ProjectId'] not in projects:
            projects[project['ProjectId']] = project['ProjectLink']
    with open('urls.json', 'w') as fp:
        json.dump(projects, fp)
        fp.close()


def flattern_json (projects):
    print(type(projects[0]))

def get_fundedOrNot(project_results):
    return 1 if (float(project_results['AmountPledged']) >= float(project_results['AmountAsked'])) else 0

def get_start_date(timeline):
    if len(timeline) == 2:
        return str(dateutil.parser.parse(timeline[0]).date())
    else:
        return ""
def get_end_date(timeline):
    if len(timeline) == 2:
        return str(dateutil.parser.parse(timeline[1]).date())
    else:
        return ""

def get_project_duration(timeline):
    if len(timeline) == 2:
        d1 = dateutil.parser.parse(timeline[0])
        d2 = dateutil.parser.parse(timeline[1])
        return int((d2 - d1).days)
    else:
        return ""
def math_current_result(filename, output_data):
    df = pd.read_excel(filename, sheet_name= 'Sheet1')
    project_set = set()
    for project_id in df['ProjectId'].values:
        project_set.add(str(project_id))
    to_be_added_projects = []
    for project in output_data:
        if project[0] not in project_set:
            to_be_added_projects.append(project)
    print (len(to_be_added_projects))
    return to_be_added_projects

def convert_json_excels(filename):
    projects = load_json(filename)
    result_map = {'live': 888, 'successful': 1, 'failed': 0, 'canceled': 2}
    output_data = []
    for project in projects:
        row = []
        row.append(project['ProjectId'])
        row.append(str(project['CampaignVideo']).upper())
        row.append(project['CreatedBy'])
        projectResults = project['ProjectResults']
        row.append(projectResults['AmountAsked'])
        row.append(projectResults['AmountPledged'])
        row.append(projectResults['FundedOrNot'])
        row.append(result_map[projectResults['FundedOrNot']])
        row.append(get_fundedOrNot(projectResults))
        row.append(projectResults['current_currency'])
        row.append(projectResults['goalFinishedPercentage'])
        row.append(projectResults['totalBackers'])
        projectSupports = json.loads(project['ProjectSupports'])
        row.append(projectSupports['totalLevels'])
        time_line = project['ProjectTimeLine']
        row.append(get_start_date(time_line))
        row.append(get_end_date(time_line))
        row.append(get_project_duration(time_line))
        project_updates = project['ProjectUpdates']
        row.append(project_updates['totalUpdatesAfterShipped'])
        row.append(project_updates['totalUpdatesBeforeFunded'])
        row.append(project_updates['totalUpdatesBetweenFundedAndShipped'])
        row.append(project['TotalCampaignImage'])
        row.append(project['totalComments'])
        row.append(project['totalVCommentsPercent'])
        row.append(project['totalVCommentsSample'])
        filtered_campaign_list = list(filter(lambda x : not x.isspace(), project['ProjectCampaign']))
        row.append(len(project['ProjectDescription'].split(" ")))
        row.append(len(filtered_campaign_list))
        row.append(filtered_campaign_list)
        creator_profile = project['CreatorProfile']
        row.append(creator_profile['BackedProjectsCount'])
        row.append(creator_profile['CreatedProjectsCount'])
        output_data.append(row)
    return output_data

def save_to_excel(output_data):
    keys = ['ProjectId', 'CampaignVideo', 'CreatedBy', 'AmountAsked', 'AmountPledged', 'FundedOrNot_Original', 'Result',
            'FundedOrNot', 'current_currency', 'goalFinishedPercentage', 'totalBackers', 'TotalLevel', 'StartDate',
            'EndDate', 'ProjectDuration', 'totalUpdatesAfterShipped', 'totalUpdatesBeforeFunded', 'totalUpdatesBetweenFundedAndShipped',
            'TotalCampaignImage', 'totalComments', 'totalVCommentsPercent', 'totalVCommentsSample', 'ProjectDesLength',
            'ProjectChampLength', 'ProjectCampaign', 'CreatorProjectBecked', 'CreatorProjectCreated']
    pd.DataFrame(output_data).to_excel('ksProject_new.xlsx', header=keys, index=False)

def extract_project_summary():
    # extract the project data and filter the duplicate project
    extra_data = math_current_result('data/ksProject(previous to 610).xlsx', convert_json_excels('data/611_725_projectInfo.json'))
    save_to_excel(extra_data)


if __name__ == '__main__':
    # convert2urls()
    # project_inatfo_path = 'projectInfo.json'
    # generateCreatorCSV(load_json("/Users/garden/Downloads/projectInfo.json"))
    # covert2urls_from_daily_files('data/daily')
    # convert_json_excels('data/611_725_projectInfo.json')
    extract_project_summary()

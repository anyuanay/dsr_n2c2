# 导入库
import pandas as pd
import re
# 定义函数
def extract_word_labels(path):
    # 加载上个函数完成的dataframe
    input_data = pd.read_csv(path)
    # 加载之前检索出标签I,B的dataframe
    df_label_I = pd.read_csv('df_label_I.csv')
    df_label_I.columns = ['Noteid', 'T', 'Position', 'Start', 'End', 'Word', 'Label']
    df_label_B = pd.read_csv('df_label_B.csv')
    df_label_B.columns = ['Noteid', 'T', 'Position', 'Start', 'End', 'Word', 'Label']
    # 将两个不同label的dataframe合并成一个
    df_label = pd.concat([df_label_B, df_label_I], axis=0, ignore_index=True)
    # # 单词处理
    # 将每句话切分成单个单词，并计算其在句中的位置
    list = []
    for j in range(0, len(input_data)):
        for i in re.findall(r"[\w']+|[.,!?;]", input_data.loc[j]['Sentence']):
            m = input_data.loc[j]['Sentence'].find(i) + input_data.loc[j]['Start']
            list.append(pd.DataFrame(
                {'Noteid': input_data.loc[j]['NotesId'], 'Sentenceid': input_data.loc[j]['SentenceId'], 'Word': i,
                 'Start': m, 'End': m + len(i)}, index=[0]))
            df3 = pd.concat(list, axis=0, ignore_index=True)
            # print(i)
    # 将得到的结果dataframe的预先加载的标签dataframe合并
    df_result = pd.merge(df3, df_label, on=['Noteid', 'Word', 'Start', 'End'], how='left')
    df_result = df_result[['Noteid', 'Sentenceid', 'Word', 'Start', 'End', 'Label']]
    # 将其他空值用'O'填充
    df_result['Label'].fillna('O', inplace=True)
    return df_result

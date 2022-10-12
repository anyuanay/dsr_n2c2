Author: Hewitt Zhang & Carl Shen
Date: Feb. 25 2022

0. 编程环境
编程语言：
Python 3.9.10 64-bit (windows store)

第三方库：
numpy 1.21.4
pandas 1.4.0
spacy 3.2.1
en-core-web-sm 3.2.0

--------------------------------------------------------------------------------
1. 程序目标
将输入的临床笔记分解为句子，并输出一个DataFrame结构，其中包含有关输入临床笔记中句子的信息。

--------------------------------------------------------------------------------
2. 输入&输出
输入：
notesId:str 
-- 文档编号。eg. 101-01.txt 编号为 101-01
notesText:str 
-- 文档内容（包含“\n”，“\t”等特殊字符）。
sections:list[str] （默认参数，默认值为['HISTORY OF PRESENT ILLNESS', 'PHYSICAL EXAMINATION', 'LABORATORY DATA', 'ASSESSMENT AND PLAN', 'NARRATIVE']）
-- section标题的列表，可以视文档情况进行扩充。

输出：
下列属性构成的DataFrame
notesId:str
-- 文档编号。eg. 101-01.txt 编号为 101-01
SentenceId:str （具有唯一性）
-- 句子编号。eg. 101-01_21 代表 101-01 文档的第21条句子。
Sentence:str
-- 句子内容（包含“\n”，“\t”等特殊字符）。
Start:int
-- 句子在整段文本中的python索引起始位置。
End:int
-- 句子在整段文本中的python索引结束位置。（python索引遵循左取右不取）
Section:str
-- 句子所属的section的标题。eg. ‘NARRATIVE’, ‘PHYSICAL EXAMINATION’
PrevSentId:str （具有唯一性）
-- 按照文本中句子的排列顺序，当前句子前一句的句子编号。（文本中首句的前一句编号为NaN）
NextSentId:str （具有唯一性）
--  按照文本中句子的排列顺序，当前句子后一句的句子编号。（文本中最后一句的后一句编号为NaN）

--------------------------------------------------------------------------------
3. 程序主要步骤
Step1: 根据预定义的section标题，按照文本中的section出现顺序给出当前文本的标题列表。
Step2: 将section标题作为划分标志，用有序字典存储section和对应文本。其中不具备section标题的文本被归类为“No Section”。
Step3: 借助Spacy库中的en_core_web_sm语言包将文本划分为句子。
Step4: 为每个句子提取输出时需要的信息，并存储为嵌套列表。
Step5: 将嵌套列表转换为DataFrame结构并输出。

--------------------------------------------------------------------------------
4. 测试用例（代码见test.ipynb）
1）当没有匹配到任何已知的section时，将所有句子标注为“No Section”。
输入：110-02.txt (不存在section结构）
结果：通过
2）自定义section列表，提高句子提取效率。
输入：126-04.txt （不匹配预定义的section列表）
传入自定义的section列表：
['Reason for referral',
 'History of Present Illness',
 'Past Medical History',
 'Medications',
 'Allergies',
 'Family History',
 'Social History',
 'Review of Systems',
 'Physical Examination',
 'Laboratory',
 'Impressions']
结果：显著提高

--------------------------------------------------------------------------------
5. 缺陷&未来计划
1）Spacy库对包含特殊符号的文本分句效果一般
-- 计划在Step3中加入判定规则来提高分句效果。（进行中，Carl Shen）
2）不同文本中同样的section标题会有大小写区别
-- 设置函数参数来控制是否忽略section标题的大小写进行匹配。
3）没能区分文本中最后一个section的范围，默认从最后一个section标题开始的所有文本都属于最后一个section
-- ？

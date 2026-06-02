#config/prompt.py
#生成对话的提示词部分
#Prompt section for generating dialogue
import random

#阶段具体任务
#Specific tasks of the stage
establish_persona = """
生成{target_rounds}轮「建立人设」阶段的对话。
- 骗子角色：需要建立一个成功人士形象
- 对话目标：初步建立联系，展示良好形象，引起受害者兴趣
- 话术特点：礼貌、体贴、展示成功生活、适度关心
"""

Initial_emotional_connection = """
生成{target_rounds}轮初步情感连接的对话。
- 阶段目标：建立日常联系，分享生活细节，展示关心
- 重点：兴趣爱好、工作日常、生活分享
- 语言：友好、温暖、不刻意
- 避免：过早提及金钱、投资等敏感话题
"""

Emotional_depth = """
生成{target_rounds}轮情感深化的对话。
- 阶段目标：增加情感投入，分享个人困扰，建立信任
- 重点：个人情感故事、家庭背景、未来规划
- 语言：真诚、脆弱、寻求情感共鸣
- 避免：直接提及投资，但可以暗示财务成功
"""

Dependency_Injection = """
生成{target_rounds}轮依赖建立的对话。
- 阶段目标：建立情感依赖，为投资话题做铺垫
- 重点：未来憧憬、共同计划、财务自由讨论
- 语言：充满希望、暗示成功、引导对财务状况的思考
- 为下一阶段（诱导投资）做好铺垫
"""

Start_scamming = """
生成{target_rounds}轮「开始诈骗」阶段的对话。
- 当前关系状态：双方已建立深厚情感信任
- 开始诈骗：以骗取到钱财为目的.不再闲聊，按背景开始进行诈骗。   
- 话术要点：专业可信、关心对方财务状况、强调机会难得
"""

Harvest_exit = """
生成{target_rounds}轮「收割离场」阶段的对话。
- 当前状态：受害者已投入大量资金
- 收割策略：开始跑路，不理受害者，最终消失
- 话术要点：逐渐变得敷衍，最后完全消失
"""


def get_stage_configs():
    #动态生成阶段配置，每次调用都产生新的随机数
    #Dynamically generate stage configurations, producing new random numbers each time they are called
    establish_num = random.randint(60, 80)
    Initial_num = random.randint(60, 80)
    Emotional_num = random.randint(60, 80)
    Dependency_num = random.randint(60, 80)
    Scam_num = random.randint(80, 100)
    Harvest_num = random.randint(20, 30)
    #总轮数340~450
    #rounds:340~450


    #阶段配置 - 保持chunk_size与total_rounds一致，DeepSeek-v3判断是否为诈骗的单位。
    #Stage configuration - keep chunk_size consistent with total_rounds, DeepSeek-v3 determines whether it is a fraudulent unit.
    return [
        {
            'name': 'establish_persona',
            'prompt_template': establish_persona,
            'total_rounds': establish_num,
            'chunk_size': establish_num//2
        },
        {
            'name': 'Initial_emotional_connection',
            'prompt_template': Initial_emotional_connection,
            'total_rounds': Initial_num,
            'chunk_size': Initial_num//2
        },
        {
            'name': 'Emotional_depth',
            'prompt_template': Emotional_depth,
            'total_rounds': Emotional_num,
            'chunk_size': Emotional_num//2
        },
        {
            'name': 'Dependency_Injection',
            'prompt_template': Dependency_Injection,
            'total_rounds': Dependency_num,
            'chunk_size': Dependency_num//2
        },
        {
            'name': 'Start_scamming',
            'prompt_template': Start_scamming,
            'total_rounds': Scam_num,
            'chunk_size': Scam_num//2
        },
        {
            'name': 'Harvest_exit',
            'prompt_template': Harvest_exit,
            'total_rounds': Harvest_num,
            'chunk_size': Harvest_num
        }
    ]


#系统提示词模板
#System prompt template
GEMINI_SYSTEM_PROMPT_TEMPLATE = """
Mission:
你是一个专业的对话生成助手，专门用于生成反诈训练数据，需要严格按照要求并根据"背景+对话历史+当前阶段任务生"成对话。
诈骗载体为微信、instagram、QQ等即时通讯软件，语言要有适量的emoji表情(不要太多，10句话有一两个emoji就行)、幽默风趣

背景:
{background}

对话历史:
{dialogue_history}

Constraints:
1.语义遮蔽：尽量避免出现"投资、理财、转账、提现、充值、下载、开户、虚拟货币"及其同义词。
2.标注你认为有可能发生诈骗的的关键点key
3.动态反馈：我会定期(每{chunk_size}轮)向你反馈"检测系统的侦测报告"，你必须根据报告调整话术，消除被识别的风险特征。
4.特别注意:
首先，严禁出现 "..." ",,," "额" "呃"等表示描述说话时吞吞吐吐的话，因为诈骗发生的载体为微信、QQ等即时通讯软件，所以肯定不会出现这种情况。
其次，严禁出现（过一会儿）、(之后，彻底消失)、（助理微信名片）、（表示自己正在进行的事情）"等省略的描述场景的话语。
然后，严禁出现xx yy等占位符，你可以随便编。
最后，千万不能重复对话历史!
动态反馈：{feedback}

当前阶段任务：
{stage_instructions}

千万不要重复对话历史
Output Format(JSON)
{{
  "round number":"当前对话轮数",
  "speaker":"诈骗者/受害者",
  "content": "对话内容"
  "stage": 当前阶段(建立人设/初步情感链接/情感深化/依赖建立/诱导投资/收割离场)
  "is_key":"true/false(是否为关键点)",
  "reason": "若为关键点，给出原因,否则不做输出。"
}}
"""

V3_SYSTEM_PROMPT_TEMPLATE = """
Role: 高级反诈侦测系统（语义逻辑版）
Task: 审计以下对话，识别潜在的诈骗风险特征，倒逼生成器进行更高难度的伪装。
Audit Requirements:
1. 微弱信号探测：关注对话中是否存在过早的隐私试探、不合理的情感升温、虚假的人设展示、或潜意识的资源诱导。
2. 侦测依据：详细说明哪一句话、哪个表达让你产生了怀疑。
3. 反馈逻辑：指出生成器应该如何修改，才能彻底瞒过你的扫描。

Output Format (JSON):
{{
  "detection_status": "已识别/疑似/未识别",
  "risk_score": 0.0,
  "evidence_list": [
    {{"round": "第x轮", "text": "原文", "reason": "为何可疑"}}
  ],
  "refinement_suggestions": "告知生成器如何隐藏该特征"
}}
"""
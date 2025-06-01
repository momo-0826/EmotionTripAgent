from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from get_random_prompt import get_random_prompt 
import os
import asyncio

# .envファイルの読み込み
load_dotenv()

# 環境変数取得
openai_api_key = os.getenv("OPENAI_API_KEY")

# 使用するモデルを定義
openai_model_client = OpenAIChatCompletionClient(
    model="gpt-4o-2024-08-06",
)

# プロンプトをテキストからランダムで取得
local_prompt = get_random_prompt()

# TODO Streamlitのチャットからプロンプトを取得するように修正する
prompt = local_prompt

# Agentを定義していく
# 1人目のエージェント：旅行の全体的なプランを提案するエージェント
planner_agent = AssistantAgent(
    name="planner_agent",
    model_client=openai_model_client,
    description="旅行の全体的なプランを提案するエージェント",
    system_message="あなたは、ユーザーの要望から最適な旅行プランを作成するプロフェッショナルです。どうしても要望が叶えられない場合はその旨を伝えることもできる優秀な人材です。"
)
# 2人目のエージェント：行き先での詳細な行動プランを提案するエージェント
# local_planner_agent = AssistantAgent(
#     name="local_planner_agent",
#     model_client=openai_model_client,
#     description="旅行の行き先での詳細な行動プランを提案するエージェント",
#     system_message="あなたは、旅行先での人気のアクティビティや文化、観光スポットなどを基に詳細な旅行のプランを作成するエージェントです。"
# )
local_planner_agent = AssistantAgent(
    name="local_planner_agent",
    model_client=openai_model_client,
    description="旅行の行き先での詳細な行動プランを提案するエージェント",
    system_message='''
    あなたは、旅行先での人気のアクティビティや文化、観光スポットなどに詳しく詳細な旅行のプランを作成するエージェントです。
    あなたは、別のエージェントから提供された旅行の全体的なプランを基に詳細な旅行のプランを作成します。
    そのため、他のエージェントが計画していない旅行先への旅行プランを独自に作成することはありません。
    あなたは、とても柔軟で予算や好みなどの情報が無くても、これらを自分で仮で決めて計画を作成することができます。
    また、提供されたコンテキスト情報を利用できます。
    '''
)


# 3人目のエージェント：行き先の文化や気を付けるべき内容を提案するエージェント
culture_agent = AssistantAgent(
    name="culture_agent",
    model_client=openai_model_client,
    description="旅行の行き先での文化に基づいて気を付けるべき事を提案するエージェント",
    system_message="あなたは、旅行先での文化や言語に詳しく、与えられた候補の情報から各旅行先で日本人旅行者が現地で気を付けるべき内容を一覧にして教えてくれるエージェントです。"
)
# 4人目のエージェント：他のエージェントの提案を受けて最終的な回答を作成するエージェント
summary_agent = AssistantAgent(
    name="summary_agent",
    model_client=openai_model_client,
    description="旅行のプランを受け取り要約して、最終的な計画を提案するエージェント",
    system_message='''
    あなたは、他のエージェントが提案した全体的な旅行プランや詳細なプラン、気を付けなければならないことを受け取り、それらを要約して最終的な計画を詳細まで提案するエージェントです。
    要約した最終的な計画内には他のエージェントから受け取った全ての内容が欠けることなく含まれていることを確認してください。
    計画が完了し、すべてのパースペクティブが統合されたら、TERMINATE で応答できます。
    '''
)

# エージェントの会話終了の合図を決める
# テキストにTERMINATEが入っている場合会話が完了したとする
termination = TextMentionTermination("TERMINATE")

# グループチャットの設定を行う
# 今回は1人目のエージェントから順番に会話を回していくように設定する
group_chat = RoundRobinGroupChat(
    participants = [planner_agent, local_planner_agent, culture_agent, summary_agent],
    termination_condition = termination,
    # 最大10ターンまで会話を行うように設定
    max_turns = 10
)

# まずは試しにconsoleから旅行に関する質問を行ってみる
async def call_console(): 
    await Console(group_chat.run_stream(task=prompt))

def main():
    asyncio.run(call_console())

if __name__ == "__main__":
    main()
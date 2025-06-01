# テキストからプロンプトをランダムで取得する
# 動作確認用のため、不要な場合には使用しない
import random

prompt_file = "prompts.txt"
delimiter = "--END--"

def get_random_prompt(file_path=prompt_file, delimiter=delimiter) -> str:
    if file_path is None:
        file_path = prompt_file
    if delimiter is None:
        delimiter = delimiter
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 区切り文字で分割、その後不要な空白を削除
    prompts = [p.strip() for p in content.split(delimiter) if p.strip()]

    if not prompts:
        raise ValueError("プロンプトが見つかりませんでした。ファイルパスが正しいことを確認してください。")
    
    return random.choice(prompts)
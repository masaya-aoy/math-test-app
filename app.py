import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

app = Flask(__name__)
CORS(app) # 開発用に、すべての場所からのアクセスを許可

# Gemini APIキーを設定
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("環境変数 'GEMINI_API_KEY' が設定されていません。")

genai.configure(api_key=gemini_api_key)

# 「/generate-encouragement」という住所にリクエストが来たら、この関数が動く
@app.route('/generate-encouragement', methods=['POST'])
def generate_encouragement():
    # 画面側から送られてきたデータを受け取る
    data = request.get_json()
    mistake_count = data.get('mistake_count')
    total_questions = data.get('total_questions')
    difficulty = data.get('difficulty') # 難易度も受け取る！

    if mistake_count is None or total_questions is None or difficulty is None:
        return jsonify({"error": "必要なデータが不足しています"}), 400

    # 難易度を日本語に変換
    difficulty_jp = {"easy": "かんたん", "normal": "ふつう", "hard": "むずかしい"}.get(difficulty, "ふつう")

    # ★★★ ここがキモ！「足し算・引き算テスト」用に最適化したプロンプト ★★★
    prompt = f"""
    あなたは小学生に算数を教えるのがとても上手な、優しい先生です。
    ユーザーの子供は今、「{difficulty_jp}」レベルの足し算・引き算のテストを終えました。
    全{total_questions}問中、{mistake_count}個間違えてしまいました。

    この結果を受けて、子供が「次も頑張ろう！」と前向きになれるような、温かい励ましのメッセージを1つ生成してください。
    以下の条件を必ず守ってください：
    - 決して子供を責めない、優しい言葉遣いをする。
    - 「おしかったね！」「次はできるよ！」のように共感的な姿勢を見せる。
    - 特に「むずかしい」レベルに挑戦した場合は、その勇気を褒める言葉を入れる。
    - 日本語で、ひらがなを多めに使った親しみやすい話し方で、60文字程度でお願いします。
    """

    # もし全問正解だったら、特別に褒めるプロンプトに変更！
    if mistake_count == 0:
        prompt = f"""
        あなたは小学生に算数を教えるのがとても上手な、優しい先生です。
        ユーザーの子供は今、「{difficulty_jp}」レベルの足し算・引き算のテストを終えました。
        結果は、なんと全問正解でした！

        この素晴らしい結果を、子供の頑張りが報われるように、最大限に褒めてあげてください。
        以下の条件を必ず守ってください：
        - 「すごい！」「やったね！」といった喜びを素直に表現する。
        - 集中して頑張ったことを具体的に褒める。
        - 日本語で、ひらがなを多めに使った親しみやすい話し方で、60文字程度でお願いします。
        """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        # Gemini先生からのメッセージを画面側に返す
        return jsonify({"message": response.text.strip()})
    except Exception as e:
        print(f"エラー発生: {e}")
        # 万が一AIが応答しない場合も、代わりの言葉を返す
        fallback_message = "すごい！パーフェクトだ！よくがんばったね！" if mistake_count == 0 else "よくがんばったね！そのちょうし！"
        return jsonify({"message": fallback_message}), 500

if __name__ == '__main__':
    # このプログラムを起動すると、サーバーがリクエストを待ち始める
    app.run(port=5000, debug=True)

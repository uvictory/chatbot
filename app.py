from flask import Flask
# 각각의 라우트 블루프린트를 불러옴
from routes.chatbot import chatbot_bp
from routes.form import form_bp
from routes.policy import policy_bp

# Flask 앱 생성
app = Flask(__name__)

# 각 기능별 라우트를 Flask 앱에 등록
app.register_blueprint(chatbot_bp)
app.register_blueprint(form_bp)
app.register_blueprint(policy_bp)

# 앱 실행 (개발용 서버)
if __name__ == "__main__":
    app.run(debug=True)

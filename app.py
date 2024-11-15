from flask import Flask, render_template, request, jsonify
from chat_model import ChatBot
from config import config
from config import config_Welcome
import os

app = Flask(__name__)

# 设置上传文件的路径
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 初始化ChatBot
chatbot = ChatBot(config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    # 获取基于上下文的回复
    response = chatbot.get_response(user_message)
    print(f"Sending response to frontend: {response}")  # 添加日志以调试
    return jsonify({"response": response})

@app.route('/welcome', methods=['GET'])
def welcome():
    welcome_message = config_Welcome
    # 将欢迎消息也添加到上下文
    # chatbot.get_response(welcome_message)
    return jsonify({"response": welcome_message})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"response": "No file part"}), 400

    file = request.files['file']
    user_message = request.form.get('message', '')

    if file.filename == '':
        return jsonify({"response": "No selected file"}), 400

    if file:
        # 保存上传的文件
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # 在这里调用模型处理图片的逻辑，并将用户消息作为部分prompt
        result = chatbot.process_image(file_path, user_message)

        return jsonify({"response": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

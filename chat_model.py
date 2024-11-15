from dwspark.models import ChatModel
from sparkai.core.messages import ChatMessage
from dwspark.models import ChatModel, Text2Img, ImageUnderstanding, Text2Audio, Audio2Text
from loguru import logger
from config import config_prompt

class ChatBot:
    def __init__(self, config):
        self.model = ChatModel(config, stream=False)
        self.iu = ImageUnderstanding(config)
        self.chat_context = []  # 用于存储整个聊天上下文
        self.train_with_prompts()
        print(self.chat_context)

    def train_with_prompts(self):
        """使用提示词初始化模型"""
        logger.info('Initializing model with prompts...')
        prompts = config_prompt
        
        # 将提示词添加到上下文，并传递给模型
        for prompt in prompts:
            self.chat_context.append(ChatMessage(role="user", content=prompt))
        
        logger.info('Model initialized with basic prompts.')

    def get_response(self, question):
        logger.info('Processing question: {}'.format(question))
        
        # 将用户的消息添加到上下文中
        self.chat_context.append(ChatMessage(role="user", content=question))
        
        # 调用模型生成回复，传递整个上下文
        response = self.model.generate(self.chat_context)
        
        # print(f'response:{response}')
        print(f'history:{self.chat_context})')

        # 调试：检查生成的回复
        logger.info('Response from model: {}'.format(response))
        
        # 确保返回值是一个非空字符串
        if isinstance(response, str) and response:
            bot_response = response
        elif isinstance(response, list) and len(response) > 0:
            # 处理 response 是列表且第一个元素是字符串的情况
            bot_response = response[0] if isinstance(response[0], str) else str(response[0])
        else:
            bot_response = "抱歉，我无法理解您的问题。"

        # 将机器人的回复也添加到上下文中
        self.chat_context.append(ChatMessage(role="bot", content=bot_response))
        return bot_response
    
    def process_image(self, image_path,user_message):
        """处理上传的图片并生成解释"""
        logger.info(f'Processing image: {image_path}')

        context = " ".join([message.content for message in self.chat_context])

        prompt = f'{context},用户请求解释以下内容："{user_message}"，请结合图片进行理解。'

        # 将用户的消息添加到上下文中
        self.chat_context.append(ChatMessage(role="user", content=user_message))
        
        # 使用 ImageUnderstanding 模型对图片生成解释
        # explanation = self.image_model.understanding(prompt, image_path)
        explanation = self.iu.understanding(prompt,image_path)
        
        logger.info(f'Image explanation generated: {explanation}')

        self.chat_context.append(ChatMessage(role="bot", content=explanation))

        return explanation if explanation else "抱歉，我无法理解这张图片。"

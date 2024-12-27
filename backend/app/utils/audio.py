import azure.cognitiveservices.speech as speechsdk
import os
import wave
import numpy as np
import base64
from io import BytesIO
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi import HTTPException
from starlette.websockets import WebSocketDisconnect, WebSocketState
from dotenv import load_dotenv
import asyncio


# 从 .env 文件中加载环境变量
load_dotenv()

# 获取 Azure 语音服务的密钥和区域信息
AZURE_SPEECH_KEY = os.getenv("SPEECH_KEY")
AZURE_REGION = os.getenv("SPEECH_REGION")


# 保存音频为 .wav 文件的函数
def save_audio(
    audio_data: bytes,
    output_path: str,
    sample_rate: int = 16000,
    channels: int = 1,
    sampwidth: int = 2,
):
    # 创建一个 WAV 文件并写入数据
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(channels)  # 设置声道数，1为单声道，2为立体声
        wf.setsampwidth(sampwidth)  # 设置每个样本的字节数，16位为2字节
        wf.setframerate(sample_rate)  # 设置采样率
        wf.writeframes(audio_data)  # 写入音频数据


# 函数：使用 Azure API 进行语音识别
def recognize_speech(audio_file_path):
    # 初始化 Azure Speech Service 配置
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY, region=AZURE_REGION
    )
    # 设置语音识别语言（中文）
    speech_config.speech_recognition_language = "zh-CN"

    # 创建音频配置
    audio_config = speechsdk.AudioConfig(filename=audio_file_path)

    # 创建语音识别器
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )
    result = recognizer.recognize_once()

    # 判断识别结果
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text  # 识别成功，返回识别的文本
    # elif result.reason == speechsdk.ResultReason.NoMatch:
    #     return f"没有语音匹配: {result.no_match_details}"  # 未识别到语音
    # elif result.reason == speechsdk.ResultReason.Canceled:
    #     cancellation_details = result.cancellation_details
    #     return f"语音识别被取消: {cancellation_details.reason}, 错误详情: {cancellation_details.error_details}"  # 识别被取消
    # else:
    #     return f"无法识别音频, 错误原因: {result.reason}"

    # 异步语音识别函数


async def recognize_and_send(websocket, output_path):
    try:
        result_text = await asyncio.to_thread(
            recognize_speech, output_path
        )  # 使用线程池执行同步任务
        print(result_text)
        if result_text is None:
            result_text = ""
        # 检查 WebSocket 是否仍然连接
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json({"text": result_text})
    except WebSocketDisconnect:
        print("WebSocket 连接已断开，无法发送数据")
    except Exception as e:
        print(f"识别或发送消息时发生错误: {e}")



# 文本转语音的方法
def text_to_speech(request_text: str):
    print("request_text:", request_text)

    # 配置 Azure 语音服务
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY, region=AZURE_REGION
    )
    # 设置语音合成使用的声音
    speech_config.speech_synthesis_voice_name = "zh-CN-YunyiMultilingualNeural"

    # 创建语音合成器
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=None
    )

    # 进行文本转语音
    speech_synthesis_result = speech_synthesizer.speak_text_async(request_text).get()

    if (
        speech_synthesis_result.reason
        == speechsdk.ResultReason.SynthesizingAudioCompleted
    ):
        # 使用 AudioDataStream 获取音频数据流
        audio_stream = speechsdk.AudioDataStream(speech_synthesis_result)

        return audio_stream

    else:
        raise HTTPException(
            status_code=400,
            detail=f"TTS 请求失败: {speech_synthesis_result.error_details}",
        )

from fastapi import APIRouter, WebSocket, HTTPException
from utils.audio import recognize_speech, save_audio, text_to_speech, recognize_and_send
import time
import asyncio
from starlette.websockets import WebSocketDisconnect, WebSocketState
import os
import uuid
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO

from functools import partial
import azure.cognitiveservices.speech as speechsdk  # Azure 语音 SDK
from dotenv import load_dotenv  # 用于从 .env 文件加载环境变量
import os  # 用于读取环境变量

# 从 .env 文件中加载环境变量
load_dotenv()

# 获取 Azure 语音服务的密钥和区域信息
AZURE_SPEECH_KEY = os.getenv("SPEECH_KEY")
AZURE_REGION = os.getenv("SPEECH_REGION")

# 创建一个APIRouter实例
audio_router = APIRouter()

# 定义 audio_dir 存储文件的临时目录
audio_dir = "./static/audio"
os.makedirs(audio_dir, exist_ok=True)  # 创建目录


# 处理 WebSocket 音频连接
@audio_router.websocket("/ws/stt")
async def audio_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_name = uuid.uuid4().hex  # 生成一个唯一的音频名称
    audio_path = os.path.join(audio_dir, audio_name + ".wav")  # 生成音频文件的路径
    print(f"音频文件路径: {audio_path}")
    try:
        audio_buffer = bytearray()  # 用于保存接收到的音频数据
        count = 0  # 用于保存音频块的数量
        start_time = time.time()

        while True:
            data = await websocket.receive_bytes()  # 接收前端发送的二进制音频数据
            print(f"接收到的数据大小: {len(data)} bytes")  # 输出接收的数据大小
            audio_buffer.extend(data)  # 将数据添加到缓冲区
            count += 1

            # 调用 Azure API 识别音频
            if count % 250 == 0:  # 差不多2秒上传一次语音识别
                # 当收到完整的音频块时，保存音频为 .wav 文件
                save_audio(bytes(audio_buffer), audio_path)  # 保存音频
                end_time = time.time()
                print(f"识别耗时: {end_time - start_time:.2f} 秒")

                # 异步任务执行语音识别
                task = asyncio.create_task(recognize_and_send(websocket, audio_path))

    except Exception as e:
        print(f"{e}")
    finally:
        if os.path.exists(audio_path):  # 检查文件是否存在
            os.remove(audio_path)  # 删除音频文件



# WebSocket 处理请求并流式发送音频数据
@audio_router.websocket("/ws/tts")
async def audio_stream(websocket: WebSocket):
    await websocket.accept()

    # 等待客户端传送的文本
    request_text = await websocket.receive_text()

    # 调用 text_to_speech 方法获取音频流
    try:
        audio_stream = text_to_speech(request_text)  # 获取音频流（非流式）
        # 将音频流逐块写入 BytesIO 对象
        buffer = bytes(1024 * 8)  # 每次读取 8KB 的缓冲区
        filled_size = audio_stream.read_data(buffer)
        while filled_size > 0:
            await websocket.send_bytes(buffer)  # 通过 WebSocket 发送二进制数据
            print(f"发送音频数据大小: {filled_size}")
            filled_size = audio_stream.read_data(buffer)

    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        await websocket.close()


# 语音合成回调函数 (同步)
# def synthesize_callback(evt: speechsdk.SpeechSynthesisEventArgs, audio_queue):
#     # 获取语音合成的音频数据
#     header_offset = 46  # 头部偏移，跳过 Azure 语音数据的前46字节
#     chunk_size = len(evt.result.audio_data) - header_offset  # 计算有效音频数据大小
#     audio = evt.result.audio_data[-chunk_size:]  # 获取有效的音频数据
#     print(
#         "接收到长度为 {} 的音频块，持续时间 {}".format(
#             len(audio), evt.result.audio_duration
#         )
#     )
#     # asyncio.get_event_loop().create_task(asyncio.sleep(3))
#     # 在事件循环中创建任务，将音频数据放入队列
#     # asyncio.get_event_loop().create_task(audio_queue.put(audio))
#     # sleep(10)
#     audio_queue.put_nowait(audio)


# # 用于将音频数据写入文件的协程函数
# async def send_audio(queue, websocket):
#     # 不断从队列中读取音频数据并写入文件
#     print("开始传输音频数据")
#     while True:
#         audio_data = await queue.get()  # 从队列中获取音频数据
#         if audio_data is None:
#             # 当收到 None 时停止写入文件
#             break
#         print("写入长度为 {} 的音频块".format(len(audio_data)))

#         # 通过 WebSocket 发送二进制数据
#         await websocket.send_bytes(audio_data)


# 复杂版本实现ws/tts 但是和简单版本实现的效果一样，没有正确实现流式发送音频数据
# WebSocket 处理请求并流式发送音频数据
# @audio_router.websocket("/ws/tts")
# async def audio_stream(websocket: WebSocket):
#     await websocket.accept()

#     # 等待客户端传送的文本
#     request_text = await websocket.receive_text()
#     audio_queue = asyncio.Queue()  # 创建一个队列用于存储音频数据

#     # 调用 text_to_speech 方法获取音频流
#     try:
#         # Create an instance of the SpeechConfig with your subscription key and region
#         speech_config = speechsdk.SpeechConfig(
#             subscription=AZURE_SPEECH_KEY, region=AZURE_REGION
#         )

#         # Create an instance of the SpeechSynthesizer with the SpeechConfig
#         synthesizer = speechsdk.SpeechSynthesizer(
#             speech_config=speech_config, audio_config=None
#         )

#         # # Connect the callback
#         # synthesizer.synthesizing.connect(
#         #     synthesizer.synthesizing.connect(synthesize_callback)
#         # )

#         synthesizer.synthesizing.connect(
#             lambda evt: synthesize_callback(evt, audio_queue)
#         )    

#         audio_task = asyncio.create_task(send_audio(audio_queue, websocket))

#         speech_synthesis_result = synthesizer.speak_text_async(request_text).get()
#         if (
#             speech_synthesis_result.reason
#             == speechsdk.ResultReason.SynthesizingAudioCompleted
#         ):
#             print("Audio data received")

#             # Signal the audio_queue to stop writing to the file
#             audio_queue.put_nowait(None)

#             # Wait for the send_audio() task to complete
#             await audio_task

#     except Exception as e:
#         await websocket.send_text(f"Error: {str(e)}")
#     finally:
#         await websocket.close()

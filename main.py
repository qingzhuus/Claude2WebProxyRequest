from flask import Flask, request, jsonify, make_response, Response, stream_with_context
from claude_api.claude_api import Client
import asyncio
import time
import threading
import queue

app = Flask(__name__)


@app.route("/")
def root():
  return jsonify(message="Claude2WebProxy")


@app.route("/api/organizations/<org_uuid>/chat_conversations", methods=['GET'])
def chat_conversations(org_uuid):
  Cookie = request.headers.get('Cookie')
  api = Client(Cookie, org_uuid)
  try:
    response = api.chat_conversations()
    return make_response(response.content, 200)
  except Exception as e:
    return make_response(str(e), 500)


@app.route("/api/organizations/<org_uuid>/chat_conversations",
           methods=['POST'])
def create_new_chat(org_uuid):
  headers = request.headers
  Cookie = headers.get('Cookie')
  api = Client(Cookie, org_uuid)
  try:
    # 获取JSON数据
    data = request.data
    response = api.create_new_chat(data)
    return make_response(response.content, 200)
  except Exception as e:
    return make_response(str(e), 500)


def sync_generator(q):
  while True:
    line = q.get()
    if line == '[ERROR]':
      break
    elif line == '[DONE]':
      break
    else:
      yield line + '\n'


async def make_claude_request(api, data):
  data_queue = queue.Queue()
  threading.Thread(
      target=lambda: asyncio.run(api.send_message(data, data_queue))).start()

  return Response(sync_generator(data_queue), 201)


@app.route("/api/append_message", methods=['POST'])
def append_message():
  headers = request.headers
  Cookie = headers.get('Cookie')
  api = Client(Cookie)
  try:
    data = request.data
    # response = asyncio.run(make_claude_request(api, data))
    # return response
    data_queue = queue.Queue()
    threading.Thread(target=lambda: asyncio.run(
        api.send_message(data, data_queue))).start()

    return Response(stream_with_context(sync_generator(data_queue)),
                    content_type='text/plain')

  except Exception as e:
    return make_response(str(e), 500)


@app.route("/api/organizations/<org_uuid>/flags/<type>/dismiss",
           methods=['POST'])
def dismiss(org_uuid, type):
  Cookie = request.headers.get('Cookie')
  api = Client(Cookie, org_uuid)
  try:
    response = api.diss_flag(org_uuid, type)
    return make_response(response.content, 200)
  except Exception as e:
    return make_response(str(e), 500)


@app.route("/api/organizations", methods=['GET'])
def get_organizations():
  Cookie = request.headers.get('Cookie')
  api = Client(Cookie)
  try:
    response = api.get_organizations()
    return make_response(response.content, 200)
  except Exception as e:
    return make_response(str(e), 500)


@app.route("/api/organizations/<org_uuid>/chat_conversations/<chat_uuid>",
           methods=['DELETE'])
def delete_chat(org_uuid, chat_uuid):
  Cookie = request.headers.get('Cookie')
  api = Client(Cookie, org_uuid)
  try:
    response = api.delete_conversation(chat_uuid)
    if response.status_code == 204:
      return make_response('', 204)
    else:
      return make_response(response.content, response.status_code)
  except Exception as e:
    return make_response(str(e), 500)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)

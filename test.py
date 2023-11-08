import requests
import json
import uuid

sessionKeys = 'sessionKey=sk-ant-sid01-what's your problem'
org_uuid = '1-2-3-4-5'

headers = {
    'Cookie': f'{sessionKeys}',
    'Content-Type': 'application/json',
}

# res = requests.delete(
#     url=
#     f'http://localhost:8000/api/organizations/{org_uuid}/chat_conversations/{chat_uuid}',
#     headers=headers,
# )

# res = requests.get(
#     url=f'http://localhost:8000/api/organizations',
#     headers=headers,
# )
# print(res.text)

res = requests.get(
    url=
    f'http://localhost:8000/api/organizations/{org_uuid}/chat_conversations',
    headers=headers,
)
print(res.text)

for convs in res.json():
  uuid = convs['uuid']
  res = requests.delete(
      url=
      f'http://localhost:8000/api/organizations/{org_uuid}/chat_conversations/{uuid}',
      headers=headers,
  )
  print(res.text)

# def generate_uuid():
#   random_uuid = uuid.uuid4()
#   random_uuid_str = str(random_uuid)
#   formatted_uuid = f"{random_uuid_str[0:8]}-{random_uuid_str[9:13]}-{random_uuid_str[14:18]}-{random_uuid_str[19:23]}-{random_uuid_str[24:]}"
#   return formatted_uuid

# uuid = generate_uuid()

# payload = json.dumps({"uuid": uuid, "name": ""})
# res = requests.post(
#     url=
#     f'http://localhost:8000/api/organizations/{org_uuid}/chat_conversations',
#     headers=headers,
#     data=payload,
# )

# print(res.text)
# chat_uuid = res.json()['uuid']
# prompt = '告诉我中国最大的湖泊'
# payload = json.dumps({
#     "completion": {
#         "prompt": f"{prompt}",
#         "timezone": "Asia/Kolkata",
#         "model": "claude-2"
#     },
#     "organization_uuid": f"{org_uuid}",
#     "conversation_uuid": f"{chat_uuid}",
#     "text": f"{prompt}",
#     "attachments": [],
#     'stream': True
# })

# response = requests.post(
#     url=f'http://localhost:8000/api/append_message',
#     headers=headers,
#     data=payload,
#     stream=True,
# )

# print('Claude>>> ', end='')
# for message_chunk in response.iter_lines():
#   message_chunk = message_chunk.decode('utf-8')
#   # print(message_chunk)
#   if message_chunk.strip() == '':
#     continue
#   if message_chunk.strip() == 'data: [DONE]':
#     continue
#   message_json = json.loads(message_chunk[6:])  # Skip the 'data: ' prefix
#   if "stop_reason" in message_json and message_json["stop_reason"] is not None:
#     break
#   message = message_json["completion"]
#   print(message, end='', flush=True)
# print()

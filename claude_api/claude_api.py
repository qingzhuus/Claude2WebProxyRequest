import json
import os
import uuid
from curl_cffi import requests
import requests as req
import re


class Client:

  def __init__(self, cookie, organization_id=None):
    self.cookie = cookie
    if organization_id:
      self.organization_id = organization_id
    # else:
    #   self.organizations = self.get_organizations()
    #   self.organization_id = self.organizations[0]['uuid']

  def get_organizations(self):
    url = "https://claude.ai/api/organizations"

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Content-Type': 'application/json',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}',
        "Host": "claude.ai",
        "Accept": "*/*",
    }
    # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    # "Accept": "*/*",
    # "Host": "claude.ai",
    # "Connection": "keep-alive"
    response = requests.get(url, headers=headers, impersonate="chrome110")
    return response
    # if response.status_code != 200:
    #   print(response.text)
    #   return response.text
    # res = json.loads(response.text)
    # return res

  def get_content_type(self, file_path):
    # Function to determine content type based on file extension
    extension = os.path.splitext(file_path)[-1].lower()
    if extension == '.pdf':
      return 'application/pdf'
    elif extension == '.txt':
      return 'text/plain'
    elif extension == '.csv':
      return 'text/csv'
    # Add more content types as needed for other file types
    else:
      return 'application/octet-stream'

  # Lists all the conversations you had with Claude
  def chat_conversations(self):
    url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations"

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Content-Type': 'application/json',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}'
    }

    response = requests.get(url, headers=headers, impersonate="chrome110")
    return response
    # conversations = response.json()

    # # Returns all conversation information in a list
    # if response.status_code == 200:
    #   return conversations
    # else:
    #   print(f"Error: {response.status_code} - {response.text}")

  # Send Message to Claude
  async def send_message(
      self,
      # prompt,
      # conversation_id,
      # attachment=None,
      send_payload,
      data_queue,
      timeout=500):
    url = "https://claude.ai/api/append_message"

    # Upload attachment if provided
    # attachments = []
    # if attachment:
    #   attachment_response = self.upload_attachment(attachment)
    #   if attachment_response:
    #     attachments = [attachment_response]
    #   else:
    #     return {"Error: Invalid file format. Please try again."}

    # # Ensure attachments is an empty list when no attachment is provided
    # if not attachment:
    #   attachments = []

    # payload = json.dumps({
    #     "completion": {
    #         "prompt": f"{prompt}",
    #         "timezone": "Asia/Kolkata",
    #         "model": "claude-2"
    #     },
    #     "organization_uuid": f"{self.organization_id}",
    #     "conversation_uuid": f"{conversation_id}",
    #     "text": f"{prompt}",
    #     "attachments": attachments
    # })
    payload = send_payload

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'text/event-stream, text/event-stream',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Content-Type': 'application/json',
        'Origin': 'https://claude.ai',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'TE': 'trailers',
        "Host": "claude.ai",
    }

    # async with requests.AsyncSession(impersonate="chrome107",
    #                                  headers={"Working": "Yes"}) as session:
    #   async with session.stream("GET",
    #                             "https://httpbin.org/stream/20") as response:
    #     response.raise_for_status()
    #     async for line in response.aiter_lines():
    #       print(json.loads(line)["headers"]["Working"])
    async with requests.AsyncSession(
        impersonate="chrome110",
        headers=headers,
    ) as session:
      async with session.stream('POST', url, data=payload,
                                timeout=timeout) as response:
        # response.raise_for_status()
        if response.status_code != 200 and response.status_code != 201:
          data_queue.put('[ERROR]')
          return
        async for line in response.aiter_lines():
          # print(line)
          # yield line.encode('utf-8')
          data_queue.put(line.decode('utf-8'))
        data_queue.put('[DONE]')

  # Deletes the conversation
  def delete_conversation(self, conversation_id):
    url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}"

    payload = json.dumps(f"{conversation_id}")
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
        'Content-Length': '38',
        'Referer': 'https://claude.ai/chats',
        'Origin': 'https://claude.ai',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}',
        'TE': 'trailers',
        "Host": "claude.ai",
        "Accept": "*/*",
    }
    # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    # "Accept": "*/*",
    # "Host": "claude.ai",
    # "Connection": "keep-alive"
    response = requests.delete(url,
                               headers=headers,
                               data=payload,
                               impersonate="chrome110")
    print(response.text)
    # Returns True if deleted or False if any error in deleting
    # if response.status_code == 204:
    #   return True
    # else:
    #   return False
    return response

  # Returns all the messages in conversation
  def chat_conversation_history(self, conversation_id):
    url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations/{conversation_id}"

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Content-Type': 'application/json',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}'
    }

    response = requests.get(url, headers=headers, impersonate="chrome110")

    # List all the conversations in JSON
    return response.json()

  def generate_uuid(self):
    random_uuid = uuid.uuid4()
    random_uuid_str = str(random_uuid)
    formatted_uuid = f"{random_uuid_str[0:8]}-{random_uuid_str[9:13]}-{random_uuid_str[14:18]}-{random_uuid_str[19:23]}-{random_uuid_str[24:]}"
    return formatted_uuid

  def create_new_chat(self, payload):
    url = f"https://claude.ai/api/organizations/{self.organization_id}/chat_conversations"
    # uuid = self.generate_uuid()

    # payload = json.dumps({"uuid": uuid, "name": ""})
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Content-Type': 'application/json',
        'Origin': 'https://claude.ai',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Cookie': self.cookie,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'TE': 'trailers',
        "Host": "claude.ai",
        "Accept": "*/*",
    }

    response = requests.post(url,
                             headers=headers,
                             data=payload,
                             impersonate="chrome110")

    # Returns JSON of the newly created conversation information
    return response

  # Resets all the conversations
  def reset_all(self):
    conversations = self.list_all_conversations()

    for conversation in conversations:
      conversation_id = conversation['uuid']
      delete_id = self.delete_conversation(conversation_id)

    return True

  def upload_attachment(self, file_path):
    if file_path.endswith('.txt'):
      file_name = os.path.basename(file_path)
      file_size = os.path.getsize(file_path)
      file_type = "text/plain"
      with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

      return {
          "file_name": file_name,
          "file_type": file_type,
          "file_size": file_size,
          "extracted_content": file_content
      }
    url = 'https://claude.ai/api/convert_document'
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://claude.ai/chats',
        'Origin': 'https://claude.ai',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}',
        'TE': 'trailers'
    }

    file_name = os.path.basename(file_path)
    content_type = self.get_content_type(file_path)

    files = {
        'file': (file_name, open(file_path, 'rb'), content_type),
        'orgUuid': (None, self.organization_id)
    }

    response = req.post(url, headers=headers, files=files)
    return response

  # Renames the chat conversation title
  def rename_chat(self, title, conversation_id):
    url = "https://claude.ai/api/rename_chat"

    payload = json.dumps({
        "organization_uuid": f"{self.organization_id}",
        "conversation_uuid": f"{conversation_id}",
        "title": f"{title}"
    })
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
        'Referer': 'https://claude.ai/chats',
        'Origin': 'https://claude.ai',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
        'Cookie': f'{self.cookie}',
        'TE': 'trailers'
    }

    response = requests.post(url,
                             headers=headers,
                             data=payload,
                             impersonate="chrome110")

    return response

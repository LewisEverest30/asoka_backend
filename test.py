# import asyncio
# from volcenginesdkarkruntime import AsyncArk

# client = AsyncArk(api_key="0b875849-8365-495f-acfa-3837842c4ba0")

#     # async def fetch_non_stream_response(self, messages):
#     #     stream = await self.client.chat.completions.create(
#     #         model="ep-20240726181421-rfxtl",
#     #         messages=messages,
#     #         stream=False
#     #     )
#     #     # async for completion in stream:
#     #     #     print(completion.choices[0].delta.content, end="")
#     #     #     return {
#     #     #         "role": "assistant",
#     #     #         "content": completion.choices[0].delta.content
#     #     #     }
#     #     return {
#     #         "role": "assistant",
#     #         "content": stream.choices[0].message.content
#     #     }




# async def fetch_non_stream_response(messages):
#     try:
#         print('running async func')
#         stream = await client.chat.completions.create(
#             model="ep-20240726181421-rfxtl",
#             messages=messages,
#             stream=False
#         )

#         print(stream.choices[0].message.content, end="")
#         return {
#             "role": "assistant",
#             "content": stream.choices[0].message.content
#         }

#         # for completion in stream:
#         #     print(completion.choices[0].delta.content, end="")
#         #     return {
#         #         "role": "assistant",
#         #         "content": completion.choices[0].delta.content
#         #     }
#     except Exception as e:
#         print(repr(e))


# if __name__ == '__main__':
#     new_msgs = [{"role": "user", "content": '告诉我你是谁'}, ]

#     try:
#         # result = asyncio.run(fetch_non_stream_response(new_msgs))
#         loop = asyncio.get_event_loop()

#         # result = loop.run_in_executor(None, fetch_non_stream_response, new_msgs)

#         result = loop.run_until_complete(fetch_non_stream_response(new_msgs))

#         print(result)
#     except Exception as e:
#         print(repr(e))



text = '### 张三\n ###黄水晶\n### 汝之八字，辛\n### 学业方面，汝具一定之天赋与毅力，然需更加勤奋\n### 汝之造温馨之家庭氛围'

parts = text.split('###')[1:]
new = []
for s in parts:
    new.append(s.strip())

print(new)








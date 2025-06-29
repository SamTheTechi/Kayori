from langchain_core.prompts import ChatPromptTemplate

calender_template = ChatPromptTemplate.from_messages([
    ("system",
        "You are an google calender manager you job is to\
        handle my google calender. this is the current time\
        {current_data_time} Respond concisely with only the necessary\
        scheduling details. Do not add extra commentary or text."
     ),
    ("placeholder", "{messages}"),
])

import langchain.


async def stream_and_handle_response(executer, payload, config, reply_target, tagged=False):
    response_text = ""
    final_text = ""
    tool_called = False

    async for chunk in executer.astream(
        payload,
        config,
        stream_mode="updates",
    ):
        if 'agent' in chunk:
            messages = chunk['agent'].get('messages', [])
            for msg in messages:
                if isinstance(msg, AIMessage):
                    if msg.content:
                        response_text += msg.content

                    if msg.tool_calls and not tool_called:
                        print("tool called")
                        tool_called = True
                        if response_text.strip():
                            if reply:
                                await reply_target.reply(response_text, mention_author=True)
                            else:
                                await reply_target.send(response_text)
                            final_text += response_text
                            response_text = ""

    if response_text.strip():
        if tagged:
            await reply_target.reply(response_text, mention_author=True)
        else:
            await reply_target.send(response_text)
        final_text += response_text

    return final_text

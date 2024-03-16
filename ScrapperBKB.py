import json
import time
from openai import OpenAI
from tavily import TavilyClient

# Initialize clients with API keys
client = OpenAI(api_key="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")

tavily_client = TavilyClient("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")

ASSISTANT_ID = "asst_zwZ6HRwSxdJvYGslXHIV92fL"

temp_check = ""
json_reply11 = None

# Function to perform a Tavily search
def tavily_search(query):
    search_result = tavily_client.get_search_context(query, search_depth="advanced", max_tokens=8000)
    return search_result

# Function to wait for a run to complete
def wait_for_run_completion(thread_id, run_id):
    global json_reply11
    while True:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print(f"Current run status: {run.status}")
        if run.status in ['completed', 'failed', 'requires_action']:
            content = print_messages_from_thread(thread_id=thread_id)
            
            if temp_check == "2":
                
                # print("Congratulations this is the JSON")
                # print(f"The content = {content}")
                json_reply11 = content
                print(f"json_reply11:  {json_reply11}")

            else:
                print(f"This is shit: {content}")

            return run

# Function to handle tool output submission
def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = tool.function.arguments

        if function_name == "tavily_search":
            output = tavily_search(query=json.loads(function_args)["query"])

        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )


def print_messages_from_thread(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    reply = []
    last_message =messages.data[0]
    role = last_message.role
    response = last_message.content[0].text.value
    reply.append(response)
    reply = "\n".join(reply)
    print(f"RESPONSE ---> {role.capitalize()}: ==> {response}")
    return response

# # Create an assistant
# def create_conversation(user_input, client, ASSISTANT_ID):
#     """
#     Creates a conversation thread, sends a user message, and manages the conversation flow.
    
#     :param user_input: The initial user input to start the conversation.
#     :param client: The OpenAI client instance.
#     :param ASSISTANT_ID: The ID of the assistant to use for the conversation.
#     :return: None
#     """
#     # Initialize conversation variables
#     temp_check = ""
#     cotent_temp = 1

#     # Create an assistant
#     assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

#     # Create a conversation thread
#     thread = client.beta.threads.create()
#     print(f"Thread: {thread}")

#     # Create a message in the thread with the user's input
#     message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_input)

#     print(f"this is content temp {cotent_temp}")
#     while cotent_temp < 4:
#         print(f"START {cotent_temp}")
#         print(f"Start temp_check: {temp_check}")
        
#         # Create a run
#         run_response = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)
#         print(f"Run ID: {run_response.id}")

#         # Wait for run to complete and manage conversation flow
#         completed_run = wait_for_run_completion(thread.id, run_response.id)
#         if completed_run.status == 'failed':
#             print("Run failed:", completed_run.error)
#             continue
#         elif completed_run.status == 'requires_action':
#             print("Handling required actions...")
#             run_response = submit_tool_outputs(thread.id, completed_run.id, completed_run.required_action.submit_tool_outputs.tool_calls)
#             completed_run = wait_for_run_completion(thread.id, run_response.id)

#             temp_check = str(cotent_temp)
#             message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=temp_check)
            

#         cotent_temp = cotent_temp + 1

#     return json_reply11
 

# checking = create_conversation(user_input= "www.interwood.pk", client = client, ASSISTANT_ID=ASSISTANT_ID )
# print(f"The result {checking}")

#----------------------------------------------------------------------------------------------------#

# assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

# thread = client.beta.threads.create()
# print(f"Thread: {thread}")

# user_input = input("You: ")
# # Create a message
# message = client.beta.threads.messages.create(
#     thread_id=thread.id,
#     role="user",
#     content=user_input,
# )

# cotent_temp = 1

# print(f"this is content temp {cotent_temp}")
# while cotent_temp<4:
#     print(f" START {cotent_temp}")
#     print(f" Start temp_check: {temp_check}")
#     # Create a run
#     run_response = client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=ASSISTANT_ID,
#     )
#     print(f"Run ID: {run_response.id}")

#     # Wait for run to complete
#     completed_run = wait_for_run_completion(thread.id, run_response.id)
#     # print(f"This is printing {run}")
#     if completed_run.status == 'failed':
#         print("completed_run.error")
#         print(completed_run.error)
#         continue
#     elif completed_run.status == 'requires_action':
#         print("-----1------")
#         run_response = submit_tool_outputs(thread.id, completed_run.id, completed_run.required_action.submit_tool_outputs.tool_calls)
#         print("----2-----")
#         completed_run = wait_for_run_completion(thread.id, run_response.id)

#         print("-----3------")
#         temp_check = str(cotent_temp)
#         message = client.beta.threads.messages.create(
#         thread_id=thread.id,
#         role="user",
#         content=temp_check,
#     )   
#         print("---4---")
               
#     cotent_temp = cotent_temp + 1
# print(f"the last message jsonreply11 {json_reply11}")

def initiate_conversation_and_retrieve_reply(user_input):
    global json_reply11, temp_check
    assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
    thread = client.beta.threads.create()
    print(f"Thread: {thread}")

    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_input)
    cotent_temp = 1

    while cotent_temp < 4:
        print(f" START {cotent_temp}")
        print(f" Start temp_check: {temp_check}")
        run_response = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)
        print(f"Run ID: {run_response.id}")

        completed_run = wait_for_run_completion(thread.id, run_response.id)
        if completed_run.status == 'failed':
            print("completed_run.error")
            print(completed_run.error)
            continue
        elif completed_run.status == 'requires_action':
            print("Handling required actions...")
            run_response = submit_tool_outputs(thread.id, completed_run.id, completed_run.required_action.submit_tool_outputs.tool_calls)
            completed_run = wait_for_run_completion(thread.id, run_response.id)

            temp_check = str(cotent_temp)
            message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=temp_check)

        cotent_temp += 1
    
    return json_reply11

# Example usage
# user_input = "www.interwood.pk"  # This can be replaced with input("You: ") for interactive use
# final_reply = initiate_conversation_and_retrieve_reply(user_input)
# print(f"The final message json_reply11: {final_reply}")
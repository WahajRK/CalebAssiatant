import openai
from dotenv import find_dotenv, load_dotenv
import time
import logging
from datetime import datetime
import streamlit as st
from ScrapperBKB import*
load_dotenv()

client = openai.OpenAI()
assistant_id_default = "asst_YDMjFbbE1aArtjg87pBRvRyw"
assistant_id_alternate = "asst_56AYtZNNVTDef41qx2vxgkVb"

class AssistantManager:
   #thread_id = None

    def __init__(self, thread_id = None, initial_assistant_id=assistant_id_default):
        self.client = client
        self.assistant = None
        self.assistant_id = initial_assistant_id
        self.thread_id = thread_id
        self.thread = None
        self.run = None
        self.pricingJson = None
        self._setup_assistant()
        self._setup_thread()

    def _setup_assistant(self):
        # Retrieve Existing assistant if already exists
        self.assistant = self.client.beta.assistants.retrieve(
            assistant_id=self.assistant_id
        )
    def _setup_thread(self):
        if self.thread_id:
            try:
                self.thread = self.client.beta.threads.retrieve(
                    thread_id=self.thread_id
                )
            except Exception as e:
                print(f"Error retrieving thread: {e}")
                self.thread = None
        else:
            self.create_thread()    
  
    def switch_assistant(self, new_assistant_id):
        self.assistant_id = new_assistant_id
        self._setup_assistant()

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                tools=tools,
                model=self.model
            )
            AssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"AssistantID::: {self.assistant.id}")

    def create_thread(self):
        if not self.thread:
            thread_obj = self.client.beta.threads.create()
            AssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"ThreadID:::{self.thread.id}")

    
    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id= self.thread.id,
                role=role,
                content=content
            )
    def run_assistant(self, instructions):
        if self.thread and self.assistant:
            run_obj = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions
            )
            self.run = run_obj
            print(f"Run Created with ID: {self.run.id}")
    def process_message(self):
        if self.thread:
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id
                )
            pricingJson = []
            
            last_message = messages.data[0]
            role = last_message.role
            response = last_message.content[0].text.value
            pricingJson.append(response)

            self.pricingJson = "\n".join(pricingJson)
            print(f"RESPONSE----> {role.capitalize()}: ==> {response}")

    # For StreamLit
    def get_pricingJson(self):
        return self.pricingJson
    
    def wait_for_completion(self):
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id= self.thread.id,
                    run_id=self.run.id
                )
                print(f"RUN STATUS::: {run_status.model_dump_json(indent = 4)}")
                if run_status.status =="completed":
                    self.process_message()
                    break
                elif run_status.status == "in_progress":
                    print("Generating Response...")
                else:
                    print(f"Unhandled run status: {run_status.status}")
                    break

    #run the steps
                    
    def run_steps(self):
        if self.run:
            try:
                run_steps = self.client.beta.threads.runs.steps.list(
                    thread_id=self.thread,
                    run_id=self.run
                )
                print(f"Run-Step for {self.run.id} : {run_steps}")
            except Exception as e:
                print(f"Error Retrieving steps for run {self.run.id}:{e}")
        else:
            print("No Run has been initiated.")


from langgraph.graph import StateGraph,START,END
from openai import OpenAI
from huggingface_hub import InferenceClient
from IPython.display import display
import base64
from io import BytesIO
import os
from dotenv import load_dotenv
import random
import json
import time
from PIL import Image

load_dotenv()

NVIDIA_TOKEN = os.getenv("NVIDIA_API_KEY","")
HF_TOKEN = os.getenv("HF_TOKEN","")
NUM_ATTEMPTS = 3

class LLMClass:

    filename = ""

    def __init__(self):
        self.filename = str(random.randint(100000, 999999)) + ".png"

    def image_to_base64_data_url(self,image_path):
        img = Image.open(image_path)

        buffered = BytesIO()
        img.save(buffered, format="PNG")

        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return f"data:image/png;base64,{img_base64}"        

    def call_nvidia(self,prompt,generate=True,feedback=""):
        generator_prompt = f"""
            You are a Master Designer specializing in high-definition, bright, and vibrant movie-style thumbnails.

            LIGHTING & COLOR (Anti-Darkness):
                High-Key Lighting: Use bright studio lighting or natural sunlight. Avoid deep shadows or "moody/shady" filters.
                Vibrancy: Ensure high saturation and "HD" clarity. Every corner of the image should be visible and crisp.

            SCENOGRAPHY & PROPS (The Podcast/Context Rule):
                Environmental Context: Never generate a subject in a vacuum. Surround the subject with 2-3 iconic props that tell the story .
                English Text: Any text in the image must be in English. Keep it short, bold, and high-contrast.
                Dynamic Action: Whenever possible, depict an action 
                Human Figures: Include people only if the user prompt implies a human presence 

            COMPOSITION:
                Wide/Medium Shot: Avoid extreme close-ups that crowd the frame. Ensure the subject and their environment are both visible.

            {feedback}
        """        
        
        validator_prompt = """
            You are a Senior Art Director. Reject any image that feels "dead," "dark," or "empty."

            CORE CHECKS:
                Luminance Check: Is the image bright and clear? If it is "shady," dark, or uses muddy colors, FAIL it for "Low Exposure."
                Contextual Narrative: Does the image contain objects that explain the prompt? 
                Action/Energy: Is there a sense of movement or life? .
                Language Check: Is the text in English? Is it legible?

            Response Format (JSON):
            {
                "status": "pass" | "fail",
                "critique_type": "physics" | "logic" | "aesthetic",
                "feedback": "Feedback must describe the physical reason for failure without using predefined examples."
            }
        """

        system_prompt = ""
        if generate:
            system_prompt = generator_prompt
        else:
            system_prompt = validator_prompt
        
        client = OpenAI(base_url = "https://integrate.api.nvidia.com/v1", api_key = NVIDIA_TOKEN)

        if generate:
            messages = [{"content":f" {system_prompt}  :  {prompt}","role":"user"}]
        else:
            image_encoded = self.image_to_base64_data_url(image_path=self.filename)
            messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": system_prompt  
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_encoded 
                                }
                            }
                        ]
                    }
                ]            
        completion = client.chat.completions.create(
            model="nvidia/llama-3.1-nemotron-nano-vl-8b-v1",
            messages=messages, 
            temperature=1.00,
            top_p=0.01,
            max_tokens=1024,
            stream=False
        )

        response = completion.choices[0].message.content
        return response
    
    def call_flux(self,image_prompt):

        client = InferenceClient(api_key=HF_TOKEN)

        for attempt in range(3):                        
            print(f"Sending request to Hugging Face... attempt : {attempt}")
            try:
                # We target a reliable, high-quality open-source model
                image = client.text_to_image(
                    image_prompt,   
                    model="stabilityai/stable-diffusion-3-medium-diffusers"                 
                )

                # The output is natively a PIL Image object
                image.save(self.filename)
                print(f"Successfully saved image as {self.filename}!")
                break
            except Exception as e:
                print("Generation failed:", e)
                time.sleep(5 * (attempt + 1))
        return ""
    
    def generate_prompt(self, user_prompt, feedback=""):
        feedback_str = f"Previous Feedback: {feedback}" if feedback else ""
        return self.call_nvidia(prompt=user_prompt, generate=True, feedback=feedback_str)        
            
    def generate_image(self,prompt):
        self.call_flux(prompt)
        return self.filename
    
    def validate_image(self,image_path):
        raw_response = self.call_nvidia(prompt=f"Analyze image context: {image_path}", generate=False)
        try:
            # Safely convert LLM text block to JSON dict
            return json.loads(raw_response)
        except Exception:
            # Fallback if the LLM output structural JSON format slips up
            return {"status": "pass", "feedback": "Failed to parse JSON validation response."}        
    
class YTThumbnail:

    user_prompt:str = ""
    feedback:list = []
    refined_prompt:str = ""
    retry_count:int = 0
    workflow_object:any
    agent:LLMClass

    def __init__(self,user_prompt):
        self.user_prompt = user_prompt
        self.agent = LLMClass()
        self.build_graph()

    def generate_thumbnail(self):
        initial_state = {
            'user_prompt': self.user_prompt,
            'retry_count': 0,
            'feedback': ""
        }        
        result = self.workflow_object.invoke(initial_state)
        print("\n--- Final Graph Output ---")
        print(result)
                        
    def display_workflow(self):        
        display(Image(self.workflow_object.get_graph().draw_mermaid_png()))

    def approval_router(self,state):
        if state.get("validimage"):
            return "approved"

        retry_count = state.get("retry_count", 0)

        if retry_count >= NUM_ATTEMPTS:
            return "failed"

        return "retry"

    def generate_refined_prompt(self,state):
        refined_prompt = self.agent.generate_prompt(user_prompt=state.get('user_prompt'),
                                                    feedback=state.get('feedback', ""))

        return {
            'user_prompt': state.get('user_prompt'), 
            'refined_prompt': refined_prompt,
            'retry_count': state.get('retry_count', 0)  # <-- Carry forward
        }

    def generate_image(self,state):
        image_name = self.agent.generate_image(state.get('refined_prompt'))
        return {'generated_image': image_name,
                'retry_count': state.get('retry_count', 0)}

    def image_validation(self,state):
        validate_obj = self.agent.validate_image(state.get('generated_image'))
        is_valid_image = (validate_obj["status"] == "pass")
        retry_count = state.get("retry_count", 0)
        if not is_valid_image:
            retry_count += 1
        feedback = validate_obj["feedback"]
        return {'validimage':is_valid_image,"feedback":feedback,"retry_count": retry_count}


    #def generate_thumbnail(self):
    def build_graph(self):

        workflow  = StateGraph(dict)

        workflow.add_node('refineprompt',self.generate_refined_prompt)
        workflow.add_node('imagegenerate',self.generate_image)
        workflow.add_node('imagevalidation',self.image_validation)

        workflow.add_edge(START,'refineprompt')
        workflow.add_edge('refineprompt','imagegenerate')
        workflow.add_edge('imagegenerate','imagevalidation')
        workflow.add_conditional_edges('imagevalidation',
                                       self.approval_router,
                                       {
                                         'approved': END,
                                         'retry': 'refineprompt',
                                         'failed': END
                                       })

        graph = workflow.compile()
        self.workflow_object = graph
        
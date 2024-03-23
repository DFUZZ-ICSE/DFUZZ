from collections import namedtuple

import openai
# from openai import OpenAI

Prompt = namedtuple("Prompt", ["instruction", "input"])


class OpenAIModel:
    def __init__(self, model_name="gpt-3.5-turbo-1106", api_key=None, **kwargs):
        """
        Initialize an OpenAIModel instance.
        Args:
            model_name (str): Name of the OpenAI model.
            api_key (str): OpenAI API key.
        """
        self.model_name = model_name
        self.api_key = api_key
        self.kwargs = kwargs

    def generate(self, instruction, input):
        """
        Generate a completion using the OpenAI API.
        Args:
            input (str): User input to be processed by the model.
            instruction (str): System message that guides the conversation.
        Returns:
            dict: Response from the OpenAI API.
        """

        # Create a chat completion with OpenAI
        completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": input}
                ],
                api_key=self.api_key,
                temperature = 0,
                # **self.kwargs,
        )

        # client = OpenAI(
        #     api_key=self.api_key,
        # )
        # completion = client.chat.completions.create(
        #     messages=[
        #         {"role": "system", "content": instruction},
        #         {"role": "user", "content": input}
        #     ],
        #     model="gpt-3.5-turbo-1106",
        #     temperature = 0,
        # )

        return completion

    def set_key(self, key):
        """
        Set the OpenAI API key.
        """
        self.api_key = key

import json

from langchain.prompts.prompt import PromptTemplate
from langchain import FewShotPromptTemplate

with open("./assets/templates/badcase.json") as f:
    examples = json.load(f)

example_template = """
  AI: {AI}
  Expert: {Expert}
"""

example_prompt = PromptTemplate(
    input_variables=["AI", "Expert"],
    template=example_template
)

prefix = """
下面的对话文本是来自专家和AI之间的对话。通常，AI需要首先向专家来询问问题，然后引导专家来回答一些问题，这里有一些例子:
"""

suffix = """
Expert: {Expert}
AI:
"""

FEW_SHOT_PROMPT_TEMPLATE = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix=prefix,
    suffix=suffix,
    input_variables=["Expert"],
    example_separator="\n\n"
)


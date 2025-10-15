import torch
from transformers import PegasusTokenizer, PegasusForConditionalGeneration
model_name = "./pegasus-samsum-manual"  # path to your saved model
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

text = """A: Hey Tom, are you free tomorrow?
B: Not sure, why?
A: I want to visit the animal shelter to adopt a puppy.
B: That sounds fun, I’ll come with you!"""

inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="longest").to(device)
summary_ids = model.generate(
    inputs["input_ids"],
    attention_mask=inputs["attention_mask"],
    max_length=50,
    num_beams=4,
    early_stopping=True
)
print("\nInput Dialogue:\n", text)
print("\nGenerated Summary:\n", tokenizer.decode(summary_ids[0], skip_special_tokens=True))

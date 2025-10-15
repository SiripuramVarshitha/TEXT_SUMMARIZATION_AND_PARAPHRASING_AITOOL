import os
from transformers import PegasusForConditionalGeneration, PegasusTokenizer

# --------------------- CONFIG ---------------------
model_path = r"C:\Users\varsh\OneDrive\Desktop\clonedproject\Text-morph---Advanced-Summarization-Using-AI\pegasus-paraphraser"

# model_path = "./pegasus-paraphraser"

print(f"🔹 Loading paraphraser model from {model_path}...")
tokenizer = PegasusTokenizer.from_pretrained(model_path, local_files_only=True)
model = PegasusForConditionalGeneration.from_pretrained(model_path, local_files_only=True)

# --------------------- FUNCTIONS ---------------------
def generate_paraphrase(text, max_length=100, num_beams=5):
    """Generate a paraphrased version of text"""
    inputs = tokenizer([text], truncation=True, padding="longest", return_tensors="pt")
    outputs = model.generate(
        inputs.input_ids,
        max_length=max_length,
        num_beams=num_beams,
        early_stopping=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def paraphrase_long_text(text, chunk_size=512, **kwargs):
    """Paraphrase long text by splitting into chunks"""
    tokens = tokenizer.tokenize(text)
    paraphrased_chunks = []

    for i in range(0, len(tokens), chunk_size):
        chunk = tokenizer.convert_tokens_to_string(tokens[i:i+chunk_size])
        paraphrased_chunks.append(generate_paraphrase(chunk, **kwargs))

    return " ".join(paraphrased_chunks)

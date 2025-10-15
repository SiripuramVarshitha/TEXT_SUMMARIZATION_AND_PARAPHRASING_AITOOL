import os
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from concurrent.futures import ThreadPoolExecutor
# --------------------------- SAVE PATH ---------------------------
SAVE_PATH = "summarization_samples"
os.makedirs(SAVE_PATH, exist_ok=True)
# --------------------------- LOAD MODEL ---------------------------
# model_name = "./pegasus-samsum-manual"
# tokenizer = PegasusTokenizer.from_pretrained(model_name)
# model = PegasusForConditionalGeneration.from_pretrained(model_name)
model_path = r"C:\Users\varsh\OneDrive\Desktop\clonedproject\Text-morph---Advanced-Summarization-Using-AI\pegasus-samsum-manual"
# model_path = "./backend/pegasus-samsum-manual"

tokenizer = PegasusTokenizer.from_pretrained(model_path, local_files_only=True)
model = PegasusForConditionalGeneration.from_pretrained(model_path, local_files_only=True)

def chunk_text_tokenwise(text, max_chunk_tokens=512):
    """Split text into chunks by token count for long input handling."""
    tokens = tokenizer.tokenize(text)
    chunks = []
    for i in range(0, len(tokens), max_chunk_tokens):
        chunk_tokens = tokens[i:i + max_chunk_tokens]
        chunk_text = tokenizer.convert_tokens_to_string(chunk_tokens)
        chunks.append(chunk_text)
    return chunks

def generate_summary(
    text,
    max_length=40,
    min_length=10,
    length_penalty=1.0,
    num_beams=3,
    temperature=None,
    no_repeat_ngram_size=None,
    repetition_penalty=None
):
    """Generate a summary for a single text chunk."""
    inputs = tokenizer([text], truncation=True, padding='longest', return_tensors="pt")

    bad_words = ["series", "part", "article", "copyright", "postmedia",
                 "http", "www", ".com", "email", "share", "click",
                 "including", "such as"]
    bad_word_ids = [tokenizer.encode(word, add_special_tokens=False) for word in bad_words]

    generate_kwargs = dict(
        max_length=max_length,
        min_length=min_length,
        length_penalty=length_penalty,
        num_beams=num_beams,
        early_stopping=True,
        bad_words_ids=bad_word_ids
    )
    if temperature is not None:
        generate_kwargs["temperature"] = temperature
    if no_repeat_ngram_size is not None:
        generate_kwargs["no_repeat_ngram_size"] = no_repeat_ngram_size
    if repetition_penalty is not None:
        generate_kwargs["repetition_penalty"] = repetition_penalty

    summary_ids = model.generate(inputs.input_ids, **generate_kwargs)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def summarize_chunk(chunk, params):
    """Summarize a single chunk with given parameters."""
    return generate_summary(
        chunk,
        max_length=params["max_length"],
        min_length=params["min_length"],
        length_penalty=params["length_penalty"],
        num_beams=params["num_beams"]
    )

# --------------------------- LONG TEXT HANDLING ---------------------------
def summarize_long_text(text, chunk_token_limit=512, summary_params=None):
    """
    Summarize long text by splitting into chunks, summarizing each,
    and then aggregating.
    """
    if summary_params is None:
        summary_params = {"max_length": 100, "min_length": 80, "length_penalty": 2.0, "num_beams": 6}

    chunks = chunk_text_tokenwise(text, max_chunk_tokens=chunk_token_limit)

    # Parallel summarization
    with ThreadPoolExecutor(max_workers=4) as executor:
        chunk_summaries = list(executor.map(lambda c: summarize_chunk(c, summary_params), chunks))

    aggregated_summary = " ".join(chunk_summaries)

    # Final hierarchical summary
    final_summary = generate_summary(
        aggregated_summary,
        max_length=summary_params["max_length"],
        min_length=summary_params["min_length"],
        length_penalty=summary_params["length_penalty"],
        temperature=0.3,
        no_repeat_ngram_size=4,
        repetition_penalty=2.5,
        num_beams=summary_params["num_beams"]
    )
    return final_summary

# --------------------------- LEVEL-BASED INTERFACE ---------------------------
def summarize_text_by_level(text, level="Easy"):
    """
    Generate summary based on user-selected level.
    Levels: Easy, Medium, Long
    """
    levels = {
        "Easy": {"max_length": 40, "min_length": 10, "length_penalty": 1.0, "num_beams": 3},
        "Medium": {"max_length": 70, "min_length": 30, "length_penalty": 1.5, "num_beams": 5},
        "Long": {"max_length": 120, "min_length": 50, "length_penalty": 2.0, "num_beams": 6}
    }

    params = levels.get(level, levels["Easy"])

    # Use long text summarization if text has more than 512 tokens
    if len(tokenizer.tokenize(text)) > 512:
        return summarize_long_text(text, summary_params=params)
    else:
        return generate_summary(text, **params)

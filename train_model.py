import torch
from datasets import load_dataset
from transformers import PegasusTokenizer, PegasusForConditionalGeneration, AdamW
from torch.utils.data import DataLoader
dataset = load_dataset("csv", data_files={
    "train": "data/train_clean.csv",
    "validation": "data/val_clean.csv"
})

print(dataset)

def is_valid(example):
    return bool(example["dialogue_clean"]) and bool(example["summary_clean"])

dataset = dataset.filter(is_valid)

model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

max_input_length = 256
max_target_length = 64

def preprocess(batch):
    dialogues = [str(x) if x is not None else "" for x in batch["dialogue_clean"]]
    summaries = [str(x) if x is not None else "" for x in batch["summary_clean"]]

    inputs = tokenizer(
        dialogues,
        truncation=True,
        padding="max_length",
        max_length=max_input_length
    )

    labels = tokenizer(
        summaries,
        truncation=True,
        padding="max_length",
        max_length=max_target_length
    )

    inputs["labels"] = labels["input_ids"]
    return inputs
train_subset = dataset["train"].select(range(200))
train_dataset = train_subset.map(preprocess, batched=True, remove_columns=["dialogue_clean", "summary_clean"])
val_dataset = dataset["validation"].map(preprocess, batched=True, remove_columns=["dialogue_clean", "summary_clean"])

train_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
val_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=2)



optimizer = AdamW(model.parameters(), lr=5e-5)

epochs = 1  
model.train()

for epoch in range(epochs):
    print(f"\nEpoch {epoch+1}/{epochs}")
    total_loss = 0
    for step, batch in enumerate(train_loader):
        optimizer.zero_grad()
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        if step % 100 == 0:
            print(f"Step {step} - Loss: {loss.item():.4f}")

    avg_loss = total_loss / len(train_loader)
    print(f"Epoch {epoch+1} finished. Avg Loss = {avg_loss:.4f}")

save_path = "./pegasus-samsum-manual"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print(f"✅ Model saved at {save_path}")

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


MODEL_NAME = "mdhugol/indonesia-bert-sentiment-classification"


tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME
)


LABELS = {
    0: "Positif",
    1: "Netral",
    2: "Negatif"
}


def classify_sentiment(text):

    if not text:
        return "Netral"

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():

        outputs = model(
            **inputs
        )

    prediction = torch.argmax(
        outputs.logits,
        dim=1
    ).item()

    return LABELS.get(
        prediction,
        "Netral"
    )


if __name__ == "__main__":

    contoh = [
        "Pelayanannya bagus sekali",
        "Jalan ini rusak parah",
        "Hari ini ada kegiatan di Karawang"
    ]

    for teks in contoh:

        print(
            teks,
            "->",
            classify_sentiment(teks)
        )
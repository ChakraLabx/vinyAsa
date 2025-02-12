from PIL import Image, ImageDraw, ImageFont
import torch
import numpy as np
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
import torch.nn.functional as F

# Load and prepare the image
image = Image.open("/home/zok/Pictures/Screenshots/Screenshot from 2025-01-27 07-46-56.png")
image = image.convert("RGB")
width, height = image.size

# Initialize processor and model
processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")
model = LayoutLMv3ForTokenClassification.from_pretrained("nielsr/layoutlmv3-finetuned-funsd")
device = torch.device('cpu' if torch.cuda.is_available() else 'cpu')
model.to(device)

# Define labels
labels = ['0', '1', '2']
id2label = {v: k for v, k in enumerate(labels)}
label2id = {k: v for v, k in enumerate(labels)}
label2color = {'text': 'violet', 'key': 'orange', 'value': 'pink'}

# Process the image in chunks
max_length = 512
all_predictions = []
all_boxes = []

# First, get the full encoding
full_encoding = processor(image, return_tensors="pt", return_offsets_mapping=True)
full_input_ids = full_encoding.input_ids[0]
full_bbox = full_encoding.bbox[0]
full_offset_mapping = full_encoding.offset_mapping[0]

for i in range(0, len(full_input_ids), max_length):
    # Extract a chunk of input_ids and corresponding bboxes
    chunk_input_ids = full_input_ids[i:i+max_length]
    chunk_bbox = full_bbox[i:i+max_length]
    chunk_offset_mapping = full_offset_mapping[i:i+max_length]

    # Create a new encoding for this chunk
    chunk_encoding = {
        'input_ids': chunk_input_ids.unsqueeze(0),
        'bbox': chunk_bbox.unsqueeze(0),
        'attention_mask': torch.ones_like(chunk_input_ids).unsqueeze(0)
    }

    # Ensure all tensors are on the same device as the model
    chunk_encoding = {k: v.to(device) for k, v in chunk_encoding.items()}

    # Forward pass
    with torch.no_grad():
        outputs = model(**chunk_encoding)

    # Get the logits directly (shape: [batch_size, sequence_length, num_labels])
    logits = outputs.logits.squeeze()  # Squeeze to remove batch dimension if needed

    # Optionally, convert logits to probabilities
    probabilities = F.softmax(logits, dim=-1)  # Softmax across the last dimension (num_labels)

    # Process the probabilities
    predictions = probabilities.tolist()  # Convert to a Python list

    token_boxes = chunk_bbox.tolist()
    is_subword = np.array(chunk_offset_mapping.tolist())[:,0] != 0

    # Store predictions and boxes for non-subword tokens
    chunk_predictions = [pred for idx, pred in enumerate(predictions) if not is_subword[idx]]
    chunk_boxes = [box for idx, box in enumerate(token_boxes) if not is_subword[idx]]

    all_predictions.extend(chunk_predictions)
    all_boxes.extend(chunk_boxes)

# Unnormalize boxes
def unnormalize_box(bbox, width, height):
    return [
        width * (bbox[0] / 1000),
        height * (bbox[1] / 1000),
        width * (bbox[2] / 1000),
        height * (bbox[3] / 1000),
    ]

true_boxes = [unnormalize_box(box, width, height) for box in all_boxes]

# Draw predictions on the image
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

def iob_to_label(label):
    return label if label else 'other'

# Draw rectangles and print probabilities
for prediction, box in zip(all_predictions, true_boxes):
    draw.rectangle(box, outline="blue")  # Just drawing the boxes in blue for now

    # # Print each label's probability for the current token
    # print(f"Token box: {box}")
    # for label_id, prob in enumerate(prediction):
    #     label = id2label[label_id]
    #     print(f"  {label}: {prob:.4f}")

    # Optionally, you can label the image with the highest probability prediction:
    max_prob_label_id = np.argmax(prediction)
    predicted_label = id2label[max_prob_label_id]
    draw.text((box[0]+10, box[1]-10), text=predicted_label, fill=label2color[predicted_label], font=font)

# Display or save the image
image.save("labeled_image.jpg")

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import qrcode
import os
import json
import cloudinary
import cloudinary.uploader
from twilio_func import *
from PIL import Image

# Configure Cloudinary
cloudinary.config(
    cloud_name="dlonah39r",
    api_key="557486886891483",
    api_secret="p5I89-L1C62faI3S6VnyDkBvprM"
)

# Create Flask app
app = Flask(__name__)

# File for local JSON storage
DATA_FILE = "data.json"

# Ensure necessary directories exist
STATIC_FOLDER = "static"
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

# Path to the base image (update this with your actual image)
BASE_IMAGE_PATH = "image/Scann.jpg"

# Function to load data from JSON file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []

# Function to save data to JSON file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Function to create an image with QR code
def create_image_with_qr(base_image_path, qr_data, output_path):
    try:
        base_image = Image.open(base_image_path).convert("RGBA")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        base_width, base_height = base_image.size
        qr_box_size = int(base_width * 0.185)
        qr_image = qr_image.resize((qr_box_size, qr_box_size))

        qr_x = int(base_width * 0.084)
        qr_y = int(base_height * 0.83)

        final_image = base_image.copy()
        final_image.paste(qr_image, (qr_x, qr_y), qr_image)

        final_image.convert("RGB").save(output_path, "JPEG")
        return output_path
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

@app.route("/sms", methods=['POST'])
def reply():
    incoming_msg = request.form.get('Body', '').strip().lower()
    response = MessagingResponse()
    message = response.message()

    try:
        if incoming_msg in ["start", "bonjour", "السلام عليكم"]:
            message.body("Bonjour! Veuillez entrer votre nom :")
            return str(response)

        elif incoming_msg.isalpha():
            name = incoming_msg.capitalize()

            # Load existing data
            users = load_data()

            # Check if name already exists
            if name not in [user["name"] for user in users]:
                users.append({"name": name})
                save_data(users)

            qr_data = f"Nom: {name}"
            output_image_path = os.path.join(STATIC_FOLDER, f"{name}_final.jpg")

            final_image_path = create_image_with_qr(BASE_IMAGE_PATH, qr_data, output_image_path)

            if final_image_path:
                upload_result = cloudinary.uploader.upload(final_image_path)
                image_url = upload_result['secure_url']
                message.media(image_url)
            else:
                message.body("Une erreur s'est produite lors de la création de l'image.")

        else:
            message.body("Entrée non valide. Veuillez entrer un nom valide (seulement des lettres).")

    except Exception as e:
        print(f"Error: {e}")
        message.body("Une erreur s'est produite. Veuillez réessayer plus tard.")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)

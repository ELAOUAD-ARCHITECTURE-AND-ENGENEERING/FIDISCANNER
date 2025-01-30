from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from gsheet_func import save_reminder_date
import qrcode
import os
import cloudinary
import cloudinary.uploader
from PIL import Image

# Configure Cloudinary
cloudinary.config(
    cloud_name="dlonah39r",  # Your Cloudinary cloud name
    api_key="557486886891483",  # Your Cloudinary API key
    api_secret="p5I89-L1C62faI3S6VnyDkBvprM"  # Your Cloudinary API secret
)

# Create Flask app
app = Flask(__name__)

# Ensure necessary directories exist
STATIC_FOLDER = "static"
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

# Path to the base image (update this with your actual image)
BASE_IMAGE_PATH = "image/Scann.jpg"  # Ensure this image exists

def create_image_with_qr(base_image_path, qr_data, output_path):
    """Generate an image with an embedded QR code perfectly inside the white box."""
    try:
        # Load the base image
        base_image = Image.open(base_image_path).convert("RGBA")

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        # Resize QR code to fit better inside the white box
        base_width, base_height = base_image.size
        qr_box_size = int(base_width * 0.185)  # Adjusted size
        qr_image = qr_image.resize((qr_box_size, qr_box_size))

        # Adjusted position to move it **down inside the white box**
        qr_x = int(base_width * 0.084)  # Keep it centered horizontally
        qr_y = int(base_height * 0.83)  # Move it lower inside the box

        # Overlay QR code on base image inside the white box
        final_image = base_image.copy()
        final_image.paste(qr_image, (qr_x, qr_y), qr_image)

        # Save final image as JPEG
        final_image.convert("RGB").save(output_path, "JPEG")
        return output_path
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None


@app.route("/sms", methods=['POST'])
def reply():
    """Handle incoming SMS and generate QR code overlayed on an image."""
    incoming_msg = request.form.get('Body', '').strip().lower()
    response = MessagingResponse()
    message = response.message()

    try:
        if incoming_msg in ["start", "bonjour", "السلام عليكم"]:
            message.body("Bonjour! Veuillez entrer votre nom :")
            return str(response)

        elif incoming_msg.isalpha():  # Check if input is a valid name
            name = incoming_msg.capitalize()
            save_reminder_date(name)  # Save name in Google Sheets

            qr_data = f"Nom: {name}"  # Data for QR code
            output_image_path = os.path.join(STATIC_FOLDER, f"{name}_final.jpg")

            # Generate image with QR code overlay
            final_image_path = create_image_with_qr(BASE_IMAGE_PATH, qr_data, output_image_path)

            if final_image_path:
                # Upload the processed image to Cloudinary
                upload_result = cloudinary.uploader.upload(final_image_path)
                image_url = upload_result['secure_url']

                # Send the final image back to the user
                """ message.body(f"Merci, {name}! Voici votre image avec QR code") """
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

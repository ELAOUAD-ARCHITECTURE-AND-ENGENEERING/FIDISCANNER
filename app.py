from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from gsheet_func import save_reminder_date
import qrcode
import os
import cloudinary
import cloudinary.uploader

# Configure Cloudinary
cloudinary.config(
    cloud_name="dlonah39r",
    api_key="557486886891483",
    api_secret="p5I89-L1C62faI3S6VnyDkBvprM"
)

# Create Flask app
app = Flask(__name__)

# Ensure the "static" directory exists
if not os.path.exists("static"):
    os.makedirs("static")

@app.route("/sms", methods=['POST'])
def reply():
    incoming_msg = request.form.get('Body', '').strip().lower()  # Get incoming message
    response = MessagingResponse()
    message = response.message()

    try:
        # Handle "start" command
        if incoming_msg in ["start", "bonjour", "السلام عليكم"]:
            reply = "Bonjour! Veuillez entrer votre nom :"
            message.body(reply)
            return str(response)

        # Handle name input and generate QR code
        elif incoming_msg.isalpha():  # Check if input is a valid name (letters only)
            name = incoming_msg.capitalize()  # Capitalize the first letter
            save_reminder_date(name)
            qr_data = f"Nom: {name}"  # QR code content
            qr_code_path = os.path.join("static", f"{name}_qr.png")

            # Generate and save QR code in the static directory
            qr_code = qrcode.make(qr_data)
            qr_code.save(qr_code_path)

            # Upload QR code to Cloudinary
            upload_result = cloudinary.uploader.upload(qr_code_path)
            qr_url = upload_result['secure_url']  # Get the public URL from Cloudinary

            # Send QR code back to user
            reply = f"Merci, {name}! Votre nom a été enregistré avec succès. Voici votre QR code :"
            message.body(reply)
            message.media(qr_url)  # Send the image URL to Twilio

        else:
            reply = "Entrée non valide. Veuillez entrer un nom valide (seulement des lettres)."
            message.body(reply)

    except Exception as e:
        print(f"Error: {e}")  # Log the error
        message.body("Une erreur s'est produite. Veuillez réessayer plus tard.")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, send_file, url_for
from twilio.twiml.messaging_response import MessagingResponse
import qrcode
import os

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
            # Inside the elif block where QR code is generated:
            qr_data = f"Nom: {name}"  # QR code content
            qr_code_path = os.path.join("static", f"{name}_qr.png")

            # Generate and save QR code in the static directory
            qr_code = qrcode.make(qr_data)
            reply = f"{name}_qr.png"
            qr_code.save(qr_code_path)

            # Send QR code back to user
            qr_url = url_for('static', filename=f"{name}_qr.png", _external=True)  # Get the external URL for static file
            reply = f"Merci, {name}! Votre nom a été enregistré avec succès. Voici votre QR code :"
            message.body(reply)
            message.media(qr_url)  # Twilio will send the image to the user

        else:
            reply = "Entrée non valide. Veuillez entrer un nom valide (seulement des lettres)."
            message.body(reply)

    except Exception as e:
        print(f"Error: {e}")  # Log the error
        message.body("Une erreur s'est produite. Veuillez réessayer plus tard.")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)

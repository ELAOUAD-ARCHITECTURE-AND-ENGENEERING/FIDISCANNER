from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from gsheet_func import save_reminder_date  # Ensure this function works correctly
from dateutil.parser import parse

app = Flask(__name__)

@app.route("/sms", methods=['POST'])
def reply():
    incoming_msg = request.form.get('Body', '').strip().lower()  # Get incoming message and clean it
    response = MessagingResponse()
    message = response.message()

    try:
        # Handle "start" or greeting commands
        if incoming_msg in ["start", "bonjour", "السلام عليكم"]:
            reply = "Bonjour! Veuillez entrer votre nom :"
            message.body(reply)
            return str(response)

        # Handle name input
        elif incoming_msg.isalpha():  # Check if input is a valid name (only letters)
            name = incoming_msg.capitalize()  # Capitalize the first letter
            save_reminder_date(name)  # Save the name to Google Sheets
            reply = f"Merci, {name}! Votre nom a été enregistré avec succès."
            message.body(reply)

        else:  # Handle invalid inputs
            reply = "Entrée non valide. Veuillez entrer un nom valide (seulement des lettres)."
            message.body(reply)

    except Exception as e:
        # Handle unexpected errors
        reply = "Une erreur s'est produite. Veuillez réessayer plus tard."
        message.body(reply)

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)

from mailjet_rest import Client
import os
import dotenv

dotenv.load_dotenv()

def send_thank_you_email_mailjet(to_email, candidate_name=None):
    api_key = os.environ.get("MAILJET_API_KEY")
    api_secret = os.environ.get("MAILJET_API_SECRET")
    if not api_key or not api_secret:
        return False
    name = candidate_name or "Candidate"
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "minatobots30@gmail.com",
                    "Name": "TalentScout"
                },
                "To": [
                    {
                        "Email": to_email,
                        "Name": name
                    }
                ],
                "Subject": "Thank you for your submission",
                "TextPart": f"Dear {name},\n\nThank you, your assignment/interview has been submitted. We appreciate your time!\n\nBest regards,\nTalentScout Team"
            }
        ]
    }
    try:
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        result = mailjet.send.create(data=data)
        return result.status_code == 200
    except Exception:
        return False

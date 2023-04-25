import os
import requests
from dotenv import load_dotenv
import jinja2

#Background worker will not run the flask app so we have to load_dotenv function to get the env variables.
load_dotenv()

domain = os.getenv("MAILGUN_DOMAIN_NAME")

#Rendering means
template_loader = jinja2.FileSystemLoader("templates")
template_env = jinja2.Environment(loader=template_loader)

def render_template(template_filename, **context):
    return template_env.get_template(template_filename).render(**context)

def send_email(to,subject,body,html):
    domain = os.getenv("MAILGUN_DOMAIN_NAME")
    print("In email")
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", os.getenv("MAILGUN_API_KEY")),
        data={"from": f"Sathyaseelan<mailgun@{domain}>",
        "to": [to],
		"subject": subject,
		"text": body,
        "html":html
        })

def send_user_registration_email(email,username):
    return send_email(
        email,
        "Succesfully signed up",
        f"Hi {username}! You have successfully signed for the Stores REST API",
        render_template("email/action.html",username=username)
        )
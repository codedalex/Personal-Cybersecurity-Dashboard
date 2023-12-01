
import os
import pandas as pd
from django.conf import settings
from twilio.rest import Client
import random, uuid, platform, psutil
import string
from django.core.cache import cache
from user_agents import parse
from geoip2.database import Reader
from decouple import config



def get_common_passwords():
    file_path = os.path.join(settings.BASE_DIR, 'passwords', 'common_passwords.xlsx')
    df = pd.read_excel(file_path)
    common_passwords = df['passwords'].tolist()
    return common_passwords

def get_special_characters(file_path='passwords/special_characters.txt'):
    file_path = os.path.join(settings.BASE_DIR, file_path)
    df = pd.read_csv(file_path, delimiter=',', header=None)
    special_chars = df.iloc[:, 0].str.split().to_list()
    return special_chars

def generate_and_store_verification_code(user_id):
    # Generate a random 6-digit verification code
    verification_code = ''.join(random.choices(string.digits, k=6))

    # Store the verification code securely, associating it with the user
    cache_key = f'verification_code_{user_id}'
    cache.set(cache_key, verification_code, timeout=300)  # Set a timeout, e.g., 5 minutes

    return verification_code

def send_sms_verification_code(phone_number, user_id):
    # Generate a verification code and store it securely
    verification_code = generate_and_store_verification_code(user_id)

    # Use Twilio or another SMS service to send the verification code to the user's phone
    twilio_account_sid = config('TWILIO_ACCOUNT_SID')
    twilio_auth_token = config('TWILIO_AUTH_TOKEN')
    twilio_phone_number = config('TWILIO_PHONE_NUMBER')

    # Initialize the Twilio Client object
    client = Client(twilio_account_sid, twilio_auth_token)

    # Send the verification code via SMS
    message = client.messages.create(
        body=f'Your verification code is: {verification_code}',
        from_=twilio_phone_number,
        to=phone_number
    )


def parse_user_agent(user_agent, component='device'):
    user_agent_obj = parse(user_agent)
    if component == 'device':
        return user_agent_obj.device.family
    elif component == 'os':
        return user_agent_obj.os.family
    elif component == 'browser':
        return user_agent_obj.browser.family
    return None

def get_screen_resolution(request):
    """Get screen resolution of current device."""
    try:
        screen_width = request.GET['width']
        screen_height = request.GET['height']
        return f"{screen_width}x{screen_height}"
    except (KeyError, TypeError):
        return 'Unknown'

def get_geolocation(ip_address):
     api_key = config('API_KEY')
     url = config('URL')
     full_url = f'{url}/{ip_address}?token={api_key}'

     try:
        response = requests.get(full_url)
        data = response.json()
        return {
            "country": data.get["country"],
            "city": data.get["city"],
            'latitude': data.get('loc').split(',')[0],
            'longitude': data.get('loc').split(',')[1]
        }

     except:
        return None

def generate_device_identifier(request):
        # Generate a unique device identifier using UUID
    uuid4 = str(uuid.uuid4())
    return uuid4 

def get_network_info(request):
    network_info = {}
    try:
        network_info['type'] = psutil.net_if_stats()[list(psutil.net_if_stats())[0]].family
        network_info['speed'] = psutil.net_if_stats()[liat(psutil.net_if_stats())[0]].speed
    except:
        network_info['type'] = 'unknown'
        network_info['speed'] = 'unknown'

    network_info['provider'] = get_network_provider()
    return network_info

def get_network_provider():
    if platform.system() == 'Windws':
        return 'Windows Network'
    elif platform.system() == 'Linux':
        return 'Linux Network'
    elif platform.system() == 'Darwin':
        return 'Mac Network'
    else:
        return 'Unknown Network Provider'


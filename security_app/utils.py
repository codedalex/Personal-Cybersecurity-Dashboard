
import os, pyautogui
import pandas as pd
from django.conf import settings
from twilio.rest import Client
import random, uuid, platform, psutil
import string, ipinfo
from django.core.cache import cache
from user_agents import parse
from geoip2.database import Reader
from decouple import config
from geopy.geocoders import Nominatim
from django.http import HttpRequest



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
    
    device_family = user_agent_obj.device.family
    os_family = user_agent_obj.os.family
    os_version = user_agent_obj.os.version_string
    browser_family = user_agent_obj.browser.family
    
    # Determine device type and OS based on user agent information
    if 'Mobile' in device_family:
        device_type = 'Mobile'
        if 'Android' in os_family:
            os_type = 'Android'
        elif 'iOS' in os_family:
            os_type = 'iOS'
        else:
            os_type = 'Unknown Mobile OS'
    elif 'Windows' in os_family:
        device_type = 'PC'
        os_type = 'Windows OS'
    elif 'Mac' in os_family:
        device_type = 'Mac'
        os_type = 'Mac OS'
    elif 'Linux' in os_family:
        device_type = 'PC'
        os_type = parse_linux_os(user_agent_obj.os.family)
    elif component == 'browser':
        return user_agent_obj.browser.family
    else:
        device_type = 'Unknown'
        os_type = 'Unknown'
    
    return {
        "device_type": device_type,
        "os_type": os_type,
        "os_version": os_version,
        "browser_family": browser_family, 
    }

def parse_linux_os(os_family):
    # Add more Linux OS types as needed
    if 'Fedora' in os_family:
        return 'Fedora'
    elif 'Ubuntu' in os_family:
        return 'Ubuntu'
    elif 'Kali' in os_family:
        return 'Kali Linux'
    # Add more conditions for other Linux OS types here
    else:
        return 'Linux (Unknown)'

def get_screen_resolution():
    """Get screen resolution of current device."""
    try:
        screen_width, screen_height = pyautogui.size()

        return f"{screen_width}x{screen_height}"

    except Exception as e:
        # Handle any exceptions that might occur (e.g., wxPython not available)
        print(f"Error getting screen resolution: {e}")
        return 'Unknown'

 
def get_geolocation(request):
    user_ip = get_client_ip(request)
    geolocator = Nominatim(user_agent="security_app")
    location = geolocator.geocode(user_ip)

    if location:
        return {
            "country": location.address.split(",")[-1].strip(),
            "city": location.address.split(",")[-2].strip(),
            'latitude': location.latitude,
            'longitude': location.longitude
        }
    else:
        return None

# Function to get client's IP address
def get_client_ip(request: HttpRequest) -> str:
    if not isinstance(request, HttpRequest):
        # Handle the case where request is not an instance of HttpRequest
        return 'unknown'

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Ensure that the retrieved IP address is valid
    try:
        ipaddress.IPv4Address(ip)
        return ip
    except ipaddress.AddressValueError:
        return 'unknown'
# def get_geolocation(ip_address):
#     access_token = config('API_KEY')
    
#     handler = ipinfo.getHandler(access_token)
#     details = handler.getDetails(ip_address)

#     return {
#         "country": details.country,
#         "city": details.city,
#         'latitude': details.latitude,
#         'longitude': details.longitude
#     }

#     # except:
#     #     return None

def generate_device_identifier(request):
        # Generate a unique device identifier using UUID
    uuid4 = str(uuid.uuid4())
    return uuid4 

def get_network_info(request):
    network_info = {}
    try:
        network_info['type'] = psutil.net_if_stats()[list(psutil.net_if_stats())[0]].family
        network_info['speed'] = psutil.net_if_stats()[list(psutil.net_if_stats())[0]].speed
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


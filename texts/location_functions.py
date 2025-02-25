from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import math

from texts.telegram_sensitive_info import TOKEN

TRINITY_LAT = 53.3438
TRINITY_LON = -6.2546
RADIUS_METERS = 400  


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi, delta_lambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in meters


async def start(update: Update, context):
    """Start command - Instructs user to send their location."""
    await update.message.reply_text("Send your live location to check if you are at Trinity College Dublin!")

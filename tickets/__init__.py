from JeremyAtCUHK.settings import TICKET_NUM
from django.core.cache import cache

cache.set('tickets', TICKET_NUM)
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/112.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
]

REFERERS_BASE = [
    "https://www.google.com/search?q=",
    "https://www.bing.com/search?q=",
    "https://duckduckgo.com/?q=",
    "https://www.youtube.com/results?search_query=",
]

ACCEPT_HEADERS = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "application/json, text/javascript, */*; q=0.01",
]

CACHE_CONTROLS = ["no-cache", "max-age=0", "no-store"]

SEC_FETCH_HEADERS = {
    "Sec-Fetch-Dest": ["document", "iframe", "image", "style", "script"],
    "Sec-Fetch-Mode": ["navigate", "no-cors", "cors", "same-origin"],
    "Sec-Fetch-Site": ["same-origin", "cross-site", "same-site", "none"],
    "Sec-Fetch-User": ["?1", "?0"]
}

def random_choice_from_list(lst):
    return random.choice(lst)

def random_string(length=8):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choices(chars, k=length))

def random_cookie():
    cookies = [
        f"sessionid={random_string(16)}",
        f"csrftoken={random_string(24)}",
        f"auth_token={random_string(32)}",
        f"__Secure-SSID={random_string(24)}",
        f"SID={random_string(20)}"
    ]
    return "; ".join(random.sample(cookies, k=random.randint(2, 4)))

def random_referer():
    base = random_choice_from_list(REFERERS_BASE)
    query = random_string(random.randint(5,12))
    return base + query

def generate_headers():
    headers = {
        "User-Agent": random_choice_from_list(USER_AGENTS),
        "Referer": random_referer(),
        "Origin": f"https://{random.choice(['example.com','test.com','mysite.net'])}",
        "Cookie": random_cookie(),
        "Accept": random_choice_from_list(ACCEPT_HEADERS),
        "Cache-Control": random_choice_from_list(CACHE_CONTROLS),
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": str(random.choice(["1", "0"])),
        "TE": "trailers",
        "X-Requested-With": "XMLHttpRequest" if random.random() < 0.3 else "",
        "X-Forwarded-For": f"{random.randint(1, 255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
    }

    for key, values in SEC_FETCH_HEADERS.items():
        headers[key] = random_choice_from_list(values)

    return {k: v for k, v in headers.items() if v}

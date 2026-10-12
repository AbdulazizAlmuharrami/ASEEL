import urllib.request
import urllib.parse
import http.cookiejar

base = "http://127.0.0.1:5000"


def get(url):
    with urllib.request.urlopen(url) as response:
        return response.status, response.read().decode("utf-8", "ignore")


status, html = get(base + "/")
print("HOME", status, "ASEEL" in html, "Authenticity" in html)

status, html = get(base + "/login")
print("LOGIN", status, "Admin Login" in html)

status, html = get(base + "/verify/ASEEL-ROYAL-OUD-001")
print("VERIFY", status, "AUTHENTIC PRODUCT" in html, "Royal Oud" in html)

status, html = get(base + "/verify/FAKE-999")
print("FAKE", status, "PRODUCT NOT VERIFIED" in html)

for _ in range(6):
    get(base + "/verify/ASEEL-AMBER-NIGHT-003")
status, html = get(base + "/verify/ASEEL-AMBER-NIGHT-003")
print("WARN", "AUTHENTICITY WARNING" in html)

cookies = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
data = urllib.parse.urlencode(
    {"email": "admin@aseel.ae", "password": "AseelAdmin2026!"}
).encode()
html = opener.open(urllib.request.Request(base + "/login", data=data)).read().decode(
    "utf-8", "ignore"
)
print("DASH", "Authentication dashboard" in html, "Royal Oud" in html)

html = opener.open(base + "/admin/products/1").read().decode("utf-8", "ignore")
print("DETAIL", "Smart QR Tag" in html, "SO-000001" in html)

form = {
    "perfume_name": "Test Rose",
    "brand_name": "ASEEL Demo",
    "batch_number": "BTEST1",
        "box_serial_number": "TEST-" + __import__("time").strftime("%Y%m%d%H%M%S"),
    "manufacturing_date": "2026-10-01",
    "authorized_seller": "ASEEL Lab",
    "place_of_sale": "Khalifa University",
    "status": "Genuine",
    "scan_threshold": "5",
    "notes": "Automated test",
}
response = opener.open(
    urllib.request.Request(
        base + "/admin/register", data=urllib.parse.urlencode(form).encode()
    )
)
html = response.read().decode("utf-8", "ignore")
print("REGISTER", response.geturl(), "Test Rose" in html, "Smart QR Tag" in html)

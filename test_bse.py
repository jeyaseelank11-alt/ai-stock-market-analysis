import urllib.request

url = "https://public.fyers.in/sym_details/BSE_CM.csv"

request = urllib.request.Request(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()

    print("BSE data connection successful")
    print("Downloaded bytes:", len(data))
    print(data[:1000].decode("utf-8", errors="replace"))

except Exception as error:
    print("BSE connection failed:", error)
    raise

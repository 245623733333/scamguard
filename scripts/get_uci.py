"""Download UCI SMS Spam Collection into data/SMSSpamCollection (needs internet ONCE, on your dev machine)."""
import io, os, urllib.request, zipfile
URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
os.makedirs("data", exist_ok=True)
z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(URL, timeout=60).read()))
open("data/SMSSpamCollection", "wb").write(z.read("SMSSpamCollection"))
print("saved data/SMSSpamCollection")

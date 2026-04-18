from PIL import Image

img = Image.open("ns/assets/nityanusanthanam-thenkalai-tamil-512x512.png")

img.resize((192, 192)).save("ns/assets/nityanusanthanam-thenkalai-tamil-192.png")
img.resize((512, 512)).save("ns/assets/nityanusanthanam-thenkalai-tamil-512.png")
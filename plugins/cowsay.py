from subprocess import Popen, PIPE
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import octeon
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
@plugin.command(command="/cowsay",
                description="Have you mooed today?",
                inline_supported=True,
                hidden=False)
def cowsay(_, update, user, args):
    args = " ".join(args)
    proc = Popen(['cowsay'], stdout=PIPE, stdin=PIPE)
    stdout = str(
        proc.communicate(input=bytes(args, 'utf-8'))[0], 'utf-8').split('\n')
    font = ImageFont.truetype("plugdata/cowsay.ttf", 12)
    width = []
    height_t = []
    height = 0
    for item in stdout:
        size = font.getsize(item)
        width.append(size[0])
        height_t.append(size[1])
    width = max(width) + 10
    for item in height_t:
        height = height + item
    height = height + 20
    size = width, height
    img = Image.new("RGB", size, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((5, 5), "\n".join(stdout), (0, 0, 0), font=font)
    draw = ImageDraw.Draw(img)
    photo = BytesIO()
    img.save(photo, 'PNG')
    photo.seek(0)
    return octeon.message(photo=photo)

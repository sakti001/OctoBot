import octeon
from collections import OrderedDict
import socket
PLUGINVERSION = 2
# Always name this variable as `plugin`
# If you dont, module loader will fail to load the plugin!
plugin = octeon.Plugin()
MESSAGE_TEMPLATE = """
<b>%(Name)s</b>
<b>Map</b>: <code>%(Map)s</code>
<b>Game folder</b>: <code>%(Folder)s</code>
<b>Game</b>: <i>%(Game)s</i>
<b>Players</b>: %(Players)s/%(Maximum Players)s
<b>Password</b>: %(Visibility)s
<b>VAC</b>: %(VAC)s
"""
def _a2s_info(ip, port):
    STRING = "STRING"
    BYTE = "BYTE"
    SHORT = "SHORT"
    UDP_IP = ip
    UDP_PORT = int(port)

    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.sendto(b'\xFF\xFF\xFF\xFFTSource Engine Query\x00', (UDP_IP, UDP_PORT))
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(4096)
        data = data.split(b'I\x11')[1]
        stuffnames = OrderedDict({
            "Name":STRING,
            "Map":STRING,
            "Folder":STRING,
            "Game":STRING,
            "ID":SHORT,
            "Players":BYTE,
            "Maximum Players":BYTE,
            "Bots":BYTE,
            "Server type":BYTE,
            "Environment":BYTE,
            "Visibility":BYTE,
            "VAC":BYTE,
        })
        info = OrderedDict({})
        for stuff in stuffnames:
            if stuffnames[stuff] == STRING:
                data = data.split(b"\x00")
                info[stuff] = str(data[0], "utf-8")
                data = b"\x00".join(data[1:])
            elif stuffnames[stuff] == SHORT:
                info[stuff] = str(bytearray(data[:1])[0])
                data = data[2:]
            elif stuffnames[stuff] == BYTE:
                info[stuff] = str(bytearray(data)[0])
                data = data[1:]
        info["VAC"] = "Yes" if info["VAC"] == "1" else "No"
        info["Visibility"] = "Yes" if info["Visibility"] == "1" else "No"
        return octeon.message(MESSAGE_TEMPLATE % info, parse_mode="HTML")
    except Exception:
        return octeon.message("Invalid server", failed=True)

@plugin.command(command="/source",
                description="Sends information about Source Engine server",
                inline_supported=True,
                hidden=False)
def source_engine(bot, update, user, args):
    if len(args) == 1:
        args[0] = args[0].split(":")
        return _a2s_info(args[0][0],args[0][1])
    else:
        return octeon.message(text="Not enough or too many arguments!", failed=True)

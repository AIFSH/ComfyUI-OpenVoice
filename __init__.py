import os,sys

now_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(now_dir)

WEB_DIRECTORY = "./web"
from .nodes import LoadAudio, PreViewAudio,OpenVoice,LoadSRT, OpenVoiceSRT

# Set the web directory, any .js file in that directory will be loaded by the frontend as a frontend extension
# WEB_DIRECTORY = "./somejs"

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "OpenVoice": OpenVoice,
    "LoadAudio": LoadAudio,
    "PreViewAudio": PreViewAudio,
    "LoadSRT": LoadSRT,
    "OpenVoiceSRT": OpenVoiceSRT
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenVoice": "OpenVoice Node",
    "LoadAudio": "AudioLoader",
    "PreViewAudio": "PreView Audio",
    "LoadSRT": "SRTLoader",
    "OpenVoiceSRT": "OpenVoice with SRT"
}
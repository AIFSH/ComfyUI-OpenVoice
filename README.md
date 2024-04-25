# ComfyUI-OpenVoice
a custom comfyui node for [OpenVoice](https://github.com/myshell-ai/OpenVoice.git) to voice cloning and tts


## how to use
Download the checkpoint from [here](https://myshell-public-repo-hosting.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip) and extract it to the `checkpoints_v2` folder.

```
git clone https://github.com/AIFSH/ComfyUI-OpenVoice.git
cd ComfyUI-OpenVoice
pip install -r requirements.txt
python -m unidic download
```
# Debuging
`libcudnn_cnn_infer.so.8` not find error need to debug
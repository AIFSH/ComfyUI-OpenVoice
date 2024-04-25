# ComfyUI-OpenVoice
a custom comfyui node for [OpenVoice](https://github.com/myshell-ai/OpenVoice.git) to voice cloning and tts
<div>
  <figure>
  <img alt='webpage' src="web.png?raw=true" width="600px"/>
  <figure>
</div>

## how to use

make sure `ffmpeg` is worked in your commandline
for Linux
```
apt update
apt install ffmpeg
```
for Windows,you can install `ffmpeg` by [WingetUI](https://github.com/marticliment/WingetUI) automatically


Download the checkpoint from [here](https://myshell-public-repo-hosting.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip) and extract it to the `checkpoints_v2` folder.

```
git clone https://github.com/AIFSH/ComfyUI-OpenVoice.git
cd ComfyUI-OpenVoice
pip install -r requirements.txt
python -m unidic download
```
`tts weights` will be downloaded from huggingface automatically! if you in china,make sure your internet attach the huggingface
or if you still struggle with huggingface, you may try follow [hf-mirror](https://hf-mirror.com/) to config your env.

## Tutorial
- [Demo](https://www.bilibili.com/video/BV1yC411G7NJ)


# Debuging
1.
```
Could not load library libcudnn_cnn_infer.so.8. Error: /usr/lib/x86_64-linux-gnu/libcudnn_cnn_infer.so.8: undefined symbol: _ZN11nvrtcHelper4loadEb, version libcudnn_ops_infer.so.8
Please make sure libcudnn_cnn_infer.so.8 is in your library path!
```

https://github.com/vladmandic/automatic/discussions/540

1. fix by
```
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/miniconda3/lib/python3.10/site-packages/torch/lib
```

2. issueを英語で書く必要はありません。

------------------- ERROR DETAILS ------------------------

arguments: 
[ifs] no such file or directory: /usr/local/miniconda3/lib/python3.10/site-packages/unidic/dicdir/mecabrc
----------------------------------------------------------

2. fix by
```
cp -r /usr/local/miniconda3/lib/python3.10/site-packages/unidic_lite/dicdir /usr/local/miniconda3/lib/python3.10/site-packages/unidic/
```


## WeChat Group && Donate
<div>
  <figure>
  <img alt='Wechat' src="wechat.jpg?raw=true" width="300px"/>
  <img alt='donate' src="donate.jpg?raw=true" width="300px"/>
  <figure>
</div>

## Thanks
- [OpenVoice](https://github.com/myshell-ai/OpenVoice.git)
- [MeloTTS](https://github.com/myshell-ai/MeloTTS.git)

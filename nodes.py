import os
import torch
import cuda_malloc
import time
import folder_paths
import audiotsm.io.wav
from pydub import AudioSegment
from srt import parse as SrtPare
from .melo.api import TTS
from .openvoice import se_extractor
from .openvoice.api import ToneColorConverter

now_dir = os.path.dirname(os.path.abspath(__file__))
device = "cuda" if cuda_malloc.cuda_malloc_supported() else "cpu"
out_path = folder_paths.get_output_directory()
input_path = folder_paths.get_input_directory()
language_list = ["en-au","en-br","en-default","en-india",
                 "en-newest","en-us","es","fr","jp","kr","zh"]
ckpt_converter = os.path.join(now_dir, 'checkpoints_v2','converter')

class OpenVoiceSRT:
    @classmethod
    def INPUT_TYPES(s):        
        return {"required":
                    {
                     "text_srt":("SRT",),
                     "reference_speaker":("AUDIO",),
                     "language":(language_list,{
                         "default": "zh"
                     })
                    }
                }
    CATEGORY = "AIFSH_OpenVoice"
    RETURN_TYPES = ('AUDIO',)
    OUTPUT_NODE = False

    FUNCTION = "get_tts_wav"

    def get_tts_wav(self,text_srt,reference_speaker,language):
        text_srt_path = folder_paths.get_annotated_filepath(text_srt)
        with open(text_srt_path, 'r', encoding="utf-8") as file:
            text_file_content = file.read()
        
        refer_wav_root = os.path.join(input_path, "openvoice_infer")
        os.makedirs(refer_wav_root,exist_ok=True)
        audio_path = folder_paths.get_annotated_filepath(reference_speaker)
        audio_seg = AudioSegment.from_file(audio_path)
        new_audio_seg = AudioSegment.silent(0)
        text_subtitles = list(SrtPare(text_file_content))
        
        tone_color_converter = ToneColorConverter(os.path.join(ckpt_converter,'config.json'), device=device)
        tone_color_converter.load_ckpt(os.path.join(ckpt_converter,'checkpoint.pth'))
        
        model = TTS(language=language, device=device)
        speaker_ids = model.hps.data.spk2id
        speaker_id = speaker_ids[language]
        source_se = torch.load(os.path.join(now_dir,'checkpoints_v2','base_speakers','ses','{speaker_key}.pth'), map_location=device)
        
        for i,text_sub in enumerate(text_subtitles):
            start_time = text_sub.start.total_seconds() * 1000
            end_time = text_sub.end.total_seconds() * 1000
            if i == 0:
                new_audio_seg += audio_seg[:start_time]
            refer_wav_seg = audio_seg[start_time:end_time]
            refer_wav = os.path.join(refer_wav_root, f"{i}_openvoice_refer.wav")
            refer_wav_seg.export(refer_wav, format='wav')

            outfile = os.path.join(refer_wav_root, f"{i}_openvoice_infer.wav")
            text = text_sub.file_content
            
            target_se, audio_name = se_extractor.get_se(refer_wav, tone_color_converter, vad=False)
            
            src_path = os.path.join(refer_wav_root, f"{i}_openvoice_v2_tmp.wav")
            
            model.tts_to_file(text, speaker_id, src_path, speed=1.0)
            # Run the tone color converter
            encode_message = "@AIFSH"
            tone_color_converter.convert(
                audio_src_path=src_path, 
                src_se=source_se, 
                tgt_se=target_se, 
                output_path=outfile,
                message=encode_message)
            
            
            text_audio = AudioSegment.from_file(outfile)
            text_audio_dur_time = text_audio.duration_seconds * 1000
            
            if i < len(text_subtitles) - 1:
                nxt_start = text_subtitles[i+1].start.total_seconds() * 1000
                dur_time =  nxt_start - start_time
            else:
                org_dur_time = audio_seg.duration_seconds * 1000
                dur_time = org_dur_time - start_time
            
            ratio = text_audio_dur_time / dur_time

            if text_audio_dur_time > dur_time:
                tmp_audio = self.map_vocal(audio=text_audio,ratio=ratio,dur_time=dur_time,
                                                wav_name=f"map_{i}_refer.wav",temp_folder=refer_wav_root)
                tmp_audio += AudioSegment.silent(dur_time - tmp_audio.duration_seconds*1000)
    
            else:
                tmp_audio = text_audio + AudioSegment.silent(dur_time - text_audio_dur_time)
          
            new_audio_seg += tmp_audio

        infer_audio = os.path.join(out_path, f"{time.time()}_openvoice_infer.wav")
        new_audio_seg.export(infer_audio, format="wav")
        
        return (infer_audio,)
    def map_vocal(self,audio:AudioSegment,ratio:float,dur_time:float,wav_name:str,temp_folder:str):
        tmp_path = f"{temp_folder}/map_{wav_name}"
        audio.export(tmp_path, format="wav")
        
        clone_path = f"{temp_folder}/cloned_{wav_name}"
        reader = audiotsm.io.wav.WavReader(tmp_path)
        
        writer = audiotsm.io.wav.WavWriter(clone_path,channels=reader.channels,
                                        samplerate=reader.samplerate)
        wsloa = audiotsm.wsola(channels=reader.channels,speed=ratio)
        wsloa.run(reader=reader,writer=writer)
        audio_extended = AudioSegment.from_file(clone_path)
        return audio_extended[:dur_time]
    

class OpenVoice:
    def __init__(self) -> None:
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {"required":{
            "reference_speaker": ("AUDIO",),
            "text":("STRING",{
                "multiline": True,
                "default": "你好，世界！"
            }),
            "language":(language_list,{
                "default": "zh"
            }),
            "speed":("FLOAT",{
                "default": 1.0,
                "min": 0.5,
                "max": 2.0,
                "step": 0.5,
                "display": "slider"
            })
        }}
    
    CATEGORY = "AIFSH_OpenVoice"
    RETURN_TYPES = ('AUDIO',)
    OUTPUT_NODE = False

    FUNCTION = "get_tts_wav"
    
    def get_tts_wav(self,reference_speaker,text,language,speed=1.0):
        
        tone_color_converter = ToneColorConverter(os.path.join(ckpt_converter,'config.json'), device=device)
        tone_color_converter.load_ckpt(os.path.join(ckpt_converter,'checkpoint.pth'))
        
        target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, vad=False)
        
        src_path = os.path.join(out_path, "openvoice_v2_tmp.wav")
        model = TTS(language=language, device=device)
        speaker_ids = model.hps.data.spk2id
        speaker_id = speaker_ids[language]
        source_se = torch.load(os.path.join(now_dir,'checkpoints_v2','base_speakers','ses','{speaker_key}.pth'), map_location=device)
        model.tts_to_file(text, speaker_id, src_path, speed=speed)
        save_path = os.path.join(out_path,f"openvoice_v2_{language}.wav")
        # Run the tone color converter
        encode_message = "@AIFSH"
        tone_color_converter.convert(
            audio_src_path=src_path, 
            src_se=source_se, 
            tgt_se=target_se, 
            output_path=save_path,
            message=encode_message)
        
        os.remove(src_path)
        del tone_color_converter,source_se,target_se,model
        import gc;gc.collect();torch.cuda.empty_cache()
        return (save_path,)
    
class PreViewAudio:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"audio": ("AUDIO",),}
                }

    CATEGORY = "AIFSH_OpenVoice"
    DESCRIPTION = "hello world!"

    RETURN_TYPES = ()

    OUTPUT_NODE = True

    FUNCTION = "load_audio"

    def load_audio(self, audio):
        audio_name = os.path.basename(audio)
        tmp_path = os.path.dirname(audio)
        audio_root = os.path.basename(tmp_path)
        return {"ui": {"audio":[audio_name,audio_root]}}

class LoadAudio:
    @classmethod
    def INPUT_TYPES(s):
        files = [f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f)) and f.split('.')[-1] in ["wav", "mp3","WAV","flac","m4a"]]
        return {"required":
                    {"audio": (sorted(files),)},
                }

    CATEGORY = "AIFSH_OpenVoice"

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "load_audio"

    def load_audio(self, audio):
        audio_path = folder_paths.get_annotated_filepath(audio)
        return (audio_path,)

class LoadSRT:
    @classmethod
    def INPUT_TYPES(s):
        files = [f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f)) and f.split('.')[-1] in ["srt", "txt"]]
        return {"required":
                    {"srt": (sorted(files),)},
                }

    CATEGORY = "AIFSH_OpenVoice"

    RETURN_TYPES = ("SRT",)
    FUNCTION = "load_srt"

    def load_srt(self, srt):
        srt_path = folder_paths.get_annotated_filepath(srt)
        return (srt_path,)
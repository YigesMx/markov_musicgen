# 初始化与前端启动
import asyncio

import gradio as gr
import os
import gen
import os
import time
import numpy as np
import pickle

from classes.song import Song
from utils.tools import chord_level, chord_seq, level_name, dig_level, to_note_num, to_note_high
import utils
from midi2audio import FluidSynth

if __name__ == "__main__":
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=1, min_width=600):
                type_radio = gr.Radio(['普通版', '专业版'], label="版本")
                type_button = gr.Button("确认切换")
        with gr.Row():
            with gr.Column(scale=1, min_width=600):
                style_radio = gr.Radio(['欢快', '思念', '悲伤', '随机'], label="风格")
                speed_slider = gr.Slider(minimum=60, maximum=200, label="速度")
                time_slider = gr.Slider(minimum=20.0, maximum=25.0, step=0.1, label="时长")
            with gr.Column(scale=1, min_width=600):
                hexian_text = gr.Textbox(label="和弦序列", visible=False)
                yinfu_text = gr.Textbox(label="音符修改", visible=False)
                chushi_text = gr.Textbox(label="初始输入", visible=False)
                text = gr.Textbox(label="说明", visible=True, interactive=False, value="解锁专业版获取更多功能！")
        with gr.Row():
            gen_button = gr.Button("生成音乐")
            music = gr.Audio()


        async def play_audio(style_radio, speed_slider, time_slider):
            chord = ['C', 'Am', 'F', 'G', 'C', 'Am', 'F', 'G']
            # chord = ['C', 'C', 'Am', 'Am', 'F', 'F', 'G', 'G']
            # chord = ['C', 'C', 'Am', 'Am']
            r1 = [
                ['chord', 'loc', 'pre_none_n1'],
            ]
            r2 = [
                ['chord', 'loc', 'pre_none_n1'],
                ['chord', 'pre', 'next']
            ]

            chord_list = ['C', 'Am', 'F', 'G', 'C', 'Am', 'F', 'G']
            print('begin\n')
            song = gen.musicgen(chord_list=chord, rule=r1, name="test", bpm=80, unit_len=1 / 16, units_per_bar=16,
                                prob_scale=1.0, policy_mode='normal')
            print('end gen\n')
            song.play()
            FluidSynth(sound_font="TimGM6mb.sf2").midi_to_audio('temp.mid', 'output.wav')
            print('end wav\n')
            wav_file_path = 'output.wav'
            return gr.Audio(wav_file_path)


        def type_check(type_radio):
            if type_radio == '专业版':
                return gr.update(visible=True, interactive=True), gr.update(visible=True, interactive=True), gr.update(visible=True, interactive=True), gr.update(visible=False)
            else:
                return gr.update(visible=False, interactive=False), gr.update(visible=False, interactive=False), gr.update(visible=False, interactive=False), gr.update(visible=True)


        type_button.click(type_check, type_radio, outputs=[hexian_text, yinfu_text, chushi_text, text])
        gen_button.click(play_audio, [style_radio, speed_slider, time_slider], outputs=music)
    demo.launch(share=True)
    # gr.Interface(play_audio, [style_radio, speed_slider, time_slider], outputs="audio").launch(share=True)

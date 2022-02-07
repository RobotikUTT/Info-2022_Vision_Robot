from threading import Thread, Event
from flask import Flask, Response
from waitress import serve
from Common.frame_supplier import FrameSupplier
import simplejpeg
import cv2
from dataclasses import dataclass
from typing import Tuple
import numpy as np


@dataclass
class StreamConfiguration:
    frame_supplier: FrameSupplier
    resize: Tuple[int, int] | None = None
    crop: Tuple[int, int, int, int] | None = None
    quality: int = 85


class WebInterfaceThread(Thread):
    def __init__(self, daemon=True):
        Thread.__init__(self, daemon=daemon)
        self.app = Flask(__name__)

    def run(self):
        serve(self.app, host="0.0.0.0", port=5000)

    def create_video_stream(self, url, stream_configuration: StreamConfiguration):
        self.app.add_url_rule(
            url,
            view_func=lambda: self._video_feed(stream_configuration),
            endpoint=url,
        )

    def _video_feed(self, stream_configuration: StreamConfiguration):
        return Response(
            self._gen_frames_data(stream_configuration),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    @staticmethod
    def _adjust_frame(frame, resize, crop):
        if crop:
            width, height = crop
            half_width = width // 2
            half_height = height // 2

            center = (frame.shape[1] // 2, frame.shape[0] // 2)
            frame = frame[
                center[1] - half_height: center[1] + half_height,
                center[0] - half_width: center[0] + half_width
                ]
            frame = np.ascontiguousarray(frame)

        if resize:
            frame = cv2.resize(frame, resize, interpolation=cv2.INTER_NEAREST)

        return frame

    @staticmethod
    def _get_frame_data(frame, quality):
        return simplejpeg.encode_jpeg(frame, colorspace="BGR", quality=quality)

    def _gen_frames_data(self, stream_configuration: StreamConfiguration):
        frame_supplier = stream_configuration.frame_supplier
        quality = stream_configuration.quality
        resize = stream_configuration.resize
        crop = stream_configuration.crop

        wait_for_frame = Event()
        frame_supplier.subscribe(lambda: wait_for_frame.set())

        while True:
            wait_for_frame.wait()
            wait_for_frame.clear()
            frame = frame_supplier.get_frame()

            new_frame = WebInterfaceThread._adjust_frame(frame, resize, crop)
            frame_data = WebInterfaceThread._get_frame_data(new_frame, quality)

            yield ( 
                b"--frame\r\n" 
                b"Content-Type: image/jpeg\r\n"
                b"\r\n" + 
                frame_data + 
                b"\r\n" 
            )
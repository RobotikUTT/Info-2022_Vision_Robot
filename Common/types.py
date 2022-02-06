"""This file contains basic types.
"""
from dataclasses import dataclass
from typing import List, NewType
import numpy as np
from Common.aruco import ArucoCode

Frame = NewType('Frame', np.ndarray)

@dataclass
class FrameArucoCodes:
    frame: Frame
    codes: List[ArucoCode]

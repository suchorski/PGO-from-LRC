import re
from dataclasses import dataclass

@dataclass
class LrcLine:
    time: float  # Tempo em segundos
    text: str

def parse_lrc_file(file_path):
    lrc_lines = []
    pattern = r"\[(\d+):(\d+)\.(\d+)\](.*)"  # Regex para capturar [mm:ss.cc] e texto

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(pattern, line.strip())
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                centiseconds = int(match.group(3))
                text = match.group(4).strip()

                # Converter para tempo em segundos
                time_in_seconds = minutes * 60 + seconds + centiseconds / 100
                lrc_lines.append(LrcLine(time=time_in_seconds, text=text))

    return lrc_lines

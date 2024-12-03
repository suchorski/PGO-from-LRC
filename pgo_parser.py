from dataclasses import dataclass, field
from typing import List

@dataclass
class Phoneme:
    frame: int
    phoneme: str

@dataclass
class Word:
    word: str
    start_frame: int
    end_frame: int
    phonemes: List[Phoneme] = field(default_factory=list)

@dataclass
class Segment:
    text: str
    start_frame: int
    end_frame: int
    words: List[Word] = field(default_factory=list)

@dataclass
class Voice:
    name: str
    full_text: str
    segments: List[Segment] = field(default_factory=list)

@dataclass
class PgoFile:
    version: str = ""
    audio_file: str = ""
    fps: int = 0
    frame_count: int = 0
    voices: List[Voice] = field(default_factory=list)


def parse_pgo_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    pgo_file = PgoFile()
    index = 0

    # Cabeçalho
    pgo_file.version = lines[index].strip()
    index += 1
    pgo_file.audio_file = lines[index].strip()
    index += 1
    pgo_file.fps = int(lines[index].strip())
    index += 1
    pgo_file.frame_count = int(lines[index].strip())
    index += 1

    # Voicelines
    voice_count = int(lines[index].strip())
    index += 1
    for _ in range(voice_count):
        voice = Voice(name=lines[index].strip(), full_text=lines[index + 1].strip())
        index += 2

        segment_count = int(lines[index].strip())
        index += 1
        for _ in range(segment_count):
            segment = Segment(
                text=lines[index].strip(),
                start_frame=int(lines[index + 1].strip()),
                end_frame=int(lines[index + 2].strip())
            )
            index += 3
            word_count = int(lines[index].strip())
            index += 1

            for _ in range(word_count):
                word_data = lines[index].strip().split()
                word = Word(
                    word=word_data[0],
                    start_frame=int(word_data[1]),
                    end_frame=int(word_data[2])
                )
                phoneme_count = int(word_data[3])
                index += 1

                for _ in range(phoneme_count):
                    phoneme_data = lines[index].strip().split()
                    phoneme = Phoneme(frame=int(phoneme_data[0]), phoneme=phoneme_data[1])
                    word.phonemes.append(phoneme)
                    index += 1

                segment.words.append(word)

            voice.segments.append(segment)

        pgo_file.voices.append(voice)

    return pgo_file

def save_pgo_file(file_path, pgo_content):
    with open(file_path, 'w', encoding='utf-8') as file:
        # Cabeçalho
        file.write(f"{pgo_content.version}\n")
        file.write(f"{pgo_content.audio_file}\n")
        file.write(f"{pgo_content.fps}\n")
        file.write(f"{pgo_content.frame_count}\n")
        file.write(f"{len(pgo_content.voices)}\n")

        for voice in pgo_content.voices:
            # Vozes
            file.write(f"\t{voice.name}\n")
            file.write(f"\t{voice.full_text}\n")
            file.write(f"\t{len(voice.segments)}\n")

            for segment in voice.segments:
                # Segmentos
                file.write(f"\t\t{segment.text}\n")
                file.write(f"\t\t{segment.start_frame}\n")
                file.write(f"\t\t{segment.end_frame}\n")
                file.write(f"\t\t{len(segment.words)}\n")

                for word in segment.words:
                    # Palavras
                    file.write(f"\t\t\t{word.word} {word.start_frame} {word.end_frame} {len(word.phonemes)}\n")

                    for phoneme in word.phonemes:
                        # Fonemas
                        file.write(f"\t\t\t\t{phoneme.frame} {phoneme.phoneme}\n")

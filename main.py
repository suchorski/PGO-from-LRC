import argparse
from pgo_parser import parse_pgo_file, save_pgo_file, Word
from lrc_parser import parse_lrc_file

def adjust_phonemes_in_word(word):
    """
    Ajusta os fonemas existentes em uma palavra para serem distribuídos uniformemente
    entre start_frame e end_frame.

    :param word: Um objeto Word cuja lista de fonemas será ajustada.
    """
    total_frames = word.end_frame - word.start_frame + 1  # Inclui o frame final
    num_phonemes = len(word.phonemes)

    if num_phonemes == 0:
        return  # Sem fonemas para ajustar

    frames_per_phoneme = total_frames // num_phonemes
    remaining_frames = total_frames % num_phonemes  # Frames extras para distribuir
    start_frame = word.start_frame

    for i, phoneme in enumerate(word.phonemes):
        # Distribuir frames extras uniformemente
        extra_frame = 1 if i < remaining_frames else 0
        phoneme.frame = start_frame + i * (frames_per_phoneme + extra_frame)

def adjust_phonemes_in_segment(segment):
    """
    Ajusta os fonemas de cada palavra no segmento.
    """
    for word in segment.words:
        adjust_phonemes_in_word(word)

def adjust_words_in_segment(segment):
    """Ajusta os start_frame e end_frame das palavras existentes no segmento sem sobreposição."""
    num_words = len(segment.words)
    if num_words == 0:
        return  # Se não há palavras, não há nada para ajustar

    total_frames = segment.end_frame - segment.start_frame
    frames_per_word = total_frames // num_words
    remaining_frames = total_frames % num_words  # Para lidar com divisão que não é exata
    start_frame = segment.start_frame

    for i, word in enumerate(segment.words):
        # Distribuir frames extras uniformemente
        extra_frame = 1 if i < remaining_frames else 0
        end_frame = start_frame + frames_per_word + extra_frame

        word.start_frame = start_frame
        word.end_frame = end_frame - 1  # End frame é inclusivo, então ajustamos para evitar sobreposição
        start_frame = end_frame

def update_segments_with_lrc(pgo_content, lrc_lines, fps):
    for voice in pgo_content.voices:
        for segment in voice.segments:
            # Procurar o texto no LRC
            matching_lines = [line for line in lrc_lines if line.text == segment.text]
            if not matching_lines:
                print(f"Texto não encontrado no LRC: {segment.text}")
                continue

            # Atualizar start_frame e end_frame
            lrc_index = lrc_lines.index(matching_lines[0])
            segment.start_frame = int(lrc_lines[lrc_index].time * fps)
            if lrc_index + 1 < len(lrc_lines):
                segment.end_frame = int(lrc_lines[lrc_index + 1].time * fps)
            else:
                segment.end_frame = segment.start_frame + fps  # Definir um intervalo padrão se for o último

            # Ajustar os frames das palavras
            adjust_words_in_segment(segment)

            # Ajustar os fonemas das palavras
            adjust_phonemes_in_segment(segment)

    return pgo_content

def main():
    parser = argparse.ArgumentParser(description="Read and update PGO with LRC data.")
    parser.add_argument("pgo_file", type=str, help="Path to the PGO file")
    parser.add_argument("lrc_file", type=str, help="Path to the LRC file")
    parser.add_argument("output_pgo", type=str, help="Path to save the updated PGO file")

    args = parser.parse_args()

    # Lendo os arquivos
    pgo_content = parse_pgo_file(args.pgo_file)
    lrc_lines = parse_lrc_file(args.lrc_file)

    # Atualizar os segmentos no PGO com base no LRC
    updated_pgo_content = update_segments_with_lrc(pgo_content, lrc_lines, pgo_content.fps)

    # Salvar o PGO atualizado
    save_pgo_file(args.output_pgo, updated_pgo_content)
    print(f"PGO file updated and saved to '{args.output_pgo}'.")

if __name__ == "__main__":
    main()

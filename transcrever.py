"""Transcreve os arquivos de áudio de uma pasta para arquivos TXT."""

import argparse
from pathlib import Path
import sys


EXTENSOES = {".mp3", ".wav", ".m4a", ".ogg", ".opus", ".flac", ".aac", ".wma", ".aiff", ".aif", ".webm"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pasta", type=Path, help="Pasta com os arquivos de áudio")
    parser.add_argument("--saida", type=Path, help="Pasta dos textos (padrão: PASTA/textos)")
    parser.add_argument("--modelo", default="small", help="Modelo Whisper (padrão: small; use base para maior velocidade)")
    parser.add_argument("--idioma", default=None, help="Código do idioma, como pt ou en (padrão: automático)")
    parser.add_argument("--recursivo", action="store_true", help="Incluir subpastas")
    parser.add_argument("--sobrescrever", action="store_true", help="Substituir textos existentes")
    args = parser.parse_args()

    pasta = args.pasta.expanduser().resolve()
    if not pasta.is_dir():
        parser.error(f"Pasta não encontrada: {pasta}")
    saida = (args.saida.expanduser().resolve() if args.saida else pasta / "textos")
    arquivos = sorted(
        p for p in (pasta.rglob("*") if args.recursivo else pasta.iterdir())
        if p.is_file() and p.suffix.lower() in EXTENSOES
    )
    if not arquivos:
        print(f"Nenhum áudio encontrado em: {pasta}")
        return 0

    pendentes = []
    for arquivo in arquivos:
        # Manter a extensão original evita colisões entre gravação.mp3 e gravação.wav.
        destino = saida / arquivo.relative_to(pasta).parent / (arquivo.name + ".txt")
        if destino.exists() and not args.sobrescrever:
            print(f"Já existe, ignorando: {destino}")
        else:
            pendentes.append((arquivo, destino))
    if not pendentes:
        print("Todos os áudios já possuem textos. Use --sobrescrever para refazer.")
        return 0

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Instale as dependências: python -m pip install -r requirements.txt", file=sys.stderr)
        return 1

    print(f"Carregando modelo {args.modelo} (o primeiro uso pode baixar o modelo)...", flush=True)
    try:
        modelo = WhisperModel(args.modelo, device="cpu", compute_type="int8")
    except Exception as erro:
        print(f"Não foi possível carregar o modelo: {erro}", file=sys.stderr)
        return 1

    falhas = 0
    for indice, (arquivo, destino) in enumerate(pendentes, start=1):
        print(f"[{indice}/{len(pendentes)}] Transcrevendo: {arquivo.name}", flush=True)
        temporario = None
        try:
            segmentos, info = modelo.transcribe(
                str(arquivo), language=args.idioma, task="transcribe", beam_size=5,
            )
            # Consumir o gerador é necessário para realizar a transcrição.
            texto = "\n".join(s.text.strip() for s in segmentos if s.text.strip())
            destino.parent.mkdir(parents=True, exist_ok=True)
            # Só substituir o arquivo final depois de uma transcrição bem-sucedida.
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destino.parent,
                                             suffix=".tmp", delete=False) as f:
                temporario = Path(f.name)
                f.write(texto + "\n" if texto else "")
            temporario.replace(destino)
            print(f"Salvo: {destino} (idioma: {info.language})")
        except Exception as erro:
            falhas += 1
            print(f"Erro em {arquivo.name}: {erro}", file=sys.stderr)
        finally:
            if temporario is not None:
                temporario.unlink(missing_ok=True)

    print(f"Concluído: {len(pendentes) - falhas} transcritos, {falhas} com erro.")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())

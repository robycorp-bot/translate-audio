# Áudios para texto

Transcreve os áudios de uma pasta usando [faster-whisper](https://github.com/SYSTRAN/faster-whisper), executado localmente na CPU. Não exige chave de API. Na primeira execução, o modelo é baixado pela internet; depois fica em cache. A fala é transcrita no idioma original.

## Instalação

Use Python 3.11 ou 3.12 para facilitar a compatibilidade das dependências. No PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Uso

Coloque seus áudios em uma pasta chamada `audios` e execute:

```powershell
.\.venv\Scripts\python.exe transcrever.py .\audios
```

Para usar outra pasta, especificar português e incluir subpastas:

```powershell
.\.venv\Scripts\python.exe transcrever.py "C:\Meus Audios" --saida .\textos --idioma pt --recursivo
```

Cada áudio gera um TXT em UTF-8: `audios/entrevista.mp3` vira `audios/textos/entrevista.mp3.txt`. A estrutura de subpastas é preservada. Textos existentes são ignorados; use `--sobrescrever` para refazê-los.

Formatos reconhecidos: MP3, WAV, M4A, OGG, OPUS, FLAC, AAC, WMA, AIFF, AIF e WEBM. Arquivos corrompidos ou com codecs não suportados são reportados e o processamento continua nos demais.

O modelo padrão é `small`. Use `--modelo base` para maior velocidade ou `--modelo medium` para um modelo maior, que exige mais memória e tempo. A precisão depende da qualidade do áudio. Execute `transcrever.py --help` para ver as opções.

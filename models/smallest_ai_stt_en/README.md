# Smallest AI — Pulse STT (English)

**Entity**: Smallest AI  
**Model**: Pulse (current STT)  
**Language**: English  
**API Docs**: https://docs.smallest.ai  

## Overview

[Pulse](https://smallest.ai) is Smallest AI's speech-to-text model. It supports 38 languages, word-level timestamps, speaker diarization, and emotion detection. This leaderboard submission evaluates its English transcription accuracy using the batch HTTP API.

## Setup

Place your Smallest AI API key in `assets/API_KEY`:

```
echo "your_api_key" > assets/API_KEY
```

## Running

```bash
./SBI /path/to/wav.scp /path/to/result_dir
```

Transcriptions are written to `result_dir/raw_rec.txt`.

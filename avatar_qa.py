"""Offline voiceover acceptance gate. Python standard library only."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys
import wave


class ValidationError(ValueError):
    pass


def timestamp(text):
    match = re.fullmatch(r'(\d{2,}):([0-5]\d):([0-5]\d),(\d{3})', text)
    if not match:
        raise ValidationError('SRT 时间必须为 HH:MM:SS,mmm')
    h, m, s, ms = map(int, match.groups())
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def parse_srt(text):
    text = text.lstrip('\ufeff').replace('\r\n', '\n').strip()
    if not text:
        raise ValidationError('字幕为空')
    cues = []
    for index, block in enumerate(re.split(r'\n\s*\n', text), 1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0].strip() != str(index):
            raise ValidationError('字幕序号必须从 1 连续递增，并包含时间和正文')
        times = lines[1].split(' --> ')
        if len(times) != 2:
            raise ValidationError('无效字幕时间行')
        start, end = map(timestamp, times)
        body = '\n'.join(lines[2:]).strip()
        if end <= start or not body:
            raise ValidationError('字幕时长必须大于零且正文非空')
        if cues and start < cues[-1]['end_ms']:
            raise ValidationError('字幕重叠或时间倒序')
        cues.append({'start_ms': start, 'end_ms': end, 'text': body})
    return cues


def normalize(text):
    # Keep punctuation and digits: a changed price or claim must not disappear.
    return re.sub(r'\s+', '', text)


def inspect_wav(path):
    with wave.open(str(path), 'rb') as source:
        channels, width, rate, frames, codec, _ = source.getparams()
        if channels != 1 or width != 2 or codec != 'NONE' or rate != 16000:
            raise ValidationError('验收输入要求 16kHz / mono / PCM16 WAV；请先转换')
        if frames <= 0 or frames > rate * 600:
            raise ValidationError('音频时长必须大于 0 且不超过 600 秒')
        raw = source.readframes(frames)
        if len(raw) != frames * 2:
            raise ValidationError('WAV 帧数与实际数据不一致，可能被截断')
    count, squared, peak, clipped = 0, 0, 0, 0
    for (value,) in struct.iter_unpack('<h', raw):
        count += 1
        squared += value * value
        peak = max(peak, abs(value))
        clipped += abs(value) >= 32760
    rms = math.sqrt(squared / count)
    return {'duration_ms': frames * 1000 / rate, 'sample_rate': rate,
            'channels': channels, 'peak': peak,
            'rms_dbfs': round(20 * math.log10(rms / 32768), 2) if rms else None,
            'clipped_ratio': clipped / count}


def validate_bundle(audio, subtitles, script):
    audio, subtitles, script = map(Path, (audio, subtitles, script))
    stats = inspect_wav(audio)
    cues = parse_srt(subtitles.read_text(encoding='utf-8-sig'))
    words = script.read_text(encoding='utf-8-sig').strip()
    issues = []
    if not words or normalize(words) != normalize(''.join(c['text'] for c in cues)):
        issues.append('script_subtitle_mismatch')
    if cues[-1]['end_ms'] > stats['duration_ms']:
        issues.append('subtitle_exceeds_audio')
    if stats['rms_dbfs'] is None or stats['rms_dbfs'] < -50:
        issues.append('silent_or_too_quiet')
    if stats['clipped_ratio'] > 0.001:
        issues.append('audio_clipping')
    return {'schema_version': 1, 'status': 'FAIL' if issues else 'PASS',
            'scope': 'offline_asset_checks_only', 'issues': issues,
            'audio': stats, 'cue_count': len(cues),
            'thresholds': {'min_rms_dbfs': -50, 'max_clipped_ratio': 0.001},
            'sha256': {key: hashlib.sha256(path.read_bytes()).hexdigest()
                       for key, path in [('audio', audio), ('subtitles', subtitles), ('script', script)]},
            'not_measured': ['speech_transcription', 'lip_sync', 'speaker_identity',
                             'render_fps', 'end_to_end_latency', 'LiveTalking_server']}


def livetalking_request(text, session_id, interrupt=False):
    """Export a /human request, without transmitting or claiming server success."""
    if not isinstance(text, str) or not text.strip() or len(text) > 5000:
        raise ValidationError('口播文本须为 1–5000 个字符')
    if not isinstance(session_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', session_id):
        raise ValidationError('必须填写已建立的 LiveTalking 会话 ID')
    if not isinstance(interrupt, bool):
        raise ValidationError('interrupt 必须为布尔值')
    return {'sessionid': session_id, 'type': 'echo', 'text': text.strip(), 'interrupt': interrupt}


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def demo(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    audio, srt, script = [folder / x for x in ('synthetic-tone.wav', 'captions.srt', 'script.txt')]
    with wave.open(str(audio), 'wb') as target:
        target.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
        target.writeframes(b''.join(struct.pack('<h', int(6000 * math.sin(2 * math.pi * 220 * i / 16000)))
                                   for i in range(48000)))
    text = '这是合成验收样例，不是真人口播。'
    script.write_text(text, encoding='utf-8')
    srt.write_text('1\n00:00:00,000 --> 00:00:02,900\n' + text + '\n', encoding='utf-8')
    good = validate_bundle(audio, srt, script)
    write_json(folder / 'pass-report.json', good)
    srt.write_text('1\n00:00:00,000 --> 00:00:04,000\n' + text + '\n', encoding='utf-8')
    bad = validate_bundle(audio, srt, script)
    write_json(folder / 'fail-report.json', bad)
    # Retain valid captions in the delivered demo bundle.
    srt.write_text('1\n00:00:00,000 --> 00:00:02,900\n' + text + '\n', encoding='utf-8')
    write_json(folder / 'human-request.json', livetalking_request(text, 'DEMO_NOT_A_LIVE_SESSION'))
    return {'fixture': 'synthetic_tone_not_speech', 'valid_case': good['status'],
            'overflow_case': bad['status'], 'detected': bad['issues'], 'rendering': 'NOT_RUN'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    run = commands.add_parser('demo')
    run.add_argument('--out', default='runs/avatar-demo')
    check = commands.add_parser('check')
    for name in ('audio', 'srt', 'script', 'out'):
        check.add_argument('--' + name, required=True)
    request = commands.add_parser('request')
    request.add_argument('--script', required=True)
    request.add_argument('--session-id', required=True)
    request.add_argument('--interrupt', action='store_true')
    request.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo(args.out)
        elif args.command == 'check':
            result = validate_bundle(args.audio, args.srt, args.script)
            write_json(args.out, result)
        else:
            result = livetalking_request(Path(args.script).read_text(encoding='utf-8-sig'),
                                        args.session_id, args.interrupt)
            write_json(args.out, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get('status') == 'FAIL' else 0
    except (OSError, ValueError, wave.Error, EOFError) as error:
        print(json.dumps({'status': 'ERROR', 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())

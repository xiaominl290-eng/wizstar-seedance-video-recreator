import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from avatar_qa import demo, inspect_wav, livetalking_request, parse_srt, validate_bundle, ValidationError


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        demo(self.root)

    def check_bundle(self):
        return validate_bundle(self.root/'synthetic-tone.wav', self.root/'captions.srt', self.root/'script.txt')

    def test_demo_success_and_failure(self):
        self.assertEqual(self.check_bundle()['status'], 'PASS')
        self.assertEqual(json.loads((self.root/'fail-report.json').read_text())['issues'], ['subtitle_exceeds_audio'])

    def test_changed_price_not_hidden(self):
        (self.root/'script.txt').write_text('价格 199 元', encoding='utf-8')
        (self.root/'captions.srt').write_text('1\n00:00:00,000 --> 00:00:02,000\n价格 99 元', encoding='utf-8')
        self.assertIn('script_subtitle_mismatch', self.check_bundle()['issues'])

    def test_empty_subtitles(self):
        with self.assertRaises(ValidationError): parse_srt('')

    def test_overlap(self):
        with self.assertRaises(ValidationError):
            parse_srt('1\n00:00:00,000 --> 00:00:02,000\n甲\n\n2\n00:00:01,000 --> 00:00:03,000\n乙')

    def test_invalid_timestamp(self):
        with self.assertRaises(ValidationError): parse_srt('1\n00:60:00,000 --> 00:61:00,000\n甲')

    def test_reverse_interval(self):
        with self.assertRaises(ValidationError): parse_srt('1\n00:00:02,000 --> 00:00:01,000\n甲')

    def test_bom_crlf_multiline(self):
        self.assertEqual(parse_srt('\ufeff1\r\n00:00:00,000 --> 00:00:02,000\r\n甲\r\n乙')[0]['text'], '甲\n乙')

    def audio(self, value, channels=1):
        with wave.open(str(self.root/'synthetic-tone.wav'), 'wb') as wav:
            wav.setparams((channels, 2, 16000, 0, 'NONE', 'not compressed'))
            wav.writeframes(struct.pack('<h', value)*48000*channels)

    def test_silence(self):
        self.audio(0)
        self.assertIn('silent_or_too_quiet', self.check_bundle()['issues'])

    def test_clipping(self):
        self.audio(32767)
        self.assertIn('audio_clipping', self.check_bundle()['issues'])

    def test_wrong_channels(self):
        self.audio(1000, channels=2)
        with self.assertRaises(ValidationError): self.check_bundle()

    def test_truncated_wav(self):
        audio = self.root/'synthetic-tone.wav'
        audio.write_bytes(audio.read_bytes()[:-100])
        with self.assertRaises(ValidationError): inspect_wav(audio)

    def test_request_preserves_approved_copy(self):
        self.assertEqual(livetalking_request('价格199元。', 'session_123'),
                         {'sessionid':'session_123', 'type':'echo', 'text':'价格199元。', 'interrupt':False})

    def test_invalid_request(self):
        for text, sid in [('', '123'), ('口播', ''), ('口播','a/b'), ('字'*5001,'123')]:
            with self.subTest(text=text[:5], sid=sid), self.assertRaises(ValidationError):
                livetalking_request(text,sid)

    def test_cli_failure_exit(self):
        (self.root/'script.txt').write_text('错稿', encoding='utf-8')
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('avatar_qa.py')), 'check',
            '--audio', str(self.root/'synthetic-tone.wav'), '--srt', str(self.root/'captions.srt'),
            '--script', str(self.root/'script.txt'), '--out', str(self.root/'report.json')], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads((self.root/'report.json').read_text())['status'], 'FAIL')

if __name__ == '__main__': unittest.main()

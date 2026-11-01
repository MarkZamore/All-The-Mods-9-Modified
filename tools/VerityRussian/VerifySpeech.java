import com.k2fsa.sherpa.onnx.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
import javax.sound.sampled.*;
import org.lwjgl.stb.STBVorbis;
import org.lwjgl.system.MemoryStack;
import org.lwjgl.system.libc.LibCStdlib;

/** Native CPU diagnostic only: no microphone, sound playback, game class or network. */
public final class VerifySpeech {
    static void report(String kind, String name, String text, int samples, int rate) {
        System.out.println(String.join("\t", kind, Base64.getEncoder().encodeToString(name.getBytes(java.nio.charset.StandardCharsets.UTF_8)),
            Base64.getEncoder().encodeToString(text.getBytes(java.nio.charset.StandardCharsets.UTF_8)), Integer.toString(samples), Integer.toString(rate)));
    }
    static float[] mono(Path file) throws Exception {
        float[] input; int rate;
        if (file.toString().endsWith(".ogg")) {
            try (MemoryStack stack = MemoryStack.stackPush()) {
                IntBuffer ch = stack.mallocInt(1), sr = stack.mallocInt(1);
                ShortBuffer raw = STBVorbis.stb_vorbis_decode_filename(file.toString(), ch, sr);
                if (raw == null) throw new IllegalStateException("Cannot decode author clip " + file);
                int channels = ch.get(0); rate = sr.get(0); input = new float[raw.remaining() / channels];
                for (int i = 0; i < input.length; ++i) {
                    float value = 0;
                    for (int c = 0; c < channels; ++c) value += raw.get(i * channels + c) / 32768f;
                    input[i] = value / channels;
                }
                LibCStdlib.free(raw);
            }
        } else {
            try (AudioInputStream original = AudioSystem.getAudioInputStream(file.toFile())) {
                AudioFormat f = original.getFormat();
                AudioFormat format = new AudioFormat(AudioFormat.Encoding.PCM_SIGNED, f.getSampleRate(), 16, f.getChannels(), 2 * f.getChannels(), f.getSampleRate(), false);
                try (AudioInputStream pcm = AudioSystem.getAudioInputStream(format, original)) {
                    byte[] bytes = pcm.readAllBytes(); int channels = format.getChannels(); rate = (int)format.getSampleRate();
                    input = new float[bytes.length / (channels * 2)];
                    for (int i = 0; i < input.length; ++i) {
                        float value = 0;
                        for (int c = 0; c < channels; ++c) {
                            int pos = (i * channels + c) * 2;
                            value += (short)((bytes[pos] & 255) | (bytes[pos + 1] << 8)) / 32768f;
                        }
                        input[i] = value / channels;
                    }
                }
            }
        }
        int size = (int)Math.round(input.length * 16000.0 / rate);
        float[] output = new float[size + 16000]; // 500ms diagnostic silence each side.
        for (int i = 0; i < size; ++i) {
            double position = i * (rate / 16000.0);
            int low = Math.min((int)position, input.length - 1), high = Math.min(low + 1, input.length - 1);
            output[i + 8000] = (float)(input[low] + (input[high] - input[low]) * (position - low));
        }
        return output;
    }
    public static void main(String[] args) throws Exception {
        if (args[0].equals("tts")) {
            Path piper = Path.of(args[1]), out = Path.of(args[2]); Files.createDirectories(out);
            var model = OfflineTtsVitsModelConfig.builder().setModel(piper.resolve("ru_RU-denis-medium.onnx").toString())
                .setTokens(piper.resolve("tokens.txt").toString()).setDataDir(piper.resolve("espeak-ng-data").toString()).build();
            var config = OfflineTtsConfig.builder().setModel(OfflineTtsModelConfig.builder().setVits(model).setNumThreads(2).setDebug(false).build()).build();
            var engine = new OfflineTts(config);
            try {
                for (int i = 3; i < args.length; ++i) {
                    GenerationConfig generation = new GenerationConfig(); generation.setSid(0); generation.setSpeed(1f); generation.setSilenceScale(.2f);
                    GeneratedAudio audio = engine.generateWithConfigAndCallback(args[i], generation, samples -> 1);
                    if (audio == null || audio.getSamples().length == 0 || !audio.save(out.resolve("line-" + (i - 3) + ".wav").toString()))
                        throw new IllegalStateException("Native Russian TTS returned no audio");
                    report("TTS", "line-" + (i - 3), args[i], audio.getSamples().length, audio.getSampleRate());
                }
            } finally { engine.release(); }
        } else {
            Path model = Path.of(args[1]); String language = args[2];
            var whisper = OfflineWhisperModelConfig.builder().setEncoder(model.resolve("base-encoder.int8.onnx").toString())
                .setDecoder(model.resolve("base-decoder.int8.onnx").toString()).setLanguage(language).setTask("transcribe").build();
            var config = OfflineRecognizerConfig.builder().setOfflineModelConfig(OfflineModelConfig.builder().setWhisper(whisper)
                .setTokens(model.resolve("base-tokens.txt").toString()).setNumThreads(2).setDebug(false).build()).build();
            var recognizer = new OfflineRecognizer(config);
            try {
                for (int i = 3; i < args.length; ++i) {
                    Path file = Path.of(args[i]); float[] waveform = mono(file); var stream = recognizer.createStream();
                    try {
                        stream.acceptWaveform(waveform, 16000); recognizer.decode(stream);
                        report("STT", file.getFileName().toString(), recognizer.getResult(stream).getText(), waveform.length, 16000);
                    } finally { stream.release(); }
                }
            } finally { recognizer.release(); }
        }
    }
}

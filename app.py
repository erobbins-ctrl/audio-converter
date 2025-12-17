from flask import Flask, request, send_file
import subprocess, tempfile, os

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return "Missing file", 400

    file = request.files["file"]

    with tempfile.TemporaryDirectory() as tmp:
        wav_path = os.path.join(tmp, "input.wav")
        mp3_path = os.path.join(tmp, "output.mp3")

        file.save(wav_path)

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", wav_path,
                "-codec:a", "libmp3lame",
                "-qscale:a", "2",
                mp3_path
            ],
            check=True
        )

        return send_file(mp3_path, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

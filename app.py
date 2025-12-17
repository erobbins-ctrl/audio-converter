from flask import Flask, request, jsonify
import subprocess, tempfile, os
import paramiko

app = Flask(__name__)

def upload_to_kinsta(local_path, filename):
    host = os.environ["SFTP_HOST"]
    port = int(os.environ.get("SFTP_PORT", 22))
    user = os.environ["SFTP_USER"]
    password = os.environ["SFTP_PASS"]
    remote_dir = os.environ["SFTP_TARGET_DIR"]

    transport = paramiko.Transport((host, port))
    transport.connect(username=user, password=password)

    sftp = paramiko.SFTPClient.from_transport(transport)

    remote_path = f"{remote_dir}/{filename}"
    sftp.put(local_path, remote_path)

    sftp.close()
    transport.close()

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    with tempfile.TemporaryDirectory() as tmp:
        wav_path = os.path.join(tmp, "input.wav")
        mp3_name = os.path.splitext(file.filename)[0] + ".mp3"
        mp3_path = os.path.join(tmp, mp3_name)

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

        upload_to_kinsta(mp3_path, mp3_name)

        return jsonify({
            "status": "success",
            "uploaded_to": mp3_name
        }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

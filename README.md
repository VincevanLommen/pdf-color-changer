# PDF Color Changer

Converts black text and lines in a PDF to a color of your choice, so you can print on a single-ink printer. Runs on port 3150.

*Vibe-coded with Claude because I got tired of online PDF color changers full of fake download buttons.*

## Install on the homeserver

From your laptop, in the folder that contains this project:

    scp -r pdf-color-changer vince@192.168.0.198:/tmp/

Then on the server:

    ssh vince@192.168.0.198
    sudo mv /tmp/pdf-color-changer /srv/docker/
    cd /srv/docker/pdf-color-changer
    docker compose up -d --build

Check that it runs:

    curl http://localhost:3150/health

Open `http://192.168.0.198:3150` in a browser on your home network.

## Update

    cd /srv/docker/pdf-color-changer
    docker compose up -d --build

## Logs and stop

    docker compose logs -f
    docker compose down

## Notes

- Pages are rendered at 300 DPI, which keeps barcodes sharp. The output is image-based, so the text is no longer searchable.
- Files are processed in memory and never written to disk.
- There is no login. Do not expose port 3150 to the internet.
- To add or change colors, edit `PALETTE` in `recolor.py`.

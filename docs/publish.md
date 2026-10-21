# Publishing the Hugging Face Bucket

The form asks for a **public** Hugging Face Bucket. Run these yourself after the README is final.

```bash
pip install -U huggingface_hub
hf auth login                      # paste a token with write access
hf buckets create darija-temporal-pilot          # public by default; do not add --private
hf buckets sync . hf://buckets/<your-hf-username>/darija-temporal-pilot --exclude ".git/*" --exclude "*__pycache__*" --exclude "*.zip"
hf buckets info <your-hf-username>/darija-temporal-pilot   # check "private": false
```

Then open https://huggingface.co/buckets/<your-hf-username>/darija-temporal-pilot in a private browser window to confirm it is visible, and paste that link in the form.

import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI(debug=False, title="GhostLock", description="Concealing Your Critical Communications")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def extend_key(message, key):
    extended_key = key * (len(message) // len(key)) + key[:len(message) % len(key)]
    return extended_key

def encrypt(message, key):
    extended_key = extend_key(message, key)
    encrypted_message = ""
    for i, char in enumerate(message):
        shift = ord(extended_key[i]) - ord('A')
        if char.isalpha():
            if char.isupper():
                encrypted_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            else:
                encrypted_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
        else:
            encrypted_char = char
        encrypted_message += encrypted_char
    return encrypted_message

def decrypt(encrypted_message, key):
    extended_key = extend_key(encrypted_message, key)
    decrypted_message = ""
    for i, char in enumerate(encrypted_message):
        shift = ord(extended_key[i]) - ord('A')
        if char.isalpha():
            if char.isupper():
                decrypted_char = chr((ord(char) - ord('A') - shift + 26) % 26 + ord('A'))
            else:
                decrypted_char = chr((ord(char) - ord('a') - shift + 26) % 26 + ord('a'))
        else:
            decrypted_char = char
        decrypted_message += decrypted_char
    return decrypted_message


@app.post("/encrypt", response_class=HTMLResponse)
async def encrypt_message(request: Request, message: str = Form(...), key: str = Form(...)):
    encrypted_msg = encrypt(message, key)
    return templates.TemplateResponse("index.html", {"request": request, "encrypted_message": encrypted_msg})


@app.post("/decrypt", response_class=HTMLResponse)
async def decrypt_message(request: Request, message: str = Form(...), key: str = Form(...)):
    decrypted_msg = decrypt(message, key)
    return templates.TemplateResponse("index.html", {"request": request, "decrypted_message": decrypted_msg})


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
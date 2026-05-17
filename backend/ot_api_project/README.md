# 998 Ebook Backend — Old OT Core + FastAPI Wrapper

This version keeps the old OT design and only adds a clean API wrapper.

## What this version keeps

- Client-side `choice_index`
- Client-side bit path
- Old 1-out-of-N OT masking design
- Server generates masked keys for a whole public group
- API never receives `choice_index`, `bit`, or final selected book

## What this version removes

- No order API
- No `book_ids` request body
- No `OrderItem(book_id)` logic
- No order-based OT

## Project structure

```text
api/ot_api.py                  FastAPI routes
core/config.py                 DH parameters
core/utils.py                  XOR, bit conversion, next power of two
core/prf.py                    SHA-256 based PRF
core/ot_channel.py             One-layer DH-style OT
server/ot_server.py            Old 1-out-of-N masking server
server/book_storage_service.py Encrypts demo books and returns group package
server/ot_flow_service.py      Bridge between old OT and API
client/ot_receiver.py          Client-side OT receiver logic
main.py                        FastAPI app entry
run_local_test.py              End-to-end test without starting HTTP server
client_api_demo.py             Demo client for a running server
```

## Install

```bash
pip install -r requirements.txt
```

## Test without starting server

```bash
python run_local_test.py
```

Expected output ends with:

```text
SUCCESS: old OT core works through the API wrapper.
```

## Run API server

```bash
uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Run HTTP client demo

In another terminal:

```bash
python client_api_demo.py
```

## Main privacy rule

Never send these values to the server:

```text
choice_index
bit
selected book id
```

The server may know the public `group_id`, but it does not know which book index inside that group the client selected.

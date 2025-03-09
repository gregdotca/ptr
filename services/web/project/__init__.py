#!/usr/bin/env python3
import socket
from flask import Flask, redirect, render_template, request
from time import sleep

app = Flask(__name__, static_folder="assets")

APP_TITLE = "PTR Record Lookup"
DEFAULT_ADDRESS = "8.8.8.8"


@app.route("/", methods=["GET"])
def home():
    return redirect("/" + DEFAULT_ADDRESS, code=302)


@app.route("/<address>", methods=["GET"])
def lookup_get(address):
    return display_homepage(address, get_ptr(address))


@app.route("/", methods=["POST"])
def lookup_post():
    sleep(0.25)

    if str(request.form["address"]) == "":
        full_url = DEFAULT_ADDRESS
    else:
        full_url = str(request.form["address"])

    return redirect(full_url, code=302)


def display_homepage(address, page_body):
    return render_template(
        "home.html",
        app_title=APP_TITLE,
        address=address,
        page_body=page_body,
    )


def get_ptr(address):
    address = address or DEFAULT_ADDRESS

    try:

        ptr_lookup_result = address + ' -> ' + socket.getnameinfo((address, 0), 0)[0]

    except Exception:

        ptr_lookup_result = "Unable to lookup PTR record"

    return ptr_lookup_result


if __name__ == "__main__":
    app.run()

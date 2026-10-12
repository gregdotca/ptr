#!/usr/bin/env python3
import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, redirect, render_template, request, url_for
from time import sleep

app = Flask(__name__, static_folder="assets")

APP_TITLE = "PTR Record Lookup"
DEFAULT_ADDRESS = "8.8.8.8"
INVALID_ADDRESS = "Invalid IP address"
LOOKUP_TIMEOUT = 3

# getnameinfo() has no timeout of its own, so lookups run here and the
# request stops waiting after LOOKUP_TIMEOUT seconds. A lookup that's
# still running keeps its pool thread until the resolver gives up, but
# never holds up a gunicorn thread for longer than the timeout.
lookup_pool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="ptr-lookup")


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return redirect("/" + DEFAULT_ADDRESS)
    else:
        sleep(0.25)

        address = request.form.get("address", "") or DEFAULT_ADDRESS

        # url_for() encodes the value, so the redirect always stays on this site
        return redirect(url_for("lookup_get", address=address))


@app.route("/<address>", methods=["GET"])
def lookup_get(address):
    # A 404 tells crawlers and bots probing paths like /robots.txt that
    # there's nothing here, while people still see the normal page
    if not is_ip_address(address):
        return display_homepage(address, INVALID_ADDRESS), 404

    return display_homepage(address, get_ptr(address))


def display_homepage(address, page_body):
    return render_template(
        "home.html",
        app_title=APP_TITLE,
        address=address,
        page_body=page_body,
    )


def is_ip_address(address):
    try:

        ipaddress.ip_address(address)

    except ValueError:

        return False

    return True


def get_ptr(address):
    address = address or DEFAULT_ADDRESS

    if not is_ip_address(address):
        return INVALID_ADDRESS

    try:

        # NI_NAMEREQD makes getnameinfo() raise when there's no PTR record,
        # instead of returning the address as if it were the hostname
        lookup = lookup_pool.submit(
            socket.getnameinfo, (address, 0), socket.NI_NAMEREQD
        )
        hostname = lookup.result(timeout=LOOKUP_TIMEOUT)[0]

    except TimeoutError:

        # Drop the lookup if it's still queued behind slow ones
        lookup.cancel()

        return "Unable to lookup PTR record"

    except socket.gaierror as e:

        if e.errno == socket.EAI_NONAME:
            return "No PTR record found for " + address

        return "Unable to lookup PTR record"

    except OSError:

        return "Unable to lookup PTR record"

    return address + ' -> ' + hostname


if __name__ == "__main__":
    app.run()

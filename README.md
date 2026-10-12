ptr
---

[![ACR B3b](https://img.shields.io/badge/ACR-B3b-2140B5)](ACR.md)

## Demo

https://ptr.greg.ca

## Installation

- Clone the repository
- Run `PTR_BIND_ADDRESS=127.0.0.1 docker-compose up -d --build`, replacing
  `127.0.0.1` with the address of the network interface to serve on
  (`0.0.0.0` for all of them)
- Load http://127.0.0.1:8101 (or that address) in your web browser

`PTR_BIND_ADDRESS` can also go in a `.env` file next to
`docker-compose.yml`. Without it, the app binds to `10.0.0.3`, which is
the address of the demo server and probably doesn't exist on yours.

## License

MIT License

Copyright (c) 2025-2026 Greg Chetcuti <greg@chetcuti.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

import re

from urllib.parse import urljoin

import html2text

from aiohttp import ClientSession, web


def change_links(string, old_link, new_link):
    return re.sub(rf"\b{old_link}\b", new_link, string)


def validate_words(words, word_length):
    validated_words = []
    for raw_word in words:
        words_regexp = re.findall(
            r"\b\w+\b", raw_word
        )
        for word in words_regexp:
            if len(word) == word_length:
                validated_words.append(word)
    return validated_words


async def proxy_with_symbol(request):
    target_url = urljoin(url_to_change, request.match_info["item"])

    async with ClientSession() as session:
        async with session.get(target_url) as resp:
            content_type = resp.content_type
            if content_type != "text/html":
                return web.Response(
                    body=await resp.read(), content_type=content_type
                )
            html = await resp.text()

        words = validate_words(
            html2text.html2text(html).replace("\n", "").split(" "), word_length
        )
        html = change_links(html, url_to_change, proxy_url)
        changed_words = set()
        for word in words:
            if word not in changed_words:
                html = re.sub(rf"\b{word}\b", f"{word}{symbol_to_add}", html)
                changed_words.add(word)

        return web.Response(body=html, content_type="text/html")


def main():
    global url_to_change, proxy_url, symbol_to_add, word_length

    url_to_change = "https://news.ycombinator.com/item?id=13713480"
    proxy_url = "http://127.0.0.1:8080"
    symbol_to_add = "™"
    word_length = 6

    app = web.Application()
    app.add_routes([web.get("/{item:.*}", proxy_with_symbol)])

    web.run_app(app)


if __name__ == "__main__":
    main()

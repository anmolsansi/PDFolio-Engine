from app.services.extractor import extract_text


def test_extract_text_strips_scripts():
    html = """
    <html>
      <head><script>console.log('x')</script></head>
      <body><p>Hello <b>world</b></p></body>
    </html>
    """
    assert extract_text(html) == "Hello world"

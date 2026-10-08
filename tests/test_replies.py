from app import MAX_POST_LENGTH, POST_LIMIT


def make_post(client, auth, content="original post"):
    auth.register()
    auth.login()
    client.post("/", data={"content": content})


def test_logged_out_user_cannot_reply(client, auth):
    make_post(client, auth)
    auth.logout()
    response = client.post("/post/1/reply", data={"content": "sneaky"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"
    assert b"sneaky" not in client.get("/").data


def test_logged_out_user_sees_no_reply_form(client, auth):
    make_post(client, auth)
    auth.logout()
    assert b'class="reply-form"' not in client.get("/").data


def test_reply_appears_under_post_with_author(client, auth):
    make_post(client, auth)
    auth.logout()
    auth.register(username="bob")
    auth.login(username="bob")
    response = client.post("/post/1/reply", data={"content": "nice post"}, follow_redirects=True)
    assert b'<p class="reply-content">nice post</p>' in response.data
    assert b"bob" in response.data


def test_replies_stay_with_their_own_post(client, auth):
    make_post(client, auth, "first")
    client.post("/", data={"content": "second"})
    client.post("/post/1/reply", data={"content": "only on first"})
    page = client.get("/").data.decode()
    # The feed is newest first, so "second" renders above "first".
    second, first = page.index("second"), page.index("first")
    assert second < first < page.index("only on first")


def test_reply_to_missing_post_is_404(client, auth):
    auth.register()
    auth.login()
    assert client.post("/post/999/reply", data={"content": "hello?"}).status_code == 404


def test_reply_html_is_escaped(client, auth):
    make_post(client, auth)
    response = client.post(
        "/post/1/reply", data={"content": "<script>x</script>"}, follow_redirects=True
    )
    assert b"<script>x</script>" not in response.data
    assert b"&lt;script&gt;" in response.data


def test_empty_reply_is_ignored(client, auth):
    make_post(client, auth)
    response = client.post("/post/1/reply", data={"content": "   "}, follow_redirects=True)
    assert b'class="reply"' not in response.data


def test_too_long_reply_is_rejected(client, auth):
    make_post(client, auth)
    response = client.post(
        "/post/1/reply", data={"content": "a" * (MAX_POST_LENGTH + 1)}, follow_redirects=True
    )
    assert b"at most" in response.data
    assert b'class="reply"' not in response.data


def test_reply_rate_limit(client, auth):
    make_post(client, auth)
    for i in range(POST_LIMIT):
        client.post("/post/1/reply", data={"content": f"reply {i}"})
    response = client.post(
        "/post/1/reply", data={"content": "one too many"}, follow_redirects=True
    )
    assert b"Try again in a few minutes." in response.data
    assert b'<p class="reply-content">one too many</p>' not in response.data

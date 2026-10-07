from app import MAX_POST_LENGTH, POST_LIMIT


def test_logged_out_user_cannot_post(client, app):
    response = client.post("/", data={"content": "hello"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"
    assert b"hello" not in client.get("/").data


def test_logged_out_user_sees_no_post_form(client):
    assert b'class="post-form"' not in client.get("/").data


def test_post_appears_in_feed_with_author(client, auth):
    auth.register()
    auth.login()
    response = client.post("/", data={"content": "first post!"}, follow_redirects=True)
    assert b"first post!" in response.data
    assert b"alice" in response.data


def test_post_html_is_escaped(client, auth):
    auth.register()
    auth.login()
    response = client.post("/", data={"content": "<script>x</script>"}, follow_redirects=True)
    assert b"<script>x</script>" not in response.data
    assert b"&lt;script&gt;" in response.data


def test_empty_post_is_ignored(client, auth):
    auth.register()
    auth.login()
    response = client.post("/", data={"content": "   "}, follow_redirects=True)
    assert b"No posts yet" in response.data


def test_too_long_post_is_rejected_and_kept_as_draft(client, auth):
    auth.register()
    auth.login()
    content = "a" * (MAX_POST_LENGTH + 1)
    response = client.post("/", data={"content": content})
    assert response.status_code == 200
    assert b"at most" in response.data
    # The draft is returned in the textarea, not published to the feed.
    assert b"No posts yet" in response.data


def test_rate_limit_blocks_extra_posts(client, auth):
    auth.register()
    auth.login()
    for i in range(POST_LIMIT):
        client.post("/", data={"content": f"post {i}"})

    response = client.post("/", data={"content": "one too many"})
    assert response.status_code == 200
    assert b"Try again in a few minutes." in response.data
    assert b'<p class="post-content">one too many</p>' not in response.data


def test_rate_limit_is_per_user(client, auth):
    auth.register()
    auth.login()
    for i in range(POST_LIMIT):
        client.post("/", data={"content": f"post {i}"})
    auth.logout()

    auth.register(username="bob")
    auth.login(username="bob")
    response = client.post("/", data={"content": "bob says hi"}, follow_redirects=True)
    assert b"bob says hi" in response.data

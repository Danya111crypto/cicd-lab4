from flask import Flask

app = Flask(__name__)

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Login</title></head>
<body>
  <h1>Sign In</h1>
  <form id="login-form">
    <input type="email" name="email" placeholder="Email" required />
    <input type="password" name="password" placeholder="Password" required />
    <button type="submit">Login</button>
  </form>
  <script>
    document.getElementById('login-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.querySelector('input[name="email"]').value;
      const password = document.querySelector('input[name="password"]').value;
      const resp = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (resp.ok) {
        const data = await resp.json();
        localStorage.setItem('token', data.token);
        localStorage.setItem('userEmail', email);
        window.location.href = '/dashboard';
      }
    });
  </script>
</body>
</html>"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Dashboard</title></head>
<body>
  <h1 id="greeting"></h1>
  <script>
    const email = localStorage.getItem('userEmail') || 'Guest';
    document.getElementById('greeting').textContent = 'Welcome, ' + email;
  </script>
</body>
</html>"""


@app.route("/login")
def login_page():
    return LOGIN_HTML


@app.route("/dashboard")
def dashboard_page():
    return DASHBOARD_HTML


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000)
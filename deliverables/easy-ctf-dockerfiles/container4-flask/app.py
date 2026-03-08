from flask import Flask, request, make_response, redirect, url_for

app = Flask(__name__)

FLAG = "FLAG{c00k13_m0nst3r_str1k3s}"

STYLE = """
<style>
  * { box-sizing: border-box; }
  body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; }
  header { background: #16213e; padding: 15px 40px; border-bottom: 3px solid #e94560; }
  header h1 { margin: 0; color: #e94560; font-size: 1.2em; letter-spacing: 2px; }
  .container { max-width: 700px; margin: 60px auto; padding: 0 20px; }
  .card { background: #16213e; border: 1px solid #0f3460; border-radius: 6px; padding: 30px; margin-bottom: 20px; }
  .flag { background: #0f3460; color: #00ff88; font-family: monospace; font-size: 1.3em;
          padding: 15px 20px; border-radius: 4px; border: 1px solid #00ff88; margin-top: 15px; }
  .info { background: #0d1b2a; border-left: 4px solid #e94560; padding: 12px 18px; font-family: monospace;
          font-size: 0.9em; color: #aaa; margin-top: 15px; border-radius: 0 4px 4px 0; }
  .btn { display: inline-block; background: #e94560; color: white; padding: 10px 25px;
         border-radius: 4px; text-decoration: none; font-size: 0.9em; margin-top: 15px; }
  h2 { color: #e94560; margin-top: 0; }
  p { color: #aaa; line-height: 1.7; }
  .role-badge { display: inline-block; padding: 3px 12px; border-radius: 3px; font-family: monospace;
                font-size: 0.85em; font-weight: bold; }
  .role-user  { background: #1a3a5c; color: #5ba4d4; }
  .role-admin { background: #1a4a1a; color: #5ad45a; }
</style>
"""

@app.route("/")
def index():
    role = request.cookies.get("role", "")
    if not role:
        resp = make_response(redirect("/portal"))
        resp.set_cookie("role", "user", httponly=False)
        return resp
    return redirect("/portal")

@app.route("/portal")
def portal():
    role = request.cookies.get("role", "user")
    badge_class = "role-admin" if role == "admin" else "role-user"

    if role == "admin":
        content = f"""
        <div class="card">
          <h2>&#x1F6E1; Admin Panel — Authenticated</h2>
          <p>Welcome, Administrator. Elevated access granted.</p>
          <p>Current session role: <span class="role-badge role-admin">admin</span></p>
          <p>Captured intelligence artifact recovered from session store:</p>
          <div class="flag">{FLAG}</div>
        </div>
        <div class="card">
          <h2>Analyst Note</h2>
          <p>The attacker bypassed authentication entirely by editing the <code>role</code> cookie
          from <code>user</code> to <code>admin</code>. No signature, no server-side validation.
          This is an insecure direct object reference combined with client-side trust.</p>
          <p>In real SOC work, cookie manipulation like this leaves traces in your web access logs —
          look for the same session making requests to <code>/portal</code> with different role values.</p>
        </div>
        """
    else:
        content = f"""
        <div class="card">
          <h2>&#x1F512; User Portal</h2>
          <p>You are logged in as a standard user.</p>
          <p>Current session role: <span class="role-badge role-user">{role}</span></p>
          <p>You do not have access to the admin panel.</p>
          <div class="info">
            Hint: Your browser is storing something about your session.
            Check your cookies for this domain.
          </div>
        </div>
        <div class="card">
          <h2>Analyst Briefing</h2>
          <p>During the FICTIONAL-CORP incident, the attacker gained privileged access to this
          internal portal without valid credentials. The attacker's browser made a single
          modified request. Replicate the technique to access the admin panel.</p>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FICTIONAL-CORP Portal</title>
  {STYLE}
</head>
<body>
<header><h1>FICTIONAL-CORP // SESSION PORTAL</h1></header>
<div class="container">
  {content}
</div>
</body>
</html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

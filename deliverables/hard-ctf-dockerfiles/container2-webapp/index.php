<?php
$db = new SQLite3('/var/www/html/ctf.db');
$error = '';
$logged_in = false;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    // INTENTIONALLY VULNERABLE — no parameterised query, no escaping
    $query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
    $result = $db->query($query);

    if ($result && $result->fetchArray()) {
        header('Location: /admin.php');
        exit;
    } else {
        $error = 'Invalid credentials.';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FICTIONAL-CORP — Secure Portal</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
<div class="login-wrap">
  <div class="login-box">
    <div class="logo">FICTIONAL-CORP</div>
    <div class="subtitle">SECURE INTERNAL PORTAL</div>
    <?php if ($error): ?>
      <div class="error"><?= htmlspecialchars($error) ?></div>
    <?php endif; ?>
    <form method="POST" action="/">
      <label>Username</label>
      <input type="text" name="username" autocomplete="off" placeholder="Enter username">
      <label>Password</label>
      <input type="password" name="password" placeholder="Enter password">
      <button type="submit">Sign In</button>
    </form>
    <div class="footer-note">FICTIONAL-CORP Internal Use Only</div>
  </div>
</div>
</body>
</html>

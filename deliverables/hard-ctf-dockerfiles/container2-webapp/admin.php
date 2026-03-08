<?php
// No authentication check — bypassed entirely by SQLi
// The entire users table is displayed including password_hash
$db = new SQLite3('/var/www/html/ctf.db');
$users = $db->query("SELECT id, username, password, password_hash, role FROM users");
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Admin Panel — FICTIONAL-CORP</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
<div class="admin-wrap">
  <header class="admin-header">
    <span class="logo-sm">FICTIONAL-CORP</span>
    <span class="panel-title">ADMINISTRATOR PANEL</span>
    <span class="flag-badge">FLAG{sql_1nj3ct10n_byp4ss}</span>
  </header>

  <div class="admin-body">

    <div class="alert-box">
      <strong>&#x26A0; SQL Injection Bypass Detected</strong><br>
      Authentication was bypassed using a tautological SQL injection payload.
      The query executed was: <code>SELECT * FROM users WHERE username = 'admin' -- ' AND password = ''</code>
    </div>

    <h2>User Database Dump</h2>
    <p class="note">The full users table is exposed below. Note the <code>password_hash</code> field for the
    <strong>sysadmin</strong> account — this is a SHA-512 crypt hash. It can be cracked offline.</p>

    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Username</th>
          <th>Password (cleartext)</th>
          <th>Password Hash (SHA-512 crypt)</th>
          <th>Role</th>
        </tr>
      </thead>
      <tbody>
        <?php while ($row = $users->fetchArray(SQLITE3_ASSOC)): ?>
        <tr>
          <td><?= (int)$row['id'] ?></td>
          <td><strong><?= htmlspecialchars($row['username']) ?></strong></td>
          <td class="mono"><?= htmlspecialchars($row['password']) ?></td>
          <td class="mono hash-cell"><?= htmlspecialchars($row['password_hash'] ?? 'NULL') ?></td>
          <td><span class="role-badge role-<?= htmlspecialchars($row['role']) ?>"><?= htmlspecialchars($row['role']) ?></span></td>
        </tr>
        <?php endwhile; ?>
      </tbody>
    </table>

    <div class="next-step">
      <strong>Next:</strong> The sysadmin hash can be cracked with john and rockyou.txt.
      The cracked plaintext is also used elsewhere — look for hidden directories on this server.
    </div>

  </div>
</div>
</body>
</html>

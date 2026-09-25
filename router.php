<?php
session_start();

$ADMIN_USERNAME = _xor([0x1E, 0x41, 0x0E]);
$ADMIN_PASSWORD = _xor([0x04, 0x59, 0x00, 0x1E, 0x46, 0x16, 0x00]);

function _xor($data) {
    $key = [0x73, 0x33, 0x63, 0x72, 0x33, 0x74];
    $out = '';
    foreach ($data as $i => $byte) $out .= chr($byte ^ $key[$i % count($key)]);
    return $out;
}

function is_logged_in() {
    return ($_SESSION['admin_logged_in'] ?? false) === true;
}

function require_login() {
    if (!is_logged_in()) {
        header('Location: /login');
        http_response_code(302);
        exit;
    }
}

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$file = __DIR__ . $path;
if ($path !== '/' && is_file($file)) {
    $mime_types = [
        'css' => 'text/css',
        'js' => 'application/javascript',
        'svg' => 'image/svg+xml',
    ];
    $extension = strtolower(pathinfo($file, PATHINFO_EXTENSION));
    $mime = $mime_types[$extension] ?? (mime_content_type($file) ?: 'application/octet-stream');
    header('Content-Type: ' . $mime);
    readfile($file);
    exit;
}

function rows_from_csv($file) {
    $rows = [];
    $handle = fopen($file, 'r');
    if (!$handle) return $rows;
    $headers = fgetcsv($handle);
    while (($values = fgetcsv($handle)) !== false) {
        if (count($values) === count($headers)) $rows[] = array_combine($headers, $values);
    }
    fclose($handle);
    return $rows;
}

function e($value) {
    return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
}

function csv_value($row, $name) {
    if (isset($row[$name])) return $row[$name];
    foreach ($row as $key => $value) {
        if (trim((string) $key) === $name) return $value;
    }
    return '';
}

function social_markup($value) {
    $text = preg_replace('/\s+instagram\s*$/i', '', (string) $value);
    if (preg_match('/\[([^\]]+)\]\((https?:\/\/(?:www\.)?instagram\.com\/[^\s)]+)\)/i', $text, $markdown)) {
        return 'Social: <a href="' . e($markdown[2]) . '" target="_blank" rel="noopener">' . e($markdown[1]) . '</a>';
    }
    $escaped = e($text);
    if (preg_match('~https?://(?:www\.)?instagram\.com/[^\s)]+~i', $text, $match)) {
        $link = e($match[0]);
        return 'Social: ' . str_replace($link, '<a href="' . $link . '" target="_blank" rel="noopener">' . $link . '</a>', $escaped);
    }
    if (preg_match('/(?:instagram|ig)\s*:?\s*(?!\(?instagram\)?)([a-z0-9._]+)/i', $text, $match)) {
        $handle = e($match[1]);
        return 'Social: ' . str_replace($match[0], '<a href="https://www.instagram.com/' . $handle . '" target="_blank" rel="noopener">' . $handle . '</a>', $escaped);
    }
    if (preg_match('/([a-z0-9._]+)\s*\(instagram\)/i', $text, $match)) {
        $handle = e($match[1]);
        return 'Social: ' . str_replace($match[0], '<a href="https://www.instagram.com/' . $handle . '" target="_blank" rel="noopener">' . $handle . '</a>', $escaped);
    }
    if (preg_match('/@([a-z0-9._]+)/i', $text, $match)) {
        $handle = e($match[1]);
        return 'Social: ' . str_replace($match[0], '<a href="https://www.instagram.com/' . $handle . '" target="_blank" rel="noopener">' . $handle . '</a>', $escaped);
    }
    if (preg_match('/([a-z0-9._]+)/i', $text, $match)) {
        $handle = e($match[1]);
        return 'Social: ' . str_replace($match[0], '<a href="https://www.instagram.com/' . $handle . '" target="_blank" rel="noopener">' . $handle . '</a>', $escaped);
    }
    return 'Social: ' . $escaped;
}

function start_page() {
    echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>WJ Clubs</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"><link rel="stylesheet" href="/static/clubslist.css"><link rel="stylesheet" href="/static/admin.css"></head><body><nav class="navbar navbar-expand-lg site-nav"><div class="container-fluid px-3 px-lg-4"><a class="navbar-brand d-flex align-items-center gap-2" href="/"><img src="/static/icons/main_logo.png" alt="WJ Clubs" class="brand-logo"><span>WJ Clubs</span></a><button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav" aria-controls="mainNav" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button><div class="collapse navbar-collapse" id="mainNav"><ul class="navbar-nav me-auto mb-2 mb-lg-0 align-items-lg-center"><li class="nav-item"><a class="nav-link active" href="/">All Clubs</a></li><li class="nav-item"><a target="_blank" class="nav-link" href="https://www.montgomeryschoolsmd.org/schools/wjhs/">WJ Main Page</a></li><li class="nav-item"><a target="_blank" class="nav-link" href="https://www.montgomeryschoolsmd.org/schools/wjhs/students/">Start a Club</a></li><li class="nav-item"><a target="_blank" class="nav-link" href="https://www.montgomeryschoolsmd.org/schools/wjhs/staff/staff-directory/?processlevel=04424">Staff Email List</a></li><li class="nav-item"><a target="_blank" class="nav-link" href="https://wjboosterclub.org/">Booster Club</a></li></ul><a class="admin-link" href="/login">Login</a></div></div></nav>';
}

function end_page() {
    echo '<footer class="site-footer"><div class="container">All clubs and organizations are inclusive of all students regardless of sex or gender identity. Website created by Web Development Club and renewed by Hack Club.</div></footer><script>const queryInput=document.getElementById("query");const categoryInput=document.getElementById("category");const clubItems=Array.from(document.querySelectorAll("[data-club-item]"));const resultCount=document.querySelector(".result-count");function filterClubs(){const query=queryInput.value.trim().toLowerCase();const category=categoryInput.value.toLowerCase();let visible=0;clubItems.forEach(item=>{const matchesQuery=!query||item.dataset.searchText.toLowerCase().includes(query);const matchesCategory=!category||item.dataset.category.toLowerCase().includes(category);item.hidden=!(matchesQuery&&matchesCategory);if(!item.hidden)visible++});resultCount.textContent=`Showing ${visible} of ${clubItems.length} clubs`}if(queryInput)queryInput.addEventListener("input",filterClubs);if(categoryInput)categoryInput.addEventListener("change",filterClubs);</script><script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script></body></html>';
}

if ($path === '/login') {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $username = trim($_POST['username'] ?? '');
        $password = trim($_POST['password'] ?? '');
        if ($username === $ADMIN_USERNAME && $password === $ADMIN_PASSWORD) {
            $_SESSION['admin_logged_in'] = true;
            header('Location: /admin');
            http_response_code(302);
            exit;
        }
        $error = 'Invalid username or password';
    }
    start_page();
    echo '<main class="login-page"><section class="outlined-box"><h1>Login</h1>';
    if (isset($error)) echo '<div class="alert alert-danger">' . e($error) . '</div>';
    echo '<form method="post" action="/login"><label for="username">Username</label><input id="username" name="username"><label for="password">Password</label><input id="password" name="password" type="password"><button class="btn search-button mt-3" type="submit">Sign in</button></form><a class="btn btn-secondary mt-3" href="/">Back to Clubs</a></section></main>';
    end_page();
    exit;
}

if ($path === '/logout') {
    session_destroy();
    header('Location: /login');
    http_response_code(302);
    exit;
}

if ($path === '/admin') {
    require_login();
    start_page();
    echo '<main class="admin-shell"><div class="admin-heading"><p class="section-label">Site management</p><h1>Admin dashboard</h1><p>Update club information, featured clubs, and local images.</p><a class="btn btn-outline-secondary mt-2" href="/logout">Log out</a></div><div class="row g-4"><div class="col-lg-6"><section class="admin-card h-100"><p class="admin-card-label">Directory data</p><h2>Update all clubs</h2><p>Upload the CSV used for the main club directory.</p><form><input class="form-control" type="file" accept=".csv"><button class="btn admin-primary mt-3" type="button">Upload CSV</button></form></section></div><div class="col-lg-6"><section class="admin-card h-100"><p class="admin-card-label">Homepage feature data</p><h2>Update featured clubs</h2><p>Upload the CSV used for featured club content.</p><form><input class="form-control" type="file" accept=".csv"><button class="btn admin-primary mt-3" type="button">Upload CSV</button></form></section></div><div class="col-lg-6 delete-card-column"><section class="admin-card h-100"><p class="admin-card-label">Local assets</p><h2>Delete downloaded images</h2><p>Remove locally stored club images before downloading a fresh set.</p><div class="delete-form"><button class="btn btn-outline-danger mt-2" type="button">Delete images</button></div></section></div></div></main>';
    end_page();
    exit;
}

$category = trim($_GET['category'] ?? '');
$query = trim($_GET['q'] ?? '');
if ($category !== '') $query = $category;
if (str_starts_with($path, '/clubslist/')) $query = trim(urldecode(substr($path, strlen('/clubslist/'))));
$clubs = rows_from_csv(__DIR__ . '/static/data/clubs_information.csv');
$clubs = array_values(array_filter($clubs, function ($club) {
    if (($club['Sponsor Replied'] ?? '') !== 'True' || ($club['Added to Website'] ?? '') !== 'True') return false;
    return true;
}));

start_page();
echo '<main><section class="directory-header"><div class="container"><div class="header-copy"><p class="section-label">Walter Johnson High School</p><h1>Find your club.</h1><p class="intro">Browse student-led communities, activities, and interests across WJ.</p></div><form class="search-form" id="club-search"><label class="visually-hidden" for="query">Search clubs</label><input id="query" name="q" class="form-control" type="search" placeholder="Search by club name or interest"><label class="visually-hidden" for="category">Sort by category</label><select class="form-select category-filter" id="category" name="category"><option value="">All categories</option><option>Academic</option><option>Arts</option><option>Charity/Activism</option><option>Competitive</option><option>Culture</option><option>Dance</option><option>Games/Sports</option><option>Interest</option><option>Music</option><option>STEM</option></select></form><p class="result-count">Showing ' . count($clubs) . ' of ' . count($clubs) . ' clubs</p></div></section><section class="clubs-section"><div class="container"><div class="row g-4">';
foreach ($clubs as $club) {
    $image = '/static/' . ltrim($club['Image Path'] ?? 'images/unknown.png', '/');
    echo '<div class="col-lg-4 col-md-6 club-item" data-club-item data-search-text="' . e($club['Club Name'] . ' ' . $club['Purpose'] . ' ' . $club['Social Media Handles (optional)']) . '" data-category="' . e($club['Select the category for your club']) . '"><article class="club-card h-100"><div class="club-image-wrap"><img src="' . e($image) . '" alt="' . e($club['Club Name']) . '" loading="lazy"></div><div class="club-card-body"><h2>' . e($club['Club Name']) . '</h2><p class="club-purpose">' . e($club['Purpose']) . '</p><dl class="club-details"><div class="schedule-row"><dd>Meets ' . e($club['Select all the days of the week that your club meets']) . ' ' . e($club['Club Meeting Frequency']) . ' during ' . e(csv_value($club, 'When does your club meet?')) . '</dd></div><div><dt>Sponsor</dt><dd>' . e($club['Sponsor email address']) . '</dd></div></dl>' . (!empty($club['Social Media Handles (optional)']) ? '<div class="social-link">' . social_markup($club['Social Media Handles (optional)']) . '</div>' : '') . '</div></article></div>';
}
if (!$clubs) echo '<div class="col-12"><p class="empty-state">No clubs matched your search.</p></div>';
echo '</div></div></section></main>';
end_page();

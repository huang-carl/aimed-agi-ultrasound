<?php
// Contact form API endpoint
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit();
}

// Get POST data
$data = json_decode(file_get_contents('php://input'), true);

// Validate required fields
$required = ['name', 'phone'];
foreach ($required as $field) {
    if (empty($data[$field])) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => "缺少必填字段：$field"]);
        exit();
    }
}

// Save to file (simple storage)
$log_file = '/root/.openclaw/workspace/skytop-dept/sales/leads.csv';
$timestamp = date('Y-m-d H:i:s');
$name = $data['name'] ?? '';
$phone = $data['phone'] ?? '';
$company = $data['company'] ?? '';
$identity = $data['identity'] ?? '';
意向 = $data['意向'] ?? '';
$message = $data['message'] ?? '';

// CSV format
$csv_line = "$timestamp,$name,$phone,$company,$identity,$意向,$message\n";
file_put_contents($log_file, $csv_line, FILE_APPEND | LOCK_EX);

echo json_encode([
    'success' => true,
    'message' => '提交成功！我们将尽快与您联系',
    'data' => [
        'timestamp' => $timestamp,
        'name' => $name
    ]
]);

CREATE TABLE IF NOT EXISTS booking_requests (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    start_time DATETIME NOT NULL,
    duration_min INTEGER NOT NULL,
    timezone VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending_verification',
    ip VARCHAR(45) NOT NULL,
    calendar_event_id VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    decided_at DATETIME NULL,
    INDEX idx_status (status),
    INDEX idx_ip_created (ip, created_at)
);

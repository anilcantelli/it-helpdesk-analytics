CREATE DATABASE IF NOT EXISTS it_helpdesk_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE it_helpdesk_analytics;

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id               VARCHAR(20) PRIMARY KEY,
    created_at              DATETIME NOT NULL,
    customer_id             VARCHAR(20),
    customer_segment        VARCHAR(30),
    channel                 VARCHAR(30),
    product_area            VARCHAR(50),
    issue_type              VARCHAR(50),
    priority                VARCHAR(20),
    status                  VARCHAR(30),
    sla_plan                VARCHAR(20),
    resolution_time_hours   DECIMAL(10,2),
    reopened                BOOLEAN DEFAULT FALSE,
    customer_sentiment      VARCHAR(20),
    csat_score               TINYINT,
    has_attachment           BOOLEAN DEFAULT FALSE,
    platform                 VARCHAR(20),
    region                    VARCHAR(10),
    initial_message           TEXT,
    agent_first_reply          TEXT,
    resolution_summary         TEXT,
    is_closed                 BOOLEAN DEFAULT FALSE,
    is_rated                  BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_tickets_issue_type ON tickets (issue_type);
CREATE INDEX idx_tickets_created_at ON tickets (created_at);
CREATE INDEX idx_tickets_priority ON tickets (priority);
CREATE INDEX idx_tickets_sla_plan ON tickets (sla_plan);

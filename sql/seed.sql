-- Seed initial records if not already present
INSERT INTO employees (name, email, role, department, salary, status)
VALUES 
    ('Alex Johnson', 'alex.j@company.com', 'Senior DevOps Engineer', 'DevOps & Cloud', 95000.00, 'Active'),
    ('Priya Sharma', 'priya.s@company.com', 'Cloud Infrastructure Architect', 'DevOps & Cloud', 115000.00, 'Active'),
    ('Marcus Chen', 'marcus.c@company.com', 'Full Stack Developer', 'Engineering', 88000.00, 'Active'),
    ('Elena Rostova', 'elena.r@company.com', 'Site Reliability Engineer', 'DevOps & Cloud', 102000.00, 'Active')
ON CONFLICT (email) DO NOTHING;

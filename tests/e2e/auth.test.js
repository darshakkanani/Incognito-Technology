/**
 * End-to-End Authentication Tests
 * Incognito Technology Healthcare Platform
 */

const { test, expect } = require('@playwright/test');

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
  });

  test('should display landing page correctly', async ({ page }) => {
    // Check if landing page loads
    await expect(page).toHaveTitle(/Incognito Technology/);
    
    // Check for key elements
    await expect(page.locator('h1')).toContainText('Secure Healthcare');
    await expect(page.locator('[data-testid="login-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="register-button"]')).toBeVisible();
  });

  test('should navigate to login page', async ({ page }) => {
    // Click login button
    await page.click('[data-testid="login-button"]');
    
    // Verify navigation to login page
    await expect(page).toHaveURL(/.*\/login/);
    await expect(page.locator('h2')).toContainText('Sign In');
    
    // Check form elements
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for empty login form', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Submit empty form
    await page.click('button[type="submit"]');
    
    // Check for validation errors
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Fill form with invalid credentials
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check for error message
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-error"]')).toContainText('Invalid email or password');
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Fill form with valid credentials
    await page.fill('input[type="email"]', 'doctor@example.com');
    await page.fill('input[type="password"]', 'SecurePass123!');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for navigation to dashboard
    await page.waitForURL(/.*\/dashboard/);
    
    // Verify successful login
    await expect(page).toHaveURL(/.*\/dashboard\/doctor/);
    await expect(page.locator('h1')).toContainText('Doctor Dashboard');
  });

  test('should navigate to registration page', async ({ page }) => {
    // Click register button
    await page.click('[data-testid="register-button"]');
    
    // Verify navigation to register page
    await expect(page).toHaveURL(/.*\/register/);
    await expect(page.locator('h2')).toContainText('Create Account');
    
    // Check form elements
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('input[name="firstName"]')).toBeVisible();
    await expect(page.locator('input[name="lastName"]')).toBeVisible();
    await expect(page.locator('select[name="role"]')).toBeVisible();
  });

  test('should validate registration form', async ({ page }) => {
    // Navigate to registration page
    await page.goto('/register');
    
    // Submit empty form
    await page.click('button[type="submit"]');
    
    // Check for validation errors
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="firstName-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="lastName-error"]')).toBeVisible();
  });

  test('should validate password strength', async ({ page }) => {
    // Navigate to registration page
    await page.goto('/register');
    
    // Fill form with weak password
    await page.fill('input[name="email"]', 'newuser@example.com');
    await page.fill('input[name="password"]', 'weak');
    await page.fill('input[name="firstName"]', 'John');
    await page.fill('input[name="lastName"]', 'Doe');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check for password strength error
    await expect(page.locator('[data-testid="password-error"]')).toContainText('Password must be at least 8 characters');
  });

  test('should successfully register new user', async ({ page }) => {
    // Navigate to registration page
    await page.goto('/register');
    
    // Fill form with valid data
    await page.fill('input[name="email"]', `newuser${Date.now()}@example.com`);
    await page.fill('input[name="password"]', 'SecurePass123!');
    await page.fill('input[name="firstName"]', 'John');
    await page.fill('input[name="lastName"]', 'Doe');
    await page.selectOption('select[name="role"]', 'patient');
    await page.check('input[name="termsAccepted"]');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for success message or redirect
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'doctor@example.com');
    await page.fill('input[type="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await page.waitForURL(/.*\/dashboard/);
    
    // Click logout button
    await page.click('[data-testid="logout-button"]');
    
    // Verify redirect to home page
    await expect(page).toHaveURL('http://localhost:3000/');
    await expect(page.locator('[data-testid="login-button"]')).toBeVisible();
  });

  test('should handle session timeout', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'doctor@example.com');
    await page.fill('input[type="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await page.waitForURL(/.*\/dashboard/);
    
    // Simulate session timeout by clearing localStorage
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // Try to access protected resource
    await page.reload();
    
    // Should be redirected to login
    await expect(page).toHaveURL(/.*\/login/);
  });

  test('should prevent access to protected routes without authentication', async ({ page }) => {
    // Try to access dashboard directly
    await page.goto('/dashboard/doctor');
    
    // Should be redirected to login
    await expect(page).toHaveURL(/.*\/login/);
    
    // Check for authentication required message
    await expect(page.locator('[data-testid="auth-required"]')).toBeVisible();
  });
});

test.describe('Role-Based Access Control', () => {
  test('should redirect doctor to doctor dashboard', async ({ page }) => {
    // Login as doctor
    await page.goto('/login');
    await page.fill('input[type="email"]', 'doctor@example.com');
    await page.fill('input[type="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');
    
    // Should redirect to doctor dashboard
    await expect(page).toHaveURL(/.*\/dashboard\/doctor/);
    await expect(page.locator('h1')).toContainText('Doctor Dashboard');
  });

  test('should redirect patient to patient dashboard', async ({ page }) => {
    // Login as patient
    await page.goto('/login');
    await page.fill('input[type="email"]', 'patient@example.com');
    await page.fill('input[type="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');
    
    // Should redirect to patient dashboard
    await expect(page).toHaveURL(/.*\/dashboard\/patient/);
    await expect(page.locator('h1')).toContainText('Patient Dashboard');
  });

  test('should prevent unauthorized role access', async ({ page }) => {
    // Login as patient
    await page.goto('/login');
    await page.fill('input[type="email"]', 'patient@example.com');
    await page.fill('input[type="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');
    
    // Try to access doctor dashboard
    await page.goto('/dashboard/doctor');
    
    // Should be denied access
    await expect(page.locator('[data-testid="access-denied"]')).toBeVisible();
  });
});

test.describe('Security Features', () => {
  test('should implement rate limiting on login attempts', async ({ page }) => {
    await page.goto('/login');
    
    // Make multiple failed login attempts
    for (let i = 0; i < 6; i++) {
      await page.fill('input[type="email"]', 'test@example.com');
      await page.fill('input[type="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');
      await page.waitForTimeout(1000);
    }
    
    // Should show rate limit error
    await expect(page.locator('[data-testid="rate-limit-error"]')).toBeVisible();
  });

  test('should show password strength indicator', async ({ page }) => {
    await page.goto('/register');
    
    // Type weak password
    await page.fill('input[name="password"]', 'weak');
    await expect(page.locator('[data-testid="password-strength"]')).toContainText('Weak');
    
    // Type strong password
    await page.fill('input[name="password"]', 'StrongPass123!');
    await expect(page.locator('[data-testid="password-strength"]')).toContainText('Strong');
  });

  test('should implement CSRF protection', async ({ page }) => {
    // This test would verify CSRF token implementation
    await page.goto('/login');
    
    // Check for CSRF token in form
    const csrfToken = await page.locator('input[name="_token"]').getAttribute('value');
    expect(csrfToken).toBeTruthy();
  });
});

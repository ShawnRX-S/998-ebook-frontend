# 998 Privacy-Preserving Ebook Platform (Frontend)

This is the Vue3 frontend of the privacy-preserving ebook store demo.

---

I have led the Phase 2 development, evolving the platform from a basic template into a secure, audit-ready ecosystem through four critical stages:

### Phase 1: UI & Framework Foundation
* **Element Plus Integration:** Replaced legacy HTML controls with a professional Vue UI component library for a commercial-grade user experience.
* **Routing System:** Architected a robust `vue-router` configuration for seamless navigation between Shop, Cart, and Admin modules.

### Phase 2: Security & Privacy Integration
* **Cryptographic Layer:** Integrated **AES-256 (CryptoJS)** for industrial-strength encryption.
* **Data Masking:** Implemented masking logic for sensitive metadata (e.g., Book Titles) to prevent unauthorized data leakage.
* **Verification Module:** Developed an "Encryption Sandbox" to verify the "Plaintext-in, Ciphertext-out" workflow.

### Phase 3: Administrative Control & Auditing
* **Admin Dashboard:** Built a comprehensive management console using `el-container` layout with real-time data visualization (Book count, User activity, Security status).
* **Privacy Audit System:** Implemented **GDPR-compliant auditing**. Every change to a security policy (e.g., toggling encryption) generates a timestamped audit log for traceability.

### Phase 4: RBAC & Security Guarding
* **Identity-Driven Auth:** Replaced manual role selection with a secure **Role-Based Access Control (RBAC)** logic using `authStore.js`.
* **Separation of Duties (SoD):** Enforced strict logical isolation between Administrative and Customer interfaces.
* **Navigation Guards:** Implemented **Vue Router Guards** to intercept unauthorized access (e.g., blocking non-admins from the backend and unauthenticated users from the cart).
* **Root Account Initialization:** Provisioned a secure root administrator (`admin/admin123`) for system bootstrapping.

---

## 🛠️ Tech Stack
* **Frontend:** Vue 3 (Composition API), Vite, Element Plus
* **Security:** CryptoJS (AES-256), Navigation Guards
* **State Management:** Reactive Store (Composition API) & LocalStorage Sync

---

## 🏃‍♂️ Quick Start
1. `npm install`
2. `npm run dev`
3. Log in as Admin: `admin / admin123` to manage privacy policies.
## Project Background

This project is part of the 998 privacy-preserving ebook platform research project.  
The frontend is implemented with Vue3 and designed to integrate with backend cryptographic protocols such as Oblivious Transfer (OT) to enable privacy-preserving digital purchases.


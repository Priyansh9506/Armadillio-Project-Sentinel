# 🧠 Project Sentinel: Architecture Thought Process

This document outlines the core architectural decisions made by Team Armadillo for Project Sentinel. It is designed to explain our technology choices during one-on-one discussions with the hackathon jury and team members.

---

## The Core Question
**"Why did we choose React + FastAPI instead of full-stack Next.js or React + Express.js?"**

---

## 1. Why FastAPI instead of Express.js?

The core innovation of Project Sentinel is the **Trust Score Engine** and **Behavioral Biometrics**.

*   **The Machine Learning Ecosystem:** In a production environment (and as per our development roadmap), Sentinel relies heavily on Machine Learning models to detect fraud. We use *Isolation Forest* (via `scikit-learn`) for keystroke anomaly detection and *XGBoost* for analyzing transaction fraud. **Python is the undisputed industry standard for Data Science and AI/ML.**
*   **The Express.js Problem:** If we had chosen Express.js (Node.js) for our backend, we would not be able to run these Python-based ML libraries natively. We would have been forced to use clunky JavaScript workarounds, or we would have had to build a separate Python microservice anyway, adding unnecessary complexity to the architecture.
*   **Why FastAPI is Perfect:** FastAPI is built natively in Python. This means we can import `scikit-learn`, `numpy`, and `pandas` directly alongside our API routes. Furthermore, FastAPI is incredibly fast, provides automatic OpenAPI (Swagger) documentation out of the box, and is currently the industry standard for modern ML-based backends.

## 2. Why React (Vite) instead of Next.js?

While Next.js is an incredible framework, its primary superpowers are **Server-Side Rendering (SSR)** and SEO optimization. For an internal banking security product like Project Sentinel, SSR actually works against us:

*   **Heavy Client-Side Logic:** Sentinel requires a custom Javascript SDK running continuously in the browser. It tracks keystroke dynamics (capturing exact `keyup` and `keydown` timestamps) and mouse velocities in real-time. This is purely client-side logic. Next.js can struggle with heavy client-side SDKs due to "hydration" mismatches between the server and the browser.
*   **Next.js Backend is Node.js:** Next.js has built-in API routes, but they run on a Node.js environment. If we attempted to use Next.js as our full-stack solution, we would hit the exact same problem as Express.js—we would have zero native Python ML support.
*   **The Vite + React Advantage:** Using a Vite-powered Single Page Application (SPA) provides a perfectly decoupled architecture. React handles the beautiful UI, state management, and the telemetry SDK purely in the browser. It then sends clean, lightweight JSON payloads to our FastAPI backend, which handles the heavy mathematical lifting and Neo4j graph database queries.

---

## The Final Verdict: "The Data Science Stack"

The **React + FastAPI** combination is widely recognized in the industry as the modern **"Data Science / AI Stack"**. It is the exact same architectural pattern used by companies like OpenAI, Netflix, and Uber for their internal dashboards and ML products.

**What this tells the Jury:** 
*"We didn't just string together a basic web application; we intentionally architected a robust, decoupled system designed specifically to handle real-time machine learning pipelines and complex behavioral biometrics."*

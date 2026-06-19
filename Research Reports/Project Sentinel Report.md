# **Project Sentinel**

## **Next-Gen Identity Trust & Omnichannel Security Framework**

**Prepared for:** Bank of Baroda Hackathon 2026 | **Theme:** Cybersecurity & Fraud

## **1\. Executive Summary**

Traditional banking security relies on binary, point-in-time checks (e.g., entering a password or OTP). However, modern cyber fraud—including Account Takeovers (ATO), synthetic identities, and insider threats—easily bypasses these static defenses using social engineering, malware, or emulators.

**Project Sentinel** is a "Continuous Identity Trust" framework. It shifts the paradigm from *"Are you who you say you are at login?"* to *"Are you behaving like yourself throughout the entire session?"* By fusing Behavioral Analytics, Graph Memory for fraud ring detection, and Role-Based Anomaly Detection, Sentinel provides a frictionless experience for legitimate users while creating an insurmountable barrier for fraudsters and malicious insiders.

## **2\. Core Innovations ("Out-of-the-Box" Features)**

### **A. Invisible Behavioral Biometrics**

Analyzes *how* a user interacts with their device. Tracks keystroke flight times, swipe pressure, typing cadence, and phone gyroscope angles. If a fraudster steals a session token, their physical interaction rhythm will fail to match the legitimate user's profile.

### **B. Graph Memory (Fraud Ring Detection)**

Instead of checking accounts in isolation, we map IP subnets, MAC addresses, and transaction histories into a Graph Database (Neo4j). This identifies hidden "Mule Account" clusters—e.g., 50 different accounts being accessed from the same IMEI device ID or VPN IP range.

### **C. Deep API Payload & Device Scrutiny**

Analyzes the metadata of the API request itself. We detect iOS Jailbreaks, Android Rooting, FRIDA instrumentation, GPS spoofing, and the presence of emulators (like Bluestacks or Genymotion) commonly used by bot farms to automate fraudulent onboardings.

### **D. Adaptive Contextual MFA**

Replaces annoying, constant OTPs. The system assigns a real-time "Trust Score". If the score drops (e.g., weird typing speed \+ new location), the system triggers a "Step-Up Challenge" (Facial Liveness or push notification). High trust \= Zero friction.

## **3\. The "Step-Up Challenge" UX (Handling the Compromised Screen)**

A critical aspect of Project Sentinel is how it handles a compromised session without panicking the legitimate user. If the device is snatched while unlocked (a sudden change in accelerometer data and swipe pressure), the screen response is immediate but elegant:

1. **The Silent Lock:** The screen does not show a scary "HACKER DETECTED" alert. Instead, it instantly blurs the banking dashboard and displays a polite, branded prompt: *"For your security, your session timed out. Please verify your identity to continue."*  
2. **Contextual Liveness Check:** Because the system suspects a physical device takeover, a text-based OTP is useless (the thief has the phone). The system forces a **Facial Liveness Check** using the front camera, requiring a specific head movement (e.g., "Look left").  
3. **Transaction Freeze:** In the background, API write-access is temporarily revoked. Even if the thief bypasses the UI, backend transfers are blocked until the Trust Score recovers.

## **4\. 360° Role-Specific Anomaly Detection**

Fraud doesn't just happen from the outside. Project Sentinel monitors the entire ecosystem, applying different behavioral models based on the entity's role.

| **Role** | **Monitored Behaviors & Context** | **Triggers for Fraud / Compromise** |

| **Retail / Corporate User** | Spending vs. Fraud patterns, typical transaction times, geolocations, usual payees. | Sudden high-velocity transfers to new payees, access via known VPN/TOR nodes, drastic change in device orientation/typing speed (Bot/ATO indicator). |

| **Banker / Teller** | Standard Operating Procedures (SOPs), typical branch hours, standard query volume. | Accessing customer PII outside of branch hours, querying high-net-worth accounts unprompted by a support ticket, sudden changes in wire-transfer approval rates. |

| **IT Admin / Superuser** | Database access patterns, bulk data extraction, configuration changes. | Downloading bulk customer data via API at 3:00 AM, disabling security logging, creating "ghost" admin accounts (Insider Threat / Compromised Creds). |

## **5\. Privacy, Compliance & Edge AI**

For a framework like Sentinel to be viable for the Bank of Baroda, it must adhere strictly to the Digital Personal Data Protection Act (DPDP), 2023\.

* **Edge Processing:** Behavioral keystroke dynamics and gyroscope telemetry are processed **on the device (Edge AI)** using a lightweight model like TensorFlow Lite. Only an anonymized mathematical vector (the "Trust Score"), never the raw keystrokes or PIN inputs, is sent to the bank's servers.  
* **Federated Learning:** The central model learns about new global fraud patterns across the banking network without ever extracting Personally Identifiable Information (PII) from individual devices.

## **6\. System Architecture & Workflow Diagram**

The following diagram illustrates the real-time, low-latency data pipeline that evaluates every transaction and session interaction.

graph TD  
    subgraph Client Layer  
        A\[iOS / Android App\] \--\>|Deep Payload \+ Biometrics| API  
        B\[Web Portal\] \--\>|Keystrokes \+ Browser Fingerprint| API  
        C\[Admin Dashboard\] \--\>|Audit Logs \+ Queries| API  
    end

    subgraph API Gateway & Edge  
        API\[API Gateway Layer\]  
        API \--\>|Extract Metadata| D(Device & Environment Check)  
        D \--\>|Flag Emulators / Root| Engine  
    end

    subgraph Core Intelligence Engine  
        Engine{Real-Time Risk Scoring Engine}  
          
        Engine \<--\>|Verify Rhythm| Model1\[Behavioral Biometric ML\]  
        Engine \<--\>|Check Connections| Graph\[(Neo4j Graph Memory)\]  
        Engine \<--\>|Spend vs History| Model2\[Financial Anomaly ML\]  
        Engine \<--\>|SOP Deviation| Model3\[Insider Threat Monitor\]  
    end

    subgraph Decision Matrix  
        Engine \--\>|Calculate Continuous Trust Score| Matrix{Decision Gateway}  
        Matrix \--\>|Score \> 90| Allow\[✅ Allow Frictionless Action\]  
        Matrix \--\>|Score 60 \- 89| StepUp\[⚠️ Trigger Contextual MFA / Liveness\]  
        Matrix \--\>|Score \< 60| Block\[🚫 Block & Alert SecOps\]  
    end  
      
    StepUp \-.-\>|MFA Passed| Allow  
    StepUp \-.-\>|MFA Failed| Block

## **7\. Proposed Technology Stack**

To build the hackathon prototype, we recommend the following modern, scalable stack:

* **Frontend (Mobile/Web):** React Native or Flutter (allows native device hooks for gyroscope/touch pressure capture).  
* **Backend Gateway:** Node.js or GoLang for low-latency API handling.  
* **Graph Intelligence:** Neo4j (for mapping complex fraud rings and node relationships).  
* **AI/ML Engine:** Python (Scikit-Learn for anomaly detection, TensorFlow Lite for on-device behavioral biometrics).  
* **Infrastructure:** Docker containerization to ensure smooth deployment during the jury presentation.

## **8\. Business Impact & ROI for Bank of Baroda**

1. **Drastic Reduction in SMS OTP Costs:** By relying on silent behavioral authentication, the bank can eliminate millions of redundant SMS OTPs sent for routine logins, saving significant operational costs.  
2. **Zero-Day Fraud Mitigation:** Graph memory catches synthetic identity rings before they mature, saving the bank from massive coordinated multi-account loan defaults.  
3. **Enhanced Customer Experience:** Legitimate customers experience zero friction. They simply open the app and transact, increasing app usage and digital banking adoption.

## **9\. Recommended Datasets for Model Training**

To implement these features effectively for the prototype, the following public datasets and research references can be utilized for training the ML and Graph models:

### **A. Spending vs. Fraud & Anomaly Detection**

* **IEEE-CIS Fraud Detection Dataset (Kaggle):** Excellent for benchmarking machine learning models on real-world e-commerce and transaction data, including device types and IP metadata.  
* **PaySim Synthetic Financial Dataset:** Simulates mobile money transactions based on a sample of real transactions. Perfect for building Graph Databases to visualize money laundering and mule accounts.

### **B. Behavioral Biometrics**

* **Balabit Mouse Dynamics Challenge:** Dataset containing mouse movement data for identifying compromised accounts based on cursor behavior.  
* **Clarkson University Keystroke Dataset:** Continuous typing data ideal for training recurrent neural networks (RNNs) to verify user identity continuously.

### **C. Insider Threat & Admin Anomalies**

* **CERT Insider Threat Dataset (Carnegie Mellon):** Synthetic datasets that simulate enterprise environments, tracking logon/logoff times, email metadata, and file access (perfect for training the Banker/Admin anomaly engine).

### **💡 Hackathon Strategy Note**

For the prototype submission, focus heavily on the **Graph Memory** and **Behavioral Auth**. Building a mock mobile app that immediately blurs and locks the **screen** when handed to a "stranger" (due to radically different swiping speed and phone angle), coupled with a Neo4j dashboard showing interconnected fraudulent accounts, will provide the interactive "Wow\!" factor needed to win the cybersecurity domain.
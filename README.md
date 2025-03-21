# Identity Reconciliation API

  **Overview
The **Identity Reconciliation API** is a FastAPI-based microservice designed to identify and link duplicate customer contacts. When users sign up using different emails or phone numbers, this API ensures that all related accounts are grouped under a **primary contact**, making data management more efficient.

## Features
-  Accepts **email and phone numbers** as input  
-  Searches for **existing contacts** in the database  
-  Links duplicate accounts under a **single primary contact**  
-  Returns all linked **emails and phone numbers**  

---

## Installation Guide

  ** Clone the Repository**
To get started, clone this repository and navigate into the project folder:
```sh
git clone https://github.com/eduru-shiva/identity-reconciliation.git
cd identity-reconciliation

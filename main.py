from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Contact

# ✅ Define FastAPI application BEFORE using @app
app = FastAPI()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Identity Reconciliation API is running"}

@app.post("/identify")
def identify_contact(email: str = None, phoneNumber: str = None, db: Session = Depends(get_db)):
    if not email and not phoneNumber:
        raise HTTPException(status_code=400, detail="At least one of email or phoneNumber is required")

    # Find all contacts matching the email or phone number
    existing_contacts = db.query(Contact).filter(
        (Contact.email == email) | (Contact.phoneNumber == phoneNumber)
    ).all()

    if existing_contacts:
        # Identify the oldest (primary) contact
        primary_contact = min(existing_contacts, key=lambda c: c.id)

        # Store linked contacts
        all_contacts = set(existing_contacts)
        secondary_contacts = []

        # Convert existing contacts into secondary contacts if needed
        for contact in existing_contacts:
            if contact.id != primary_contact.id:
                if contact.linkPrecedence != "secondary":
                    contact.linkPrecedence = "secondary"
                    contact.linkedId = primary_contact.id
                    db.commit()
                secondary_contacts.append(contact.id)

        # 🚀 **Force insert new contact if not found**
        if not any(c.email == email and c.phoneNumber == phoneNumber for c in existing_contacts):
            new_secondary = Contact(email=email, phoneNumber=phoneNumber, linkPrecedence="secondary", linkedId=primary_contact.id)
            db.add(new_secondary)
            db.commit()
            db.refresh(new_secondary)
            secondary_contacts.append(new_secondary.id)

        return {
            "primaryContactId": primary_contact.id,
            "emails": list(set([c.email for c in all_contacts if c.email] + ([email] if email else []))),
            "phoneNumbers": list(set([c.phoneNumber for c in all_contacts if c.phoneNumber] + ([phoneNumber] if phoneNumber else []))),
            "secondaryContactIds": secondary_contacts,
        }

    # 🚀 If no existing contact is found, create a new primary contact
    new_contact = Contact(email=email, phoneNumber=phoneNumber, linkPrecedence="primary")
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return {
        "primaryContactId": new_contact.id,
        "emails": [new_contact.email] if new_contact.email else [],
        "phoneNumbers": [new_contact.phoneNumber] if new_contact.phoneNumber else [],
        "secondaryContactIds": [],
    }

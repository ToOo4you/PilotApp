\# Pilot Architecture



\## Overview



Pilot is designed as an AI-powered workforce operations platform for companies that manage people, vehicles, equipment, customers, and jobs.



\## Main Parts



\### Backend



The backend is built with FastAPI and Python.



Responsibilities:



\- API endpoints

\- User authentication

\- Company accounts

\- Database access

\- Business logic

\- AI integrations



\### Database



Pilot currently uses SQLite for development.



Later, Pilot will use PostgreSQL for production.



Core tables:



\- Companies

\- Users

\- Employees

\- Customers

\- Vehicles

\- Equipment

\- Jobs

\- Dispatches

\- GPS Locations

\- Invoices

\- Payments



\### Web Dashboard



The web dashboard will be used by owners, managers, and dispatchers.



It will include:



\- Company dashboard

\- Dispatch board

\- Live map

\- Employees

\- Vehicles

\- Customers

\- Jobs

\- Reports



\### Mobile App



The mobile app will be used by drivers, technicians, and field workers.



It will include:



\- Assigned jobs

\- Navigation

\- Status updates

\- Photo uploads

\- Signatures

\- Messaging



\### AI Layer



The AI layer will help users automate operations.



Examples:



\- Assign the closest worker

\- Summarize daily activity

\- Create invoices

\- Optimize routes

\- Warn about delays or problems



\## Design Principle



Every important record belongs to a company.



This keeps each company's data separate and secure.



Example:



Company

\- Users

\- Employees

\- Vehicles

\- Customers

\- Jobs



\## Long-Term Goal



Pilot should be built as a scalable platform that can support many industries, including towing, trucking, construction, utilities, public safety, and field services.


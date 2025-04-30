# NYUAD Bazaar -  Instructions on how to run the app

## Frontend
When running on frontend, you'll get a message like
```
You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://10.228.253.234:3000
```
Run the 'on your network' option on your phone to see app view
```
cd frontend
npm install (ONLY AFTER A PULL FOR THE FIRST TIME - ONLY NEEDED ONCE)
npm start
```
## Backend
 Be in the root directory
 ```
uvicorn backend.main:app --reload
 ```

---
# Reservation API Endpoints

---

## POST `/listings/{item_id}/request`  
**Request Reservation**  
Allows a user (buyer) to request a reservation for a listing.  
A reservation is valid for 7 days and automatically expires if not confirmed by the seller. The listing status remains "available".

**Query Parameters:**
- `user_id` (string): ID of the buyer requesting the reservation.

**Responses:**
- `200 OK` – Reservation added successfully.
- `404 Not Found` – Listing does not exist.

---

## POST `/listings/{item_id}/confirm`  
**Confirm Reservation**  
Allows the seller to confirm a specific buyer’s reservation.  
Upon confirmation:
- Listing status updates to `"reserved"`.
- All other reservations remain `"pending"`.

**Query Parameters:**
- `buyer_id` (string): ID of the buyer whose reservation is being confirmed.

**Responses:**
- `200 OK` – Reservation confirmed successfully.
- `404 Not Found` – Listing or reservation does not exist.

---

## GET `/listings/{item_id}/reservations`  
**Get Reservations**  
Returns all active reservation requests for a listing.

- If listing status is `"reserved"`, returns only the confirmed reservation (with buyer’s phone).
- If status is `"available"`, returns all non-expired pending requests.

**Responses:**
- `200 OK` – Returns list of reservations with:
  - `buyer_id`
  - `requested_at`
  - `expires_at` (if pending)
  - `status` ("pending" or "confirmed")
  - `buyer_phone` (if confirmed)

---

## DELETE `/listings/{item_id}/cancel_reservation`  
**Cancel Reservation Request**  
Cancels a reservation request (can be initiated by buyer or seller).

- If listing was `"reserved"`, it becomes `"available"` and other reservations reset to 7 days.
- If listing was `"available"`, request is simply removed.

**Query Parameters:**
- `buyer_id` (string): ID of the buyer whose reservation is being cancelled.

**Responses:**
- `200 OK` – Reservation cancelled.
- `404 Not Found` – Listing or reservation does not exist.

---

## POST `/listings/{item_id}/sold`  
**Mark Listing As Sold**  
Marks a listing as `"sold"`.

- All reservation requests are removed.
- Listing status is updated to `"sold"`.

**Responses:**
- `200 OK` – Listing marked as sold.
- `404 Not Found` – Listing does not exist.

---

## GET `/user/{user_id}/get_my_requests`  
**Get Listings Requested by User (My Reservation Requests)**  
Retrieves all listings where the specified user has submitted a reservation request.

- Pending reservations include expiration date.
- Confirmed reservations include seller’s phone number.
- Expired reservations are excluded.

**Path Parameters:**
- `user_id` (string): ID of the buyer.

**Responses:**
- `200 OK` – Returns list of reservations with:
  - `listing_id`
  - `title`
  - `seller_id`
  - `requested_at`
  - `expires_at` (only for pending)
  - `status` ("pending" or "confirmed")
  - `seller_phone` (only for confirmed)
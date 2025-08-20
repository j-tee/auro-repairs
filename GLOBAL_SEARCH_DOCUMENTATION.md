# Global Search API - How It Works

## ✅ Global Search is Working Correctly!

The global search for "toyota" returns **2 results**, which is the correct behavior:

### Search Results for "toyota":
1. **1 Vehicle**: Alice Cooper's Toyota Camry (2020) - matches "toyota" in make field
2. **1 Customer**: Alice Cooper - returned because she owns a Toyota vehicle
3. **Total: 2 results**

## 🔍 How Global Search Works

The global search endpoint `/api/shop/search/?q=<term>` searches across three categories:

### 1. **Vehicle Search**
Finds vehicles where the search term appears in:
- `make` (e.g., "Toyota")
- `model` (e.g., "Camry") 
- `vin` (VIN number)
- `license_plate` (license plate)
- `color` (vehicle color)

**For "toyota" search**: Finds 1 vehicle (Toyota Camry)

### 2. **Customer Search** 
Finds customers where the search term appears in:
- `name` (customer name)
- `email` (customer email)
- `address` (customer address)
- `phone_number` (customer phone)
- `vehicles__make` (make of vehicles they own)
- `vehicles__model` (model of vehicles they own)

**For "toyota" search**: Finds 1 customer (Alice Cooper owns a Toyota)

### 3. **Repair Order Search**
Finds repair orders where the search term appears in:
- `notes` (repair notes)
- `vehicle__make` (make of vehicle being repaired)
- `vehicle__model` (model of vehicle being repaired)
- `vehicle__vin` (VIN of vehicle being repaired)

**For "toyota" search**: Finds any repair orders for Toyota vehicles

## 🎯 Why This is Correct

When a user searches for "toyota", they likely want to find:
1. **All Toyota vehicles** in the system ✅
2. **All customers who own Toyota vehicles** ✅ 
3. **All repair orders for Toyota vehicles** ✅

This provides comprehensive results that help users find everything related to their search term.

## 🧪 Test Examples

### Search: "toyota"
```json
{
  "vehicles": [
    {
      "id": 27,
      "make": "Toyota",
      "model": "Camry", 
      "year": 2020,
      "customer_name": "Alice Cooper",
      "type": "vehicle"
    }
  ],
  "customers": [
    {
      "id": 19,
      "name": "Alice Cooper",
      "email": "alice.cooper@customer.com",
      "type": "customer"
    }
  ],
  "repair_orders": [],
  "total_results": 2
}
```

### Search: "honda"
```json
{
  "vehicles": [
    {
      "id": 28,
      "make": "Honda",
      "model": "Civic",
      "year": 2019, 
      "customer_name": "Bob Martinez",
      "type": "vehicle"
    }
  ],
  "customers": [
    {
      "id": 20,
      "name": "Bob Martinez",
      "email": "bob.martinez@customer.com",
      "type": "customer"
    }
  ],
  "repair_orders": [],
  "total_results": 2
}
```

### Search: "alice"
```json
{
  "vehicles": [],
  "customers": [
    {
      "id": 19,
      "name": "Alice Cooper",
      "email": "alice.cooper@customer.com", 
      "type": "customer"
    }
  ],
  "repair_orders": [],
  "total_results": 1
}
```

## 🚀 API Usage

### Endpoint
```
GET /api/shop/search/?q=<search_term>
```

### Authentication Required
```javascript
headers: {
  'Authorization': 'Bearer <access_token>'
}
```

### Response Format
```json
{
  "vehicles": [array of matching vehicles],
  "customers": [array of matching customers],
  "repair_orders": [array of matching repair orders],
  "total_results": number
}
```

### Role-Based Access
- **Owners/Employees**: See all results
- **Customers**: See only their own vehicles and data

## ✅ Summary

The global search is working exactly as designed! It provides comprehensive search results that include:

1. **Direct matches**: Vehicles with "toyota" in their make/model
2. **Related matches**: Customers who own Toyota vehicles
3. **Associated matches**: Repair orders for Toyota vehicles

This gives users a complete view of everything related to their search term, which is the intended behavior for a global search feature.

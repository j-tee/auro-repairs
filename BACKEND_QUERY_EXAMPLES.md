# 🔍 Backend Query Examples - Accurate Search Results

**For Frontend Developer Reference**: These are the exact backend queries that return correct results. Compare these with your frontend API calls to identify discrepancies.

---

## 🎯 **Working Backend Queries**

### 1. **Vehicle Search Endpoint** ✅
**URL**: `/api/shop/vehicles/?search=toyota`

**Backend Django Query**:
```python
# In VehicleViewSet - this is what actually executes
from django.db.models import Q
from shop.models import Vehicle

# Search fields configured in ViewSet
search_fields = ["make", "model", "vin", "license_plate", "color"]

# DjangoFilterBackend creates this query automatically
vehicles = Vehicle.objects.filter(
    Q(make__icontains='toyota') |
    Q(model__icontains='toyota') |
    Q(vin__icontains='toyota') |
    Q(license_plate__icontains='toyota') |
    Q(color__icontains='toyota')
).select_related('customer')

# Result: 1 vehicle (Toyota Camry)
```

**Equivalent SQL Query**:
```sql
SELECT v.*, c.name as customer_name, c.email as customer_email 
FROM shop_vehicle v 
LEFT JOIN shop_customer c ON v.customer_id = c.id
WHERE LOWER(v.make) LIKE LOWER('%toyota%')
   OR LOWER(v.model) LIKE LOWER('%toyota%')
   OR LOWER(v.vin) LIKE LOWER('%toyota%')
   OR LOWER(v.license_plate) LIKE LOWER('%toyota%')
   OR LOWER(v.color) LIKE LOWER('%toyota%');
```

**Actual API Response**:
```json
[
  {
    "id": 27,
    "make": "Toyota",
    "model": "Camry",
    "year": 2020,
    "vin": "1HGBH41JXMN118133",
    "license_plate": "ABC-5189",
    "color": "Silver",
    "customer": {
      "id": 19,
      "name": "Alice Cooper",
      "phone_number": "(555) 714-5422",
      "email": "alice.cooper@customer.com",
      "address": "123 Elm St, Springfield, NY 10001"
    },
    "customer_name": "Alice Cooper",
    "customer_email": "alice.cooper@customer.com",
    "customer_phone": "(555) 714-5422"
  }
]
```

---

### 2. **Global Search Endpoint** ✅
**URL**: `/api/shop/search/?q=toyota`

**Backend Django Query**:
```python
# In global_search function - shop/views.py lines 83-120
from django.db.models import Q
from shop.models import Vehicle, Customer, RepairOrder

search_query = 'toyota'

# Vehicle search (same as above)
vehicles = Vehicle.objects.filter(
    Q(make__icontains=search_query) |
    Q(model__icontains=search_query) |
    Q(vin__icontains=search_query) |
    Q(license_plate__icontains=search_query) |
    Q(color__icontains=search_query)
).select_related('customer')

# Customer search (includes customers who own matching vehicles)
customers = Customer.objects.filter(
    Q(name__icontains=search_query) |
    Q(email__icontains=search_query) |
    Q(address__icontains=search_query) |
    Q(phone_number__icontains=search_query) |
    Q(vehicles__make__icontains=search_query) |
    Q(vehicles__model__icontains=search_query)
).distinct()

# Repair order search
repair_orders = RepairOrder.objects.filter(
    Q(notes__icontains=search_query) |
    Q(vehicle__make__icontains=search_query) |
    Q(vehicle__model__icontains=search_query) |
    Q(vehicle__vin__icontains=search_query)
).select_related('vehicle', 'vehicle__customer')
```

**Actual API Response**:
```json
{
  "vehicles": [
    {
      "id": 27,
      "make": "Toyota",
      "model": "Camry",
      "year": 2020,
      "vin": "1HGBH41JXMN118133",
      "license_plate": "ABC-5189",
      "color": "Silver",
      "customer_name": "Alice Cooper",
      "customer_email": "alice.cooper@customer.com",
      "type": "vehicle"
    }
  ],
  "customers": [
    {
      "id": 19,
      "name": "Alice Cooper",
      "email": "alice.cooper@customer.com",
      "phone_number": "(555) 714-5422",
      "address": "123 Elm St, Springfield, NY 10001",
      "type": "customer"
    }
  ],
  "repair_orders": [],
  "total_results": 2
}
```

---

## 🧪 **Test These Exact Queries**

### **Frontend API Call Template**:
```javascript
// Test the exact endpoints that work on backend
const testVehicleSearch = async () => {
  console.log('🔍 Testing Vehicle Search...');
  
  const response = await fetch('/api/shop/vehicles/?search=toyota', {
    headers: {
      'Authorization': `Bearer ${yourAccessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  console.log('Status:', response.status);
  const data = await response.json();
  console.log('Response:', JSON.stringify(data, null, 2));
  
  // ✅ Expected: Array with 1 Toyota vehicle
  // ❌ If you see Honda/Ford here, check your endpoint URL
  
  return data;
};

const testGlobalSearch = async () => {
  console.log('🌐 Testing Global Search...');
  
  const response = await fetch('/api/shop/search/?q=toyota', {
    headers: {
      'Authorization': `Bearer ${yourAccessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  console.log('Status:', response.status);
  const data = await response.json();
  console.log('Response:', JSON.stringify(data, null, 2));
  
  // ✅ Expected: {vehicles: [1 Toyota], customers: [1 Alice Cooper], total_results: 2}
  // ❌ If you see Honda/Ford here, check your caching/state management
  
  return data;
};

// Run both tests
testVehicleSearch();
testGlobalSearch();
```

---

## 🔍 **Backend Verification Commands**

**You can verify these work by running**:
```bash
# 1. Test direct database query
cd /path/to/your/django/project
python manage.py shell -c "
from shop.models import Vehicle
from django.db.models import Q
vehicles = Vehicle.objects.filter(Q(make__icontains='toyota'))
print(f'Found {vehicles.count()} Toyota vehicles')
for v in vehicles:
    print(f'  {v.make} {v.model} - {v.customer.name}')
"

# 2. Test API endpoint with curl
curl -X POST "http://localhost:8000/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}' \
  | jq -r '.access' \
  | xargs -I {} curl -H "Authorization: Bearer {}" \
    "http://localhost:8000/api/shop/vehicles/?search=toyota"
```

---

## 🚨 **Common Frontend Mistakes**

### ❌ **Wrong Endpoint URLs**
```javascript
// ❌ WRONG - these might not exist or work differently
'/api/vehicles/?search=toyota'           // Missing 'shop'
'/api/shop/vehicle/?search=toyota'       // Wrong singular 'vehicle'
'/api/search/?query=toyota'              // Wrong parameter name
```

### ❌ **Wrong Query Parameters**
```javascript
// ❌ WRONG parameter names
'/api/shop/vehicles/?q=toyota'           // Should be 'search' not 'q'
'/api/shop/vehicles/?query=toyota'       // Should be 'search' not 'query'
'/api/shop/search/?search=toyota'        // Should be 'q' not 'search'
```

### ❌ **Missing Authentication**
```javascript
// ❌ WRONG - missing or malformed auth header
fetch('/api/shop/vehicles/?search=toyota')  // No auth header
fetch('/api/shop/vehicles/?search=toyota', {
  headers: { 'Authorization': yourToken }   // Missing 'Bearer '
})
```

### ❌ **Caching Issues**
```javascript
// ❌ WRONG - not handling cache properly
const [searchResults, setSearchResults] = useState([]);

const handleSearch = (query) => {
  // BUG: Not clearing previous results
  searchAPI(query).then(newResults => {
    setSearchResults([...searchResults, ...newResults]); // Appending old results!
  });
};
```

---

## ✅ **Correct Frontend Implementation**

```javascript
// ✅ CORRECT implementation
const SearchComponent = () => {
  const [searchResults, setSearchResults] = useState({
    vehicles: [],
    customers: [],
    repair_orders: [],
    total_results: 0
  });
  const [loading, setLoading] = useState(false);

  const handleSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults({ vehicles: [], customers: [], repair_orders: [], total_results: 0 });
      return;
    }

    setLoading(true);
    // Clear previous results immediately
    setSearchResults({ vehicles: [], customers: [], repair_orders: [], total_results: 0 });

    try {
      const token = localStorage.getItem('accessToken');
      
      // Use the correct global search endpoint
      const response = await fetch(`/api/shop/search/?q=${encodeURIComponent(query)}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data); // Set new results only
        
        console.log('Search Results:', {
          query,
          total: data.total_results,
          vehicles: data.vehicles.length,
          customers: data.customers.length
        });
      } else {
        console.error('Search failed:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input 
        type="text" 
        placeholder="Search for vehicles, customers..." 
        onChange={(e) => handleSearch(e.target.value)}
      />
      
      {loading && <div>Searching...</div>}
      
      <div>
        <h3>Vehicles ({searchResults.vehicles.length})</h3>
        {searchResults.vehicles.map(vehicle => (
          <div key={vehicle.id}>
            {vehicle.make} {vehicle.model} - {vehicle.customer_name}
          </div>
        ))}
        
        <h3>Customers ({searchResults.customers.length})</h3>
        {searchResults.customers.map(customer => (
          <div key={customer.id}>
            {customer.name} - {customer.email}
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## 🎯 **Debug Checklist for Frontend Developer**

1. **✅ Verify Endpoint URLs**
   - Vehicle search: `/api/shop/vehicles/?search=toyota`
   - Global search: `/api/shop/search/?q=toyota`

2. **✅ Check Authentication**
   - Header format: `Authorization: Bearer <token>`
   - Valid token (not expired)

3. **✅ Clear All Caches**
   - Browser cache: Ctrl+Shift+F5
   - Local storage: Clear in DevTools
   - API cache: Add cache-busting headers

4. **✅ Monitor Network Tab**
   - See exact requests being made
   - Check response data
   - Verify no duplicate/conflicting requests

5. **✅ Add Debug Logging**
   - Log query parameters
   - Log API responses
   - Log state changes

When you implement these exact queries and endpoints, you should get the same accurate results that the backend is returning. If you're still seeing Honda/Ford vehicles, the issue is in your frontend caching or state management, not the API calls themselves.

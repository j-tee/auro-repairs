# API Testing Commands for Frontend Developer

## Quick Testing with cURL

### 1. Get Access Token (Login)

```bash
# Login as Owner
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "owner@autorepairshop.com", "password": "owner123"}'

# Example Response:
# {"access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...", "refresh": "..."}
```

### 2. Test Vehicles API

```bash
# Replace YOUR_ACCESS_TOKEN with the token from step 1
curl -X GET http://localhost:8000/api/shop/vehicles/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. Expected Response Structure

```json
[
  {
    "id": 27,
    "customer": {
      "id": 19,
      "name": "Alice Cooper",
      "phone_number": "(555) 714-5422",
      "email": "alice.cooper@customer.com",
      "address": "123 Elm St, Springfield, NY 10001",
      "user": null
    },
    "customer_name": "Alice Cooper",
    "customer_email": "alice.cooper@customer.com",
    "customer_phone": "(555) 714-5422",
    "make": "Toyota",
    "model": "Camry",
    "year": 2020,
    "vin": "1HGBH41JXMN118133",
    "license_plate": "ABC-5189",
    "color": "Silver"
  }
]
```

## Browser Testing

### JavaScript Console Test

```javascript
// 1. Login first
fetch('http://localhost:8000/api/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'owner@autorepairshop.com',
    password: 'owner123'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Login successful:', data);
  
  // 2. Use the access token to get vehicles
  return fetch('http://localhost:8000/api/shop/vehicles/', {
    headers: {
      'Authorization': `Bearer ${data.access}`,
      'Content-Type': 'application/json'
    }
  });
})
.then(response => response.json())
.then(vehicles => {
  console.log('Vehicles loaded:', vehicles.length);
  
  // 3. Check customer names
  vehicles.forEach((vehicle, i) => {
    console.log(`${i+1}. ${vehicle.customer_name} -> ${vehicle.year} ${vehicle.make} ${vehicle.model}`);
  });
  
  // 4. Verify the fix
  const hasUnknownCustomers = vehicles.some(v => !v.customer_name || v.customer_name === 'Unknown Customer');
  if (hasUnknownCustomers) {
    console.error('❌ Still has unknown customers!');
  } else {
    console.log('✅ All vehicles have proper customer names!');
  }
})
.catch(error => console.error('Error:', error));
```

## Frontend Component Example

### React Component

```jsx
import React, { useState, useEffect } from 'react';

const VehicleRegistry = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchVehicles();
  }, []);

  const fetchVehicles = async () => {
    try {
      const accessToken = localStorage.getItem('accessToken');
      
      const response = await fetch('/api/shop/vehicles/', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setVehicles(data);
    } catch (error) {
      console.error('Error fetching vehicles:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading vehicles...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="vehicle-registry">
      <h2>🚗 Vehicle Registry</h2>
      <table>
        <thead>
          <tr>
            <th>Customer</th>
            <th>Vehicle</th>
            <th>VIN</th>
            <th>License Plate</th>
            <th>Color</th>
          </tr>
        </thead>
        <tbody>
          {vehicles.map(vehicle => (
            <tr key={vehicle.id}>
              <td>
                {/* ✅ Use customer_name field directly */}
                {vehicle.customer_name || 'Unknown Customer'}
              </td>
              <td>
                {vehicle.year} {vehicle.make} {vehicle.model}
              </td>
              <td>{vehicle.vin}</td>
              <td>{vehicle.license_plate}</td>
              <td>{vehicle.color}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default VehicleRegistry;
```

### Vue.js Component

```vue
<template>
  <div class="vehicle-registry">
    <h2>🚗 Vehicle Registry</h2>
    <table v-if="!loading">
      <thead>
        <tr>
          <th>Customer</th>
          <th>Vehicle</th>
          <th>VIN</th>
          <th>License Plate</th>
          <th>Color</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="vehicle in vehicles" :key="vehicle.id">
          <td>
            <!-- ✅ Use customer_name field directly -->
            {{ vehicle.customer_name || 'Unknown Customer' }}
          </td>
          <td>
            {{ vehicle.year }} {{ vehicle.make }} {{ vehicle.model }}
          </td>
          <td>{{ vehicle.vin }}</td>
          <td>{{ vehicle.license_plate }}</td>
          <td>{{ vehicle.color }}</td>
        </tr>
      </tbody>
    </table>
    <div v-else>Loading vehicles...</div>
  </div>
</template>

<script>
export default {
  name: 'VehicleRegistry',
  data() {
    return {
      vehicles: [],
      loading: true
    }
  },
  async mounted() {
    await this.fetchVehicles();
  },
  methods: {
    async fetchVehicles() {
      try {
        const accessToken = localStorage.getItem('accessToken');
        
        const response = await fetch('/api/shop/vehicles/', {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          this.vehicles = await response.json();
        }
      } catch (error) {
        console.error('Error fetching vehicles:', error);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
```

## Troubleshooting Checklist

### ❌ Still seeing "Unknown Customer"?

1. **Clear browser cache**: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)
2. **Check API endpoint**: Must be `/api/shop/vehicles/` not `/api/vehicles/`
3. **Verify authentication**: Ensure JWT token is being sent
4. **Check field name**: Use `vehicle.customer_name` not `vehicle.customer?.name`
5. **Test in incognito mode**: Rules out caching issues

### ❌ Getting 403 Forbidden?

1. **Check authentication token**: Ensure it's valid and not expired
2. **Verify user role**: Customers can only see their own vehicles
3. **Check headers**: Must include `Authorization: Bearer <token>`

### ❌ Getting empty response?

1. **Check user role**: Different roles see different data
2. **Verify server is running**: Should be on `http://localhost:8000`
3. **Check CORS settings**: Ensure frontend can communicate with backend

## Test Accounts

```
Owner (sees all 7 vehicles):
  Email: owner@autorepairshop.com
  Password: owner123

Employee (sees all 7 vehicles):
  Email: john.mechanic@autorepair.com
  Password: password123

Customer (sees only their own vehicles):
  Email: alice.cooper@customer.com
  Password: password123
```

## Expected Results

When working correctly, you should see:

```
✅ Alice Cooper -> 2020 Toyota Camry
✅ Bob Martinez -> 2019 Honda Civic  
✅ Carol White -> 2021 Ford F-150
✅ David Lee -> 2018 Chevrolet Malibu
✅ Emma Garcia -> 2020 Nissan Altima
✅ Frank Rodriguez -> 2019 BMW 3 Series
✅ Frank Rodriguez -> 2021 Audi A4
```

**No more "Unknown Customer" entries!** 🎉

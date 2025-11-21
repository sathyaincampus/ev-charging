# How to View Real Charging Stations in the UI

## Where the Data Appears

### 1. **Console/Terminal Output** (Most Detailed)

When you run the Streamlit app, the **terminal/console** shows detailed information:

```bash
streamlit run app_streamlit.py
```

You'll see output like:
```
🔍 Querying OpenChargeMap API...
   Midpoint: (35.91355, -120.33155)
   Search radius: 309.1 km
   Min power: 150 kW
   Found 20 stations from API
```

### 2. **Streamlit Web UI** (Now Enhanced!)

After the latest update, the web UI now shows:

#### A. **Charging Stations Section**
After clicking "Start Trip Planning", if charging is needed, you'll see:

```
🔌 Charging Stations Found
```

With expandable cards for each station showing:
- Network name (Tesla Supercharger, EVgo, etc.)
- Location (city, state)
- Address
- Power rating (kW)
- Price per kWh
- Availability status
- Amenities

#### B. **Notifications Panel** (Right sidebar)
Shows reservation details:
```
🔌 Reserved Tesla Supercharger at Kettleman City, CA
```

### 3. **Agent Activity Panel**

The "Charging" agent status shows when it's:
- 🔄 Finding chargers...
- ✅ Complete

## How to Demo

### Quick Demo (5 minutes):

1. **Start the app:**
   ```bash
   cd ev-concierge
   streamlit run app_streamlit.py
   ```

2. **In the browser:**
   - Select: **Los Angeles, CA** → **San Francisco, CA**
   - Set battery: **35%**
   - Click: **"🚀 Start Trip Planning"**

3. **Watch for:**
   - Console shows: "🔍 Querying OpenChargeMap API..."
   - Console shows: "Found X stations from API"
   - Web UI shows: "🔌 Charging Stations Found" section
   - Expandable cards with real station details
   - Notification: "🔌 Reserved [Network] at [Location]"

### What You'll See:

**In the Web UI:**
```
🔌 Charging Stations Found

⚡ Tesla Supercharger - Kettleman City, CA
   Address: 33341 Bernard Drive, Kettleman City, CA
   Power: 250 kW
   Price: $0.4/kWh
   Status: 🟢 Available

⚡ Electrify America - Lost Hills, CA
   Address: 21959 CA-46, Lost Hills, CA
   Power: 350 kW
   Price: $0.4/kWh
   Status: 🟢 Available

⚡ EVgo - Ladera Ranch, CA
   Address: 123 Main St, Ladera Ranch, CA
   Power: 350 kW
   Price: $0.4/kWh
   Status: 🟢 Available
```

**In the Console:**
```
🔍 DEBUG - Trip Planning Agent:
   - Tool result: {'needs_charging': True, 'deficit_percent': 15}
   Tool calls made: 1

🔍 Querying OpenChargeMap API...
   Midpoint: (35.91355, -120.33155)
   Search radius: 309.1 km
   Min power: 150 kW
   Found 20 stations from API
```

## Troubleshooting

### If you don't see stations in the UI:

1. **Check the console** - The API query happens there first
2. **Verify USE_MOCK_DATA=false** in `.env`
3. **Check battery level** - Set to 30-40% to trigger charging need
4. **Look for errors** in the console output

### If you see "Unknown Network":

This was fixed! Make sure you have the latest code with `compact=false` in the API request.

### If the agent doesn't call the charging tool:

- The trip planning agent might determine charging isn't needed
- Try a longer route (LA → SF) with lower battery (35%)

## For Hackathon Judges

**Point out these features:**

1. **Real API Integration**: Show the console output with API query
2. **Network Variety**: Expand different station cards to show Tesla, EVgo, Electrify America
3. **Real Addresses**: These are actual locations you can navigate to
4. **Power Ratings**: Show the variety (150kW, 250kW, 350kW)
5. **Smart Sorting**: Stations are ordered by distance from origin
6. **Reservation Details**: Show the notification with network name and location

## Screenshots to Take

1. **Before**: Mock data (USE_MOCK_DATA=true)
2. **After**: Real data (USE_MOCK_DATA=false)
3. **Console output**: Showing API query
4. **Station cards**: Expanded view with details
5. **Notifications**: Showing reserved station with network name

---

**The real charging station data is now visible in both the console AND the web UI!** 🎉

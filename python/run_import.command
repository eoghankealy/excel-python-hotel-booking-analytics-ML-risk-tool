#!/bin/bash
cd /Users/eoghankealy/Documents/data_projects/hotel_bookings/python
echo "🏨 Starting Hotel Booking Import..."
echo ""
python3 import_bookings.py
echo ""
echo "✅ Import complete! You can close this window."
read -p "Press Enter to close..."

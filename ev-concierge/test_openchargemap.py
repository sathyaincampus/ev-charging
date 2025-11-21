#!/usr/bin/env python3
"""
Quick test script for OpenChargeMap integration
"""

from utils.location_coords import get_coordinates
from utils.openchargemap_client import get_chargers_along_route
import json

def test_openchargemap():
    print("=" * 60)
    print("Testing OpenChargeMap Integration")
    print("=" * 60)
    
    # Test 1: LA to San Francisco
    print("\n🧪 Test 1: Los Angeles to San Francisco")
    origin = "Los Angeles, CA"
    destination = "San Francisco, CA"
    
    origin_coords = get_coordinates(origin)
    dest_coords = get_coordinates(destination)
    
    print(f"   Origin: {origin} -> {origin_coords}")
    print(f"   Destination: {destination} -> {dest_coords}")
    
    if origin_coords and dest_coords:
        stations = get_chargers_along_route(
            origin_coords,
            dest_coords,
            min_power_kw=50,
            max_results=5
        )
        
        print(f"\n   ✅ Found {len(stations)} charging stations:")
        for i, station in enumerate(stations, 1):
            print(f"\n   {i}. {station['network']} - {station['location']}")
            print(f"      ID: {station['id']}")
            print(f"      Address: {station['address']}")
            print(f"      Power: {station['power_kw']} kW")
            print(f"      Price: ${station['price_per_kwh']}/kWh")
            print(f"      Coordinates: ({station['latitude']}, {station['longitude']})")
    
    # Test 2: LA to San Diego (shorter route)
    print("\n" + "=" * 60)
    print("🧪 Test 2: Los Angeles to San Diego")
    origin = "Los Angeles, CA"
    destination = "San Diego, CA"
    
    origin_coords = get_coordinates(origin)
    dest_coords = get_coordinates(destination)
    
    print(f"   Origin: {origin} -> {origin_coords}")
    print(f"   Destination: {destination} -> {dest_coords}")
    
    if origin_coords and dest_coords:
        stations = get_chargers_along_route(
            origin_coords,
            dest_coords,
            min_power_kw=100,  # Higher power requirement
            max_results=5
        )
        
        print(f"\n   ✅ Found {len(stations)} charging stations (100+ kW):")
        for i, station in enumerate(stations, 1):
            print(f"\n   {i}. {station['network']} - {station['location']}")
            print(f"      Power: {station['power_kw']} kW")
    
    print("\n" + "=" * 60)
    print("✅ OpenChargeMap integration test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_openchargemap()

import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import numpy as np

# Micro warehouse locations
warehouses = {
    "Hebbal": (13.066819, 77.604538),
    "Banashankari": (12.89162, 77.55644),
    "Mahadevapura": (12.9908333, 77.7042778),
    "Chandra Layout": (12.997615, 77.5138312),
    "Kudlu": (12.8798786, 77.6529101),
    "Koramangala NGV": (12.88021201, 77.65505249)
}

def geocode_address(address):
    geolocator = Nominatim(user_agent="geo_locator")
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        return None
    except:
        return None

def find_nearest_warehouse(driver_location):
    if not driver_location:
        return None, None
    min_dist = float('inf')
    nearest_wh = None
    for wh, wh_loc in warehouses.items():
        dist = geodesic(driver_location, wh_loc).km
        if dist < min_dist:
            min_dist = dist
            nearest_wh = wh
    return nearest_wh, min_dist

def main():
    st.title("Driver to Micro Warehouse Assignment")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Driver Data CSV", type=['csv'])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # Process only if required columns exist
        required_cols = ['driver_name', 'Driver Number', 'current_address']
        if all(col in df.columns for col in required_cols):
            st.write("Processing data...")
            
            # Add progress bar
            progress_bar = st.progress(0)
            
            # Geocode addresses and find nearest warehouse
            df['driver_location'] = df['current_address'].apply(geocode_address)
            df['nearest_warehouse'], df['distance_km'] = zip(*df['driver_location'].apply(find_nearest_warehouse))
            
            # Update progress
            progress_bar.progress(100)
            
            # Display results by warehouse
            for warehouse in sorted(warehouses.keys()):
                st.subheader(f"{warehouse} [BH Micro warehouse]")
                wh_drivers = df[df['nearest_warehouse'] == warehouse]
                
                if not wh_drivers.empty:
                    # Display relevant columns
                    display_df = wh_drivers[['driver_name', 'Driver Number', 'distance_km']]
                    display_df = display_df.sort_values('distance_km')
                    display_df['distance_km'] = display_df['distance_km'].round(2)
                    display_df.columns = ['Driver Name', 'Driver Number', 'Distance (km)']
                    st.dataframe(display_df)
                else:
                    st.write("No drivers found near this warehouse")
            
            # Option to download processed data
            st.download_button(
                label="Download Processed Data",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='drivers_with_warehouse_assignments.csv',
                mime='text/csv'
            )
        else:
            st.error("CSV file is missing required columns. Please ensure it contains: driver_name, Driver Number, current_address")

if __name__ == "__main__":
    main()
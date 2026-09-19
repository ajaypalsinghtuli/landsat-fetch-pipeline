import os
import requests
from pystac_client import Client
import planetary_computer
from shapely.geometry import shape

# Switch to Planetary Computer which allows free, token-signed downloads
STAC_API_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
COLLECTION = "landsat-c2-l2"

def fetch_landsat_data(task_id, geojson_feature, start_date, end_date, output_dir):
    geometry = geojson_feature.get('geometry')
    if not geometry:
        raise ValueError("Invalid GeoJSON: Missing geometry")
        
    bounding_box = shape(geometry).bounds
    time_range = f"{start_date}/{end_date}"

    # 1. Query the STAC Catalog with the Planetary Computer modifier
    # This automatically signs all URLs so we don't get 403 errors
    client = Client.open(STAC_API_URL, modifier=planetary_computer.sign_inplace)
    search = client.search(
        collections=[COLLECTION],
        bbox=bounding_box,
        datetime=time_range,
        max_items=1 
    )
    
    items = list(search.items())
    if not items:
        raise Exception("No Landsat imagery found for the specified area and dates.")
        
    selected_item = items[0]
    
    # 2. Select the asset to download
    asset_key = 'rendered_preview' 
    if asset_key not in selected_item.assets:
        asset_key = list(selected_item.assets.keys())[0] 
        
    # This URL is now a fully authenticated HTTPS link with a SAS token
    download_url = selected_item.assets[asset_key].href
    
    # 3. Download the file to local storage
    os.makedirs(output_dir, exist_ok=True)
    file_extension = download_url.split('.')[-1].split('?')[0]
    if len(file_extension) > 4: 
        file_extension = "jpg"
        
    file_name = f"{task_id}_{selected_item.id}.{file_extension}"
    file_path = os.path.join(output_dir, file_name)
    
    response = requests.get(download_url, stream=True)
    response.raise_for_status()
    
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    return file_path
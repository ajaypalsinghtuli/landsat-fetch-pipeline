import os
import requests
from pystac_client import Client
from shapely.geometry import shape

# Element 84 Earth Search v1 (AWS) - Excellent open STAC for Landsat
STAC_API_URL = "https://earth-search.aws.element84.com/v1"
COLLECTION = "landsat-c2-l2"

def fetch_landsat_data(task_id, geojson_feature, start_date, end_date, output_dir):
    """
    Queries the STAC API for Landsat data intersecting the given geometry and dates,
    then downloads a visual asset to the local server.
    """
    # 1. Extract bounding box from the GeoJSON Feature
    geometry = geojson_feature.get('geometry')
    if not geometry:
        raise ValueError("Invalid GeoJSON: Missing geometry")
        
    bounding_box = shape(geometry).bounds # Returns (minx, miny, maxx, maxy)
    time_range = f"{start_date}/{end_date}"

    # 2. Query the STAC Catalog
    client = Client.open(STAC_API_URL)
    search = client.search(
        collections=[COLLECTION],
        bbox=bounding_box,
        datetime=time_range,
        max_items=1 # Grab the first matching scene for this pipeline
    )
    
    items = list(search.items())
    if not items:
        raise Exception("No Landsat imagery found for the specified area and dates.")
        
    selected_item = items[0]
    
    # 3. Select the asset to download
    # Landsat items have multiple assets (bands). We will download the rendered visual image ('rendered_preview')
    # If you need raw GeoTIFFs, you would use assets like 'red', 'green', 'nir08'
    asset_key = 'rendered_preview' 
    
    if asset_key not in selected_item.assets:
        # Fallback if rendered_preview is unavailable
        asset_key = list(selected_item.assets.keys())[0] 
        
    download_url = selected_item.assets[asset_key].href
    
    # 4. Download the file to local storage
    os.makedirs(output_dir, exist_ok=True)
    file_extension = download_url.split('.')[-1].split('?')[0] # Basic extension parsing
    if len(file_extension) > 4: 
        file_extension = "jpg" # default fallback
        
    file_name = f"{task_id}_{selected_item.id}.{file_extension}"
    file_path = os.path.join(output_dir, file_name)
    
    response = requests.get(download_url, stream=True)
    response.raise_for_status()
    
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    return file_path
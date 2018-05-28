import json
import os
import requests

from subprocess import Popen,PIPE

# Get this from the Ghiro Profile page
ghiro_api_key = ""

# Get the IP address when you boot up the Ghiro VM
ghiro_ip_address = ""

# Mac OSX
hunchly_api_location = "/Applications/Hunchly2/Contents/MacOS/HunchlyAPI"

# Windows
#hunchly_api_location = "C:\\Program Files (x86)\\Hunchly 2\\Dashboard\\HunchlyAPI.exe"

# Linux
#hunchly_api_location   = "/opt/hunchly/HunchlyAPI"


ghiro_new_case_url  = "http://%s/api/cases/new" % ghiro_ip_address
ghiro_new_image_url = "http://%s/api/images/new" % ghiro_ip_address

#
# Retrieves all photos for a case from Hunchly
#
def get_hunchly_photos(case_id):
    
    process        = Popen([hunchly_api_location, 'casePhotos','-c',str(case_id)], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
        
    results = json.loads(stdout)    
        
    return results['photos']    
  

#
# Retrieves all Hunchly cases
#
def get_hunchly_cases():
    
    process        = Popen([hunchly_api_location, 'cases'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    
    results = json.loads(stdout)    
    
    return results['cases']

#
# This creates a new case in Ghiro.
# Returns the Ghiro Case ID
#
def create_ghiro_case(case_name):
    
    params = {}
    params['name']    = case_name
    params['api_key'] = ghiro_api_key
    
    response = requests.post(ghiro_new_case_url,params)
    
    if response.status_code == 200:
        
        print "[*] Created a new Ghiro case named: %s" % case_name
        
        ghiro_response = response.json()
        
        return ghiro_response['id']
    
    return

#
# This uploads photos to Ghiro for processing.
#
def create_ghiro_images(case_id,image_list):
    
    upload_count = 0
    
    for image in image_list:
        
        params = {}
        params['case_id'] = case_id
        params['api_key'] = ghiro_api_key
        
        file_name = os.path.basename(image['photo_local_file_path'])
        
        # open the image file for uploading
        with open(image['photo_local_file_path'],"rb") as fd:
            
            file_upload = {}
            file_upload['image'] = (file_name,fd.read())
        
        response = requests.post(ghiro_new_image_url,data=params,files=file_upload)
        
        if response.status_code == 200:
            
            print "[*] Uploaded %s to case ID: %d (%d of %d)" % (image['photo_local_file_path'],case_id,upload_count,len(
                                                                                                                  image_list))
            
            upload_count += 1
        
    return


# retrieve all cases from Hunchly
cases = get_hunchly_cases()

for case in cases:
    
    photos = get_hunchly_photos(case['case_id'])
    
    if photos != None:
        
        # create a new Ghiro case to match Hunchly
        ghiro_case_id = create_ghiro_case(case['case_name'])
        
        # upload all of the photos to Ghiro
        create_ghiro_images(ghiro_case_id,photos)
    
            
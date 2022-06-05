from multiprocessing import Pool
import os
import json
import re
from google.cloud import vision
from google.cloud import storage

def async_detect_document(gcs_source_uri, gcs_destination_uri, id):
    """OCR with PDF/TIFF as source files on GCS"""

    # Supported mime_types are: 'application/pdf' and 'image/tiff'
    mime_type = 'application/pdf'

    # How many pages should be grouped into each json output file.
    batch_size = 4

    client = vision.ImageAnnotatorClient.from_service_account_json('jade-ocr-a6a21d754209.json')

    feature = vision.Feature(
        type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(
        gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config,
        output_config=output_config)

    operation = client.async_batch_annotate_files(
        requests=[async_request])

    print('Waiting for the operation to finish.')
    operation.result(timeout=420)

    # Once the request has completed and the output has been
    # written to GCS, we can list all the output files.
    storage_client = storage.Client.from_service_account_json('jade-ocr-a6a21d754209.json')

    match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)

    bucket = storage_client.get_bucket(bucket_name)

    # List objects with the given prefix, filtering out folders.
    blob_list = [blob for blob in list(bucket.list_blobs(
        prefix=prefix)) if not blob.name.endswith('/')]
    print('Output files:')
    for blob in blob_list:
        print(blob.name)

    # Process the first output file from GCS.
    # Since we specified batch_size=2, the first response contains
    # the first two pages of the input file.
    output = blob_list[0]

    json_string = output.download_as_string()
    response = json.loads(json_string)

    # The actual response for the first page of the input file.
    for page_response in response['responses']:
        annotation = page_response['fullTextAnnotation']
        with open(f'interpreted-syllabi2/{id}.txt', 'a') as myfile:
            myfile.write(annotation['text'])
    
    #delete above and replace with below for original (working) script
    #first_page_response = response['responses'][0]
    #annotation = first_page_response['fullTextAnnotation']

    # Here we print the full text from the first page.
    # The response contains more information:
    # annotation/pages/blocks/paragraphs/words/symbols
    # including confidence scores and bounding boxes

    #print('Full text:\n')
    #print(annotation['text'])

def extract_files_to_convert():
    files = []
    client = storage.Client.from_service_account_json('jade-ocr-a6a21d754209.json')
    bucket_name = 'jades-syllabi'
    prefix = 'syllabi/'
    bucket = client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    for blob in blobs:
        fulluri = f'gs://{bucket_name}/{blob.name}'
        files.append(fulluri)
        #print(fulluri)
    return files

def run_one_file(gcs_source_uri):
    id = gcs_source_uri.split('/')[-1]
    id = ''.join(id.split()).strip('.pdf')
    gcs_destination_uri = 'gs://jades-syllabi/interpreted-syllabi2/' + id
    print(f'running with {gcs_source_uri}, {gcs_destination_uri}, {id}')
    async_detect_document(gcs_source_uri, gcs_destination_uri, id)

def main():
    files = extract_files_to_convert()   
    pool = Pool(os.cpu_count() - 1)
    pool.map(run_one_file, files)

    #gcs_source_uri = sys.argv[1]
    ##print(gcs_source_uri)
    #gcs_destination_uri = sys.argv[2]
    #id = gcs_source_uri.split('/')[-1]
    #id = ''.join(id.split()).strip('.pdf')
    #gcs_destination_uri += id
    ##print(gcs_destination_uri)
    #print(f'running with {gcs_source_uri}')
    #async_detect_document(gcs_source_uri, gcs_destination_uri, id)

if __name__== "__main__":
    main()

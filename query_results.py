from google.cloud import storage
import json


def main():
    client = storage.Client.from_service_account_json('jade-ocr-a6a21d754209.json')
    bucket_name = 'jades-syllabi'
    prefix = 'interpreted-syllabi2/'
    bucket = client.get_bucket(bucket_name)
    blobs = [blob for blob in bucket.list_blobs(prefix=prefix) if not blob.name.endswith('/')]
    for blob in blobs:
        print(''.join(blob.name.split('.')[:-1]))
        json_string = blob.download_as_string()
        response = json.loads(json_string)
        for page_response in response['responses']:
            annotation = page_response['fullTextAnnotation']
            with open(f'{"".join(blob.name.split(".")[:-1])}.txt', 'a') as myfile:
                myfile.write(annotation['text'])
    return


if __name__ == "__main__":
    main()
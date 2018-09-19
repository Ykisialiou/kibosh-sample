import json
import os

from minio import Minio

def new_image():
    if on_disk_db():
        return ImageDisk()
    else:
        return ImageMinio()

def on_disk_db():
    vcap_service = json.loads(os.environ.get('VCAP_SERVICES', "{}"))
    if vcap_service.get("minio", ""):
        return False
    return True

class ImageDisk:
    def __init__(self):
        self.on_disk = True

    def get_image(self, path):
        with open(os.path.join(".", "static", "images", path), mode='rb') as file:
            return file.read()

    def save_image(self, file):
        file.save(os.path.join(".", "static", "images", file.filename))


class ImageMinio:
    def __init__(self):
        self.on_disk = False
        self.bucket_name = "kibosh"
        self.credentials = self.get_credentials_from_env()
        url = self.credentials["host"] + ":" + str(self.credentials["port"])
        self.minio_client = Minio(url, self.credentials["access_key"], self.credentials["secret_key"], secure=False)
        self.bootstrap()

    def bootstrap(self):
        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name)
        self.copy_image("rabbit.jpg")
        self.copy_image("dog_with_cows.jpg")

    def copy_image(self, path):
        with open(os.path.join(".", "static", "images", path), 'rb') as file_data:
            file_stat = os.stat(os.path.join(".", "static", "images", path))
            self.minio_client.put_object(self.bucket_name, path, file_data, file_stat.st_size)

    def get_image(self, path):
        return self.minio_client.get_object(self.bucket_name, path).read()

    def save_image(self, file):
        bytes = file.read()
        file.stream.seek(0)
        self.minio_client.put_object(self.bucket_name, file.filename, file, len(bytes))

    def get_credentials_from_env(self):
        vcap_service = json.loads(os.environ['VCAP_SERVICES'])

        minio = vcap_service['minio'][0]
        secrets = minio["credentials"]["secrets"][0]
        services = minio["credentials"]["services"][0]

        return {
            'host': services["status"]["loadBalancer"]["ingress"][0]["ip"],
            'port': services["spec"]["ports"][0]["port"],
            'access_key': secrets["data"]["accesskey"],
            'secret_key': secrets["data"]["secretkey"]
        }

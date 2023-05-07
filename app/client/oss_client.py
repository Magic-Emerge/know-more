import oss2
from app.config.conf import OSS_ENDPOINT, ACCESSKEY_ID, ACCESSKEY_SECRET, BUCKET_NAME

endpoint = OSS_ENDPOINT

auth = oss2.Auth(ACCESSKEY_ID, ACCESSKEY_SECRET)
bucket = oss2.Bucket(auth, endpoint, BUCKET_NAME)


def upload_object(file_name: str, content: str) -> oss2.models.PutObjectResult:
    return bucket.put_object(file_name, content)


def download_object(file_name: str) -> str:
    return bucket.get_object(file_name).read().decode('utf-8')


# if __name__ == '__main__':
#     result = upload_object("sample.txt", "test is good")
#     print(result)
#     res = download_object("sample.txt")
#     print(res)

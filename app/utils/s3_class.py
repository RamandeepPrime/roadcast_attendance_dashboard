class S3:
    async def upload(self, file_path: str, destination_path: str):
        """
        Dummy S3 upload implementation.
        Replace this with actual logic for uploading a file to S3.
        """
        print(f"Uploading {file_path} to {destination_path}")

# singletone instance
s3_instance = S3()
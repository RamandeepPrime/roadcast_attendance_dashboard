import os
from tempfile import TemporaryFile
import tempfile
from uuid import uuid4

from app.utils.s3_class import s3_instance


async def save_image(image, image_base_path):
	"""
		dummy function 

		Solutions:
			Create s3 class which upload files to s3.
			
	"""
	image_upload_path = os.path.join(image_base_path, str(uuid4()))
	with tempfile.NamedTemporaryFile(delete=True) as tmpfile:
		tmpfile.write(image.file.read())
		tmpfile.flush()
		temp_file_path = tmpfile.name

		# Upload the file to S3
		await s3_instance.upload(temp_file_path, image_upload_path)
	
	return image_upload_path
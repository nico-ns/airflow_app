import os
import stat

from pathlib import Path
from airflow.contrib.hooks.fs_hook import FSHook
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults


class CustomFileSensor(BaseSensorOperator):
    """
    Waits for a file or folder to land in a filesystem.

    If the path given is a directory then this sensor will only return true if
    any files exist inside it (either directly, or within a subdirectory)

    :param fs_conn_id: reference to the File (path)
        connection id
    :type fs_conn_id: str
    :param filepath: File or folder name (relative to
        the base path set within the connection)
    :type fs_conn_id: str
    """
    template_fields = ('filepath',)

    ui_color = '#91818a'


    @apply_defaults
    def __init__(self,
                 filepath,
                 fs_conn_id='fs_default',
                 file_type=None,
                 *args,
                 **kwargs):
        super(CustomFileSensor, self).__init__(*args, **kwargs)
        self.filepath = filepath
        self.fs_conn_id = fs_conn_id
        self.file_type = file_type

    def poke(self, context):
        hook = FSHook(self.fs_conn_id)
        basepath = hook.get_path()
        self.log.info(f'Poking for {self.file_type} files  in {self.filepath}')
        
        try:
            if self.file_type:
                files = [str(file) for file in Path(self.filepath).glob(f"*.{self.file_type}")]

                if len(files):
                    context["ti"].xcom_push(key="files", value=files)
                    return True
            else:
                self.log.info("File type was not specified")
                return False

        except OSError:
            return False
        return False

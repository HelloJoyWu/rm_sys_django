import logging
import sys
import traceback
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def check_config() -> [str, None]:
    """
    Returns a message to user for missing configuration
    :return: Error info
    """
    from django.conf import settings
    aad_cfg = settings.AAD_SET

    if aad_cfg.get('AUTHENTICATION_MODE', '') == '':
        return 'Please specify one of the two authentication modes'
    if aad_cfg.get('AUTHENTICATION_MODE', '').lower() == 'serviceprincipal' and aad_cfg['TENANT_ID'] == '':
        return 'Tenant ID is not provided in the config.py file'
    # elif app.config['REPORT_ID'] == '':
    #     return 'Report ID is not provided in config.py file'
    # elif app.config['WORKSPACE_ID'] == '':
    #     return 'Workspace ID is not provided in config.py file'
    elif aad_cfg.get('CLIENT_ID', '') == '':
        return 'Client ID is not provided in config.py file'
    elif aad_cfg.get('AUTHENTICATION_MODE', '').lower() == 'masteruser':
        if aad_cfg.get('POWER_BI_USER', '') == '':
            return 'Master account username is not provided in config.py file'
        elif aad_cfg.get('POWER_BI_PASS', '') == '':
            return 'Master account password is not provided in config.py file'
    elif aad_cfg.get('AUTHENTICATION_MODE', '').lower() == 'serviceprincipal':
        if aad_cfg.get('CLIENT_SECRET', '') == '':
            return 'Client secret is not provided in config.py file'
    elif aad_cfg.get('SCOPE', '') == '':
        return 'Scope is not provided in the config.py file'
    elif aad_cfg.get('AUTHORITY_URL', '') == '':
        return 'Authority URL is not provided in the config.py file'

    return None


def get_err_txt(e: Exception) -> str:
    """
    Make error message into one line.
    :param e: error
    :return: error text
    """
    err_txt = str()
    error_class = e.__class__.__name__  # getting error class
    detail = e.args[0] if len(e.args) >= 1 else 'No detail'  # get content detail
    cl, exc, tb = sys.exc_info()  # get Call Stack

    if e.__cause__:  # get the caused exception if exists
        cause_err_class = e.__cause__.__class__.__name__
        cause_detail = e.__cause__.__str__()
        err_txt += f'While handle [{cause_err_class}] {cause_detail}, Cause \n'

    last_call_stack = traceback.extract_tb(tb)[-1]  # the last record from Call Stack
    file_name = last_call_stack[0]  # error file name
    line_num = last_call_stack[1]  # error line number in file
    func_name = last_call_stack[2]  # error function in file
    err_txt += f'File \'{file_name}\', line {line_num}, in {func_name}: [{error_class}] {detail}'
    logger.debug(f'origin error: \n {e}')

    return err_txt


def get_datawarehouse_latest_date():

    now_dt = datetime.utcnow()
    if now_dt.hour >= 22:
        datawarehouse_latest_dt = now_dt
    else:
        datawarehouse_latest_dt = now_dt - timedelta(days=1)

    return datawarehouse_latest_dt

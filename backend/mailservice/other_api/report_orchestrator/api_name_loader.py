# backend/mailservice/other_api/report_orchestrator/api_name_loader.py

import importlib
import os
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent.parent / "services"


def load_mail_service_for_report(api_name: str):
    """
    API adından doğru MailService sınıfını dinamik olarak yükler.
    Herhangi bir sabit listeye ihtiyaç duymaz.
    Arama sırası:
    - mailservice/services/*/send_<api_name>_email_task.py
    """

    try:
        # Dosya adı: send_<api_name>_email_task.py
        file_name = f"send_{api_name}_email_task.py"
        found_submodule = None

        # mailservice/services altındaki tüm klasörleri ara
        for subdir in os.listdir(BASE_PATH):
            subdir_path = BASE_PATH / subdir
            if subdir_path.is_dir():
                candidate = subdir_path / file_name
                if candidate.exists():
                    found_submodule = subdir
                    break

        if not found_submodule:
            print(f"[LOAD ERROR] Mail service dosyası bulunamadı: {api_name}")
            return None

        module_path = f"mailservice.services.{found_submodule}.send_{api_name}_email_task"
        class_name = ''.join(word.title() for word in api_name.split('_')) + "MailService"

        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    except (ModuleNotFoundError, AttributeError) as e:
        print(f"[LOAD ERROR] Mail service yüklenemedi: {api_name} – {str(e)}")
        return None














''' 
import importlib


def load_mail_service_for_report(api_name: str):
    """
    Rapor adına göre ilgili mail servis sınıfını dinamik olarak yükler.
    Geliştirilmiş versiyon: eğer özel klasördeyse otomatik çözer.
    """

    try:
        # Varsayılan klasör
        base_module = "mailservice.services"

        # Eğer özel report_orchestrator içindeyse path değiştir
        report_orchestrator_list = [
            "sofitel_balance_report",
            "customer_balance_top20",
            "sofitel_supplier_balance_report",
        ]
        if api_name in report_orchestrator_list:
            base_module += ".report_orchestrator"

        module_path = f"{base_module}.send_{api_name}_email_task"
        class_name = ''.join(word.title() for word in api_name.split('_')) + "MailService"

        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    except (ModuleNotFoundError, AttributeError) as e:
        print(f"[LOAD ERROR] Mail service bulunamadı: {api_name} – {str(e)}")
        return None

'''
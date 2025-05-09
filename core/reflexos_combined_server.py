# สร้างไฟล์ core/reflexos_combined_server.py
from reflexos_integrated_server_fully_patched import IntegratedServer
import os
import sys

# เพิ่ม path ของ extension ทั้งหมด
extensions_path = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)),
    'extensions')
sys.path.append(extensions_path)

# นำเข้าโมดูลจาก core

# สร้าง server และดึง app จากนั้น
server = IntegratedServer()
main_app = server.app
# ฟังก์ชัน setup_server และ run_server จะต้องสร้างเอง


def setup_server():
    server = IntegratedServer()
    return server.app


def run_server(app, host='0.0.0.0', port=5000, debug=True):
    app.run(host=host, port=port, debug=debug)

# ฟังก์ชันเพื่อรวม extension


def integrate_extensions(app):
    # รายชื่อ extension ที่จะรวม
    extensions = [
        'betty_countmsg',
        'betty_darkmode',
        'betty_exportcombo',
        'betty_exportmd',
        'betty_favorite',
        'betty_favoriteview',
        'betty_fixtimeago',
        'betty_fullstack',
        'betty_history_ui',
        'betty_logdownload',
        'betty_logsearch',
        'betty_noreset',
        'betty_preview',
        'betty_quickinject',
        'betty_relativetime',
        'betty_togglehistory',
        'betty_txtlog',
        'betty_uiclean'
    ]

    # รวมฟีเจอร์จากแต่ละ extension
    for ext_name in extensions:
        try:
            ext_path = os.path.join(extensions_path, ext_name)
            if os.path.exists(ext_path):
                # เพิ่ม path ของ extension
                sys.path.append(ext_path)

                # นำเข้าโมดูลแบบไดนามิก
                module_name = f"{ext_name}.reflexos_server"
                module = __import__(
                    module_name, fromlist=['integrate_extension'])

                # เรียกฟังก์ชัน integrate_extension จาก extension
                if hasattr(module, 'integrate_extension'):
                    print(f"กำลังรวม extension: {ext_name}")
                    module.integrate_extension(app)
                else:
                    print(f"ไม่พบฟังก์ชัน integrate_extension ใน {ext_name}")
        except Exception as e:
            print(f"ไม่สามารถรวม {ext_name} เนื่องจาก: {e}")

    return app


# main function
if __name__ == "__main__":
    app = setup_server()
    app = integrate_extensions(app)
    run_server(app)

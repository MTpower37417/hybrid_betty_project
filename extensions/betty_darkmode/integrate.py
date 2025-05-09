def integrate_extension(app):
    """ฟังก์ชันรวม betty_darkmode extension เข้ากับแอปหลัก"""
    from flask import jsonify, render_template

    @app.route('/darkmode/toggle', methods=['POST'])
    def toggle_darkmode():
        return jsonify({"status": "success", "mode": "dark"})

    @app.route('/darkmode/settings')
    def darkmode_settings():
        return render_template('darkmode_settings.html')

    print("รวม betty_darkmode extension สำเร็จ")
    return app

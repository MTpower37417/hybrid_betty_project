class BettyIntegrated:
    def __init__(self, user_id='user_a'):
        self.user_id = user_id

    def process_message(self, message):
        return {
            'response': 'สวัสดีค่ะ',
            'emotion': 'neutral'
        }

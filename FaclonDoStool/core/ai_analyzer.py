# falconDOS/core/ai_analyzer.py
import requests
import socket
import threading
import time
import logging

logging.basicConfig(level=logging.INFO, format='[AI-Analyzer] %(asctime)s - %(levelname)s - %(message)s')


class AIAttackAnalyzer(threading.Thread):
    def __init__(self, target_ip, control_callback, protocols=None,
                 max_blocked_before_switch=3,
                 http_port=80, tcp_port=80, udp_port=80,
                 tcp_message=None,
                 udp_message="Ping",
                 timeout=5,
                 check_interval=5):
        """
        :param target_ip: IP الهدف
        :param control_callback: دالة لاستدعاءها عند تغيير البروتوكول (للتواصل مع محرك الهجوم)
        :param protocols: قائمة البروتوكولات التي سيتم التبديل بينها
        :param max_blocked_before_switch: عدد مرات الحجب قبل التبديل
        :param ports: منافذ HTTP, TCP, UDP
        :param tcp_message: رسالة TCP لإرسالها عند الفحص
        :param udp_message: رسالة UDP لإرسالها عند الفحص
        :param timeout: مهلة الانتظار للرد
        :param check_interval: فترة الفحص بين كل محاولة
        """
        super().__init__()
        self.target_ip = target_ip
        self.control_callback = control_callback
        self.protocols = protocols or ["HTTP", "TCP", "UDP"]
        self.current_protocol_index = 0
        self.current_protocol = self.protocols[self.current_protocol_index]
        self.blocked_count = 0
        self.success_count = 0
        self.max_blocked_before_switch = max_blocked_before_switch

        self.http_port = http_port
        self.tcp_port = tcp_port
        self.udp_port = udp_port

        self.tcp_message = tcp_message or f"HEAD / HTTP/1.1\r\nHost: {target_ip}\r\n\r\n"
        self.udp_message = udp_message
        self.timeout = timeout
        self.check_interval = check_interval

        self._stop_event = threading.Event()

    def run(self):
        logging.info(f"بدء الفحص الذكي للهدف {self.target_ip} باستخدام البروتوكول {self.current_protocol}")
        while not self._stop_event.is_set():
            try:
                blocked = self.analyze_response()
                if blocked:
                    logging.warning(f"تم رصد حجب أو تحدي على البروتوكول {self.current_protocol}")
                else:
                    logging.info(f"البروتوكول {self.current_protocol} يعمل بشكل جيد")
            except Exception as e:
                logging.error(f"خطأ أثناء التحليل: {e}")
            time.sleep(self.check_interval)

    def stop(self):
        self._stop_event.set()

    def analyze_response(self):
        if self.current_protocol == "HTTP":
            return self._analyze_http()
        elif self.current_protocol == "TCP":
            return self._analyze_tcp()
        elif self.current_protocol == "UDP":
            return self._analyze_udp()
        else:
            logging.error(f"بروتوكول غير مدعوم: {self.current_protocol}")
            return False

    def _analyze_http(self):
        try:
            url = f"http://{self.target_ip}:{self.http_port}"
            response = requests.get(url, timeout=self.timeout)
            blocked_status_codes = [403, 429, 503]
            challenge_keywords = ["challenge", "captcha", "access denied", "blocked", "forbidden"]
            response_text = response.text.lower()

            if (response.status_code in blocked_status_codes or
                    any(k in response_text for k in challenge_keywords) or
                    response.elapsed.total_seconds() > 2.0):
                self._increment_blocked()
                return True
            else:
                self._reset_blocked()
                return False

        except requests.RequestException as e:
            logging.warning(f"HTTP - خطأ في الاتصال أو الطلب: {e}")
            self._increment_blocked()
            return True

    def _analyze_tcp(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.target_ip, self.tcp_port))
                sock.sendall(self.tcp_message.encode())
                data = sock.recv(1024)
                response = data.decode(errors='ignore').lower()
                blocked_keywords = ["forbidden", "blocked", "denied", "challenge", "captcha"]

                if any(word in response for word in blocked_keywords):
                    self._increment_blocked()
                    return True
                else:
                    self._reset_blocked()
                    return False

        except socket.error as e:
            logging.warning(f"TCP - خطأ في الاتصال: {e}")
            self._increment_blocked()
            return True

    def _analyze_udp(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(self.timeout)
                sock.sendto(self.udp_message.encode(), (self.target_ip, self.udp_port))
                data, _ = sock.recvfrom(1024)
                response = data.decode(errors='ignore').lower()
                blocked_keywords = ["forbidden", "blocked", "denied", "challenge", "captcha"]

                if any(word in response for word in blocked_keywords):
                    self._increment_blocked()
                    return True
                else:
                    self._reset_blocked()
                    return False

        except socket.error as e:
            logging.warning(f"UDP - خطأ في الاتصال: {e}")
            self._increment_blocked()
            return True

    def _increment_blocked(self):
        self.blocked_count += 1
        if self.blocked_count >= self.max_blocked_before_switch:
            self.switch_protocol()

    def _reset_blocked(self):
        self.blocked_count = 0

    def switch_protocol(self):
        old_protocol = self.current_protocol
        self.current_protocol_index = (self.current_protocol_index + 1) % len(self.protocols)
        self.current_protocol = self.protocols[self.current_protocol_index]
        logging.info(f"تم تغيير البروتوكول من {old_protocol} إلى {self.current_protocol}")
        # إبلاغ محرك الهجوم بتغيير البروتوكول
        if self.control_callback:
            self.control_callback(self.current_protocol)


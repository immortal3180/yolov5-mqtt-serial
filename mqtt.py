import logging
import time

import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(self, broker="124.70.54.142", port=1883, topic="test_A"):
        """初始化MQTT客户端.

        Args:
            broker (str): MQTT服务器地址
            port (int): MQTT服务器端口
            topic (str): 默认订阅主题.
        """
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.connected = False

        # 设置回调函数
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _on_connect(self, client, userdata, flags, rc):
        """连接回调函数."""
        if rc == 0:
            self.connected = True
            self.logger.info("成功连接到MQTT服务器")
            # 连接成功后订阅主题
            self.subscribe(self.topic)
        else:
            self.logger.error(f"连接失败，返回码：{rc}")

    def _on_message(self, client, userdata, msg):
        """消息接收回调函数."""
        try:
            message = msg.payload.decode()
            self.logger.info(f"收到消息 主题:{msg.topic} 内容:{message}")
            # 这里可以添加消息处理逻辑
        except Exception as e:
            self.logger.error(f"消息处理错误：{e!s}")

    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调函数."""
        self.connected = False
        if rc != 0:
            self.logger.warning("意外断开连接，尝试重新连接...")
            self._reconnect()

    def connect(self):
        """连接到MQTT服务器."""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            self.logger.error(f"连接错误：{e!s}")
            return False
        return True

    def _reconnect(self):
        """重新连接."""
        while not self.connected:
            try:
                self.client.reconnect()
                time.sleep(5)
            except Exception as e:
                self.logger.error(f"重连失败：{e!s}")
                time.sleep(5)

    def disconnect(self):
        """断开连接."""
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic=None, message=""):
        """发布消息.

        Args:
            topic (str): 发布主题，如果为None则使用默认主题
            message (str): 要发布的消息

        Returns:
            bool: 发布是否成功.
        """
        if not self.connected:
            self.logger.error("未连接到服务器")
            return False

        try:
            pub_topic = topic if topic else self.topic
            result = self.client.publish(pub_topic, message)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"消息发布成功：{message}")
                return True
            else:
                self.logger.error(f"消息发布失败，错误码：{result.rc}")
                return False
        except Exception as e:
            self.logger.error(f"发布错误：{e!s}")
            return False

    def subscribe(self, topic=None):
        """订阅主题.

        Args:
            topic (str): 要订阅的主题，如果为None则使用默认主题

        Returns:
            bool: 订阅是否成功.
        """
        try:
            sub_topic = topic if topic else self.topic
            result = self.client.subscribe(sub_topic)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"成功订阅主题：{sub_topic}")
                return True
            else:
                self.logger.error(f"订阅失败，错误码：{result[0]}")
                return False
        except Exception as e:
            self.logger.error(f"订阅错误：{e!s}")
            return False


# 使用示例
if __name__ == "__main__":
    # 创建MQTT客户端实例
    mqtt_client = MQTTClient()

    # 连接到服务器
    if mqtt_client.connect():
        # 发布测试消息
        mqtt_client.publish(message="Hello MQTT")

        # 保持程序运行一段时间以接收消息
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("程序终止")
            mqtt_client.disconnect()

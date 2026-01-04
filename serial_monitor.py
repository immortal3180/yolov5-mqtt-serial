#!/usr/bin/env python3
"""
串口监听工具 - 用于观察YOLOv5检测结果发送的串口数据
适用于树莓派5

使用方法:
    1. 硬件连接: 将树莓派的TX连接到USB转TTL的RX，然后USB转TTL插到树莓派
    2. 运行此脚本监听USB转TTL对应的串口
    
    或者使用虚拟串口进行测试（无需硬件）
"""

import serial
import serial.tools.list_ports
import argparse
import time
from datetime import datetime


def list_available_ports():
    """列出所有可用的串口"""
    ports = serial.tools.list_ports.comports()
    print("\n📡 可用串口列表:")
    print("-" * 50)
    if not ports:
        print("  未发现任何串口设备")
    for port in ports:
        print(f"  {port.device}: {port.description}")
    print("-" * 50)
    return [port.device for port in ports]


def monitor_serial(port, baudrate, timeout=1):
    """
    监听串口数据
    
    Args:
        port: 串口设备路径 (如 /dev/ttyUSB0 或 COM3)
        baudrate: 波特率
        timeout: 读取超时时间
    """
    print(f"\n🔌 正在连接串口: {port} @ {baudrate} baud")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"✅ 串口连接成功!")
        print(f"\n📥 开始监听串口数据 (按 Ctrl+C 退出)...")
        print("=" * 60)
        
        message_count = 0
        while True:
            if ser.in_waiting > 0:
                try:
                    # 读取一行数据
                    data = ser.readline()
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    message_count += 1
                    
                    # 尝试解码为字符串
                    try:
                        decoded = data.decode('utf-8').strip()
                        
                        # 解析消息类型
                        if decoded == "start":
                            msg_type = "🔍 未检测到目标"
                            print(f"[{timestamp}] #{message_count:04d} {msg_type}")
                        elif decoded.startswith("(") and decoded.endswith(")"):
                            # 解析坐标
                            coords = decoded[1:-1].split(",")
                            if len(coords) == 2:
                                x, y = coords
                                msg_type = f"🎯 检测到目标 - 中心坐标: X={x}, Y={y}"
                                print(f"[{timestamp}] #{message_count:04d} {msg_type}")
                            else:
                                print(f"[{timestamp}] #{message_count:04d} 📦 原始数据: {decoded}")
                        else:
                            print(f"[{timestamp}] #{message_count:04d} 📦 原始数据: {decoded}")
                            
                    except UnicodeDecodeError:
                        # 如果无法解码，显示十六进制
                        hex_data = data.hex()
                        print(f"[{timestamp}] #{message_count:04d} 🔢 HEX: {hex_data}")
                        
                except Exception as e:
                    print(f"❌ 读取错误: {e}")
            else:
                time.sleep(0.01)  # 短暂休眠，减少CPU占用
                
    except serial.SerialException as e:
        print(f"❌ 串口错误: {e}")
    except KeyboardInterrupt:
        print(f"\n\n📊 统计: 共接收 {message_count} 条消息")
        print("👋 监听已停止")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("🔌 串口已关闭")


def send_test_data(port, baudrate):
    """发送测试数据（用于测试）"""
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"✅ 串口连接成功: {port}")
        
        test_messages = [
            b"start\n",
            b"(320,240)\n",
            b"(150,200)\n",
            b"(500,300)\n",
            b"start\n",
        ]
        
        print("📤 发送测试数据...")
        for msg in test_messages:
            ser.write(msg)
            print(f"  发送: {msg}")
            time.sleep(0.5)
            
        ser.close()
        print("✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="串口监听工具 - 观察YOLOv5检测结果",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 列出可用串口
  python serial_monitor.py --list
  
  # 监听树莓派默认串口
  python serial_monitor.py --port /dev/ttyAMA0
  
  # 监听USB转TTL串口
  python serial_monitor.py --port /dev/ttyUSB0
  
  # Windows下监听COM口
  python serial_monitor.py --port COM3
  
  # 发送测试数据
  python serial_monitor.py --port /dev/ttyUSB0 --test
        """
    )
    
    parser.add_argument("--port", "-p", type=str, default="/dev/ttyAMA0",
                        help="串口设备路径 (默认: /dev/ttyAMA0)")
    parser.add_argument("--baud", "-b", type=int, default=115200,
                        help="波特率 (默认: 115200)")
    parser.add_argument("--list", "-l", action="store_true",
                        help="列出所有可用串口")
    parser.add_argument("--test", "-t", action="store_true",
                        help="发送测试数据")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  🖥️  YOLOv5 串口监听工具")
    print("  适用于树莓派5 串口通信调试")
    print("=" * 60)
    
    if args.list:
        list_available_ports()
        return
    
    if args.test:
        send_test_data(args.port, args.baud)
        return
    
    # 先列出可用串口
    list_available_ports()
    
    # 开始监听
    monitor_serial(args.port, args.baud)


if __name__ == "__main__":
    main()


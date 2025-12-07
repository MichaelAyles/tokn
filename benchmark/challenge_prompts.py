"""
Hard challenge prompts for TOKN benchmark.

These are complex, system-level prompts that test:
- Multi-subsystem integration
- Specific component selection
- Power supply design knowledge
- Real-world electronics experience
"""

import json
from pathlib import Path


CHALLENGE_PROMPTS = [
    {
        "prompt": "Design a synchronous buck converter using TPS54360B controller. Include 22uH inductor (SRP1265A-220M), SS34 Schottky diode, 22uF input caps, 100uF output caps, and proper feedback network with 49.9k and 10k resistors for 5V output from 12-24V input.",
        "prompt_style": "smps_challenge",
        "required_ics": ["TPS54360B"],
        "required_components": ["TPS54360B", "22uH", "SS34", "22uF", "100uF", "49.9k", "10k"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Buck Converter Challenge",
            "subcircuit_tags": ["power", "smps", "buck", "challenge"],
            "subcircuit_components": "TPS54360B, 22uH inductor, SS34 diode, 22uF, 100uF, feedback resistors",
            "file_id": 0,
            "file_name": "challenge",
            "repo": "benchmark/challenges",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a flight computer system with: STM32F405RGT6 processor, BMP280 barometer on I2C, MPU6050 6-axis IMU on I2C, NEO-M8N GPS module on UART, W25Q128 flash for logging on SPI, and AMS1117-3.3 LDO for power. Include all decoupling caps (100nF per IC, 10uF bulk), 8MHz crystal with 20pF load caps, and proper pull-ups on I2C (4.7k).",
        "prompt_style": "system_challenge",
        "required_ics": ["STM32F405RGT6", "BMP280", "MPU6050", "NEO-M8N", "W25Q128", "AMS1117"],
        "required_components": ["STM32F405RGT6", "BMP280", "MPU6050", "NEO-M8N", "W25Q128", "AMS1117", "100nF", "10uF", "8MHz", "20pF", "4.7k"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Flight Computer Challenge",
            "subcircuit_tags": ["embedded", "flight", "sensors", "gps", "challenge"],
            "subcircuit_components": "STM32F405, BMP280, MPU6050, GPS, Flash, LDO",
            "file_id": 0,
            "file_name": "challenge",
            "repo": "benchmark/challenges",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an isolated flyback converter for 5V 2A output from 230VAC mains using TNY290PG controller. Include safety capacitors Y1 (2.2nF) and X2 (100nF), CM choke, fuse, MOV, bridge rectifier (MB10S), opto-isolator (PC817) for feedback, TL431 voltage reference, and transformer with 1:0.1 ratio. Primary inductance 1mH.",
        "prompt_style": "smps_challenge",
        "required_ics": ["TNY290PG", "PC817", "TL431", "MB10S"],
        "required_components": ["TNY290PG", "PC817", "TL431", "MB10S", "2.2nF", "100nF", "1mH"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Isolated Flyback Challenge",
            "subcircuit_tags": ["power", "smps", "flyback", "isolated", "challenge"],
            "subcircuit_components": "TNY290, optocoupler, TL431, bridge rectifier",
            "file_id": 0,
            "file_name": "challenge",
            "repo": "benchmark/challenges",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a Class-D audio amplifier using TPA3116D2. Include 22uF input coupling caps, 680uF output filter caps, 10uH filter inductors (SLF7045T-100M1R0), LC input filter with 100nF and ferrite bead, PVDD decoupling with 1000uF bulk and 100nF ceramic, and proper bootstrap caps (100nF). Support BTL configuration for 2x50W into 4 ohms.",
        "prompt_style": "analog_challenge",
        "required_ics": ["TPA3116D2"],
        "required_components": ["TPA3116D2", "22uF", "680uF", "10uH", "100nF", "1000uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Class-D Amplifier Challenge",
            "subcircuit_tags": ["audio", "amplifier", "class-d", "challenge"],
            "subcircuit_components": "TPA3116D2, LC filters, bootstrap caps",
            "file_id": 0,
            "file_name": "challenge",
            "repo": "benchmark/challenges",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a 4-layer motor driver board with dual DRV8301 gate drivers for 3-phase BLDC control. Include LMZ14201 5V/1A buck for logic power, AS5047P magnetic encoder on SPI, STM32G474 for control with 25MHz HSE crystal, CAN transceiver (SN65HVD230), current sense amplifiers (INA240A2) with 1mOhm shunts, and proper gate drive with 10R gate resistors and TVS protection.",
        "prompt_style": "system_challenge",
        "required_ics": ["DRV8301", "LMZ14201", "AS5047P", "STM32G474", "SN65HVD230", "INA240A2"],
        "required_components": ["DRV8301", "LMZ14201", "AS5047P", "STM32G474", "SN65HVD230", "INA240A2", "25MHz", "1mOhm", "10R"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "BLDC Motor Driver Challenge",
            "subcircuit_tags": ["motor", "bldc", "foc", "challenge"],
            "subcircuit_components": "DRV8301, encoder, current sense, CAN",
            "file_id": 0,
            "file_name": "challenge",
            "repo": "benchmark/challenges",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an ESP32-S3 IoT sensor node with: solar charging (CN3065), LiFePO4 battery management, BME680 environmental sensor (I2C), VEML7700 light sensor (I2C), soil moisture sensor interface (ADC), LoRa module (RFM95W on SPI), deep sleep capability, and LED indicators. Include proper voltage regulation (3.3V from battery using TPS63000 buck-boost), reverse polarity protection, and ESD protection on all external interfaces.",
        "prompt_style": "system_challenge",
        "required_ics": ["ESP32-S3", "CN3065", "BME680", "VEML7700", "RFM95W", "TPS63000"],
        "required_components": ["ESP32-S3", "CN3065", "BME680", "VEML7700", "RFM95W", "TPS63000"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "IoT Sensor Node Challenge",
            "subcircuit_tags": ["iot", "solar", "lora", "sensors", "challenge"],
            "subcircuit_components": "ESP32-S3, solar charger, sensors, LoRa",
            "file_id": 0,
            "file_name": "challenge",
            "repo": "benchmark/challenges",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a precision ADC front-end for 24-bit ADS1256 with programmable gain amplifier (PGA281), anti-aliasing filter (4th order Butterworth at 1kHz using MCP6004), precision 2.5V reference (REF5025), and low-noise LDO power supply (LP5907-3.3). Include proper grounding with analog/digital separation, decoupling (10uF tantalum + 100nF ceramic per rail), and input protection.",
        "prompt_style": "analog_challenge",
        "required_ics": ["ADS1256", "PGA281", "MCP6004", "REF5025", "LP5907"],
        "required_components": ["ADS1256", "PGA281", "MCP6004", "REF5025", "LP5907", "10uF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Precision ADC Challenge",
            "subcircuit_tags": ["adc", "precision", "analog", "challenge"],
            "subcircuit_components": "ADS1256, PGA, op-amp filter, reference",
            "file_id": 0,
            "file_name": "challenge",
            "repo": "benchmark/challenges",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a USB-PD sink with FUSB302 controller, STUSB4500 standalone PD controller, TPS25740 power path controller, ideal diode (LM74700), and 5V/3A buck converter (TPS562200) with 4.7uH inductor and 22uF output caps. Support 5V/9V/12V/15V/20V PD profiles with automatic voltage negotiation.",
        "prompt_style": "power_challenge",
        "required_ics": ["FUSB302", "STUSB4500", "TPS25740", "LM74700", "TPS562200"],
        "required_components": ["FUSB302", "STUSB4500", "TPS25740", "LM74700", "TPS562200", "4.7uH", "22uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "USB-PD Sink Challenge",
            "subcircuit_tags": ["usb", "power-delivery", "charging", "challenge"],
            "subcircuit_components": "FUSB302, STUSB4500, power path, buck",
            "file_id": 0,
            "file_name": "challenge",
            "repo": "benchmark/challenges",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a 6S LiPo battery management system with BQ76940 AFE, external balancing MOSFETs (CSD17575Q3), thermistor inputs (10k NTC), cell voltage sensing with 100nF filtering, charge/discharge FETs (NVMFS6H800NL), pre-charge resistor (100R 5W), and communication via I2C to host MCU. Include proper protection for overvoltage, undervoltage, overcurrent, and overtemperature.",
        "prompt_style": "power_challenge",
        "required_ics": ["BQ76940", "CSD17575Q3", "NVMFS6H800NL"],
        "required_components": ["BQ76940", "CSD17575Q3", "NVMFS6H800NL", "10k", "100nF", "100R"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "BMS Challenge",
            "subcircuit_tags": ["battery", "bms", "lipo", "protection", "challenge"],
            "subcircuit_components": "BQ76940, balancing FETs, protection FETs",
            "file_id": 0,
            "file_name": "challenge",
            "repo": "benchmark/challenges",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an Ethernet-to-RS485 converter with W5500 Ethernet controller, MAX3485 RS485 transceiver, STM32F103C8T6 processor, 25MHz crystal for Ethernet PHY, 8MHz crystal for MCU, RJ45 jack with integrated magnetics (HR911105A), termination resistor (120R switchable), and isolated power for RS485 side using B0505S-1W.",
        "prompt_style": "interface_challenge",
        "required_ics": ["W5500", "MAX3485", "STM32F103C8T6", "B0505S"],
        "required_components": ["W5500", "MAX3485", "STM32F103C8T6", "B0505S", "25MHz", "8MHz", "120R"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Ethernet Gateway Challenge",
            "subcircuit_tags": ["ethernet", "rs485", "gateway", "industrial", "challenge"],
            "subcircuit_components": "W5500, RS485, STM32, isolation",
            "file_id": 0,
            "file_name": "challenge",
            "repo": "benchmark/challenges",
            "score": 10.0
        }
    }
]


def export_challenge_prompts(output_path: str):
    """Export challenge prompts to JSONL."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for p in CHALLENGE_PROMPTS:
            f.write(json.dumps(p, ensure_ascii=False) + '\n')
    print(f"Exported {len(CHALLENGE_PROMPTS)} challenge prompts to {output_path}")


def main():
    base_dir = Path(__file__).parent
    output_path = base_dir / 'challenge_prompts.jsonl'
    export_challenge_prompts(str(output_path))

    print("\nChallenge prompts:")
    for i, p in enumerate(CHALLENGE_PROMPTS):
        print(f"\n{i+1}. [{p['prompt_style']}]")
        print(f"   {p['prompt'][:100]}...")
        print(f"   Required ICs: {p['required_ics']}")


if __name__ == '__main__':
    main()

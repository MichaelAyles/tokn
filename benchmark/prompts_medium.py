"""
TOKN Medium Benchmark Prompts Generator
Generates 100 medium-difficulty circuit design prompts for benchmarking
"""

import json
import os

MEDIUM_PROMPTS = [
    # Category 1: MCU Minimal Systems (10 prompts)
    {
        "prompt": "Design an STM32F103C8T6 minimal system with 8MHz HSE crystal, two 22pF load capacitors, APX803 reset supervisor with 0.1uF capacitor, and 100nF decoupling on VDD",
        "prompt_style": "medium",
        "required_ics": ["STM32F103C8T6", "APX803"],
        "required_components": ["8MHz", "22pF", "22pF", "0.1uF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "STM32 minimal system",
            "subcircuit_tags": ["mcu", "microcontroller", "reset", "crystal"],
            "subcircuit_components": ["STM32F103C8T6", "APX803", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an ATmega328P system with 16MHz crystal, two 18pF capacitors, MCP130T reset IC with pull-up resistor 10k, and three 100nF decoupling capacitors on AVCC, VCC, and AREF",
        "prompt_style": "medium",
        "required_ics": ["ATmega328P", "MCP130T"],
        "required_components": ["16MHz", "18pF", "18pF", "10k", "100nF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "ATmega328P minimal system",
            "subcircuit_tags": ["mcu", "arduino", "reset", "crystal"],
            "subcircuit_components": ["ATmega328P", "MCP130T", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an ESP32-WROOM-32 module system with TPS3840 voltage supervisor on EN pin with 100nF capacitor, 10k pull-up on EN, and 100nF decoupling on 3V3 pin",
        "prompt_style": "medium",
        "required_ics": ["ESP32-WROOM-32", "TPS3840"],
        "required_components": ["100nF", "10k", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "ESP32 minimal system",
            "subcircuit_tags": ["mcu", "wifi", "esp32", "reset"],
            "subcircuit_components": ["ESP32-WROOM-32", "TPS3840", "capacitors", "resistors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an STM32L476RG low-power system with 32.768kHz LSE crystal, two 10pF load capacitors, MAX809 reset supervisor with 1uF capacitor, and 4.7uF decoupling on VDD",
        "prompt_style": "medium",
        "required_ics": ["STM32L476RG", "MAX809"],
        "required_components": ["32.768kHz", "10pF", "10pF", "1uF", "4.7uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "STM32L4 low-power system",
            "subcircuit_tags": ["mcu", "low-power", "rtc", "reset"],
            "subcircuit_components": ["STM32L476RG", "MAX809", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a PIC18F4550 USB system with 20MHz crystal, two 15pF capacitors, DS1233 reset IC with 4.7k resistor, and 220nF plus 10uF tantalum decoupling on VDD",
        "prompt_style": "medium",
        "required_ics": ["PIC18F4550", "DS1233"],
        "required_components": ["20MHz", "15pF", "15pF", "4.7k", "220nF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "PIC18F USB system",
            "subcircuit_tags": ["mcu", "pic", "usb", "reset"],
            "subcircuit_components": ["PIC18F4550", "DS1233", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an NRF52832 Bluetooth system with 32MHz crystal, two 12pF capacitors, TPS3823 supervisor on RESET pin with 100nF capacitor, and 1uF decoupling on VDD",
        "prompt_style": "medium",
        "required_ics": ["NRF52832", "TPS3823"],
        "required_components": ["32MHz", "12pF", "12pF", "100nF", "1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "NRF52 BLE system",
            "subcircuit_tags": ["mcu", "bluetooth", "ble", "reset"],
            "subcircuit_components": ["NRF52832", "TPS3823", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an STM32F407VG system with 25MHz HSE crystal, two 20pF capacitors, ADM708 reset supervisor with 0.1uF capacitor, and 100nF decoupling on each of the 4 VDD pins",
        "prompt_style": "medium",
        "required_ics": ["STM32F407VG", "ADM708"],
        "required_components": ["25MHz", "20pF", "20pF", "0.1uF", "100nF", "100nF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "STM32F4 high-performance system",
            "subcircuit_tags": ["mcu", "high-performance", "reset", "crystal"],
            "subcircuit_components": ["STM32F407VG", "ADM708", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a SAMD21G18A ARM Cortex-M0+ system with 32.768kHz crystal for RTC, two 22pF capacitors, MCP100 reset IC with 10k pull-up, and 100nF decoupling on VDDCORE and VDDANA",
        "prompt_style": "medium",
        "required_ics": ["SAMD21G18A", "MCP100"],
        "required_components": ["32.768kHz", "22pF", "22pF", "10k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "SAMD21 minimal system",
            "subcircuit_tags": ["mcu", "arm", "cortex-m0", "reset"],
            "subcircuit_components": ["SAMD21G18A", "MCP100", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an MSP430F5529 ultra-low-power system with 32.768kHz crystal, two 12pF capacitors, TPS3808 supervisor with 0.47uF capacitor, and 10uF plus 100nF decoupling on DVCC",
        "prompt_style": "medium",
        "required_ics": ["MSP430F5529", "TPS3808"],
        "required_components": ["32.768kHz", "12pF", "12pF", "0.47uF", "10uF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "MSP430 ultra-low-power system",
            "subcircuit_tags": ["mcu", "msp430", "low-power", "reset"],
            "subcircuit_components": ["MSP430F5529", "TPS3808", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a RP2040 dual-core system with 12MHz crystal, two 27pF capacitors, LM809 reset supervisor with 100nF capacitor, and 100nF decoupling on IOVDD, DVDD, VREG_VIN, and USB_VDD",
        "prompt_style": "medium",
        "required_ics": ["RP2040", "LM809"],
        "required_components": ["12MHz", "27pF", "27pF", "100nF", "100nF", "100nF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "RP2040 minimal system",
            "subcircuit_tags": ["mcu", "dual-core", "raspberry-pi", "reset"],
            "subcircuit_components": ["RP2040", "LM809", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },

    # Category 2: Sensor Interfaces (10 prompts)
    {
        "prompt": "Design an I2C sensor interface with BME280 environmental sensor, PCA9306 level shifter for 5V to 3.3V conversion, 10k pull-ups on both sides, and 0.1uF decoupling on each IC",
        "prompt_style": "medium",
        "required_ics": ["BME280", "PCA9306"],
        "required_components": ["10k", "10k", "10k", "10k", "0.1uF", "0.1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "BME280 I2C interface",
            "subcircuit_tags": ["sensor", "i2c", "level-shifter", "environmental"],
            "subcircuit_components": ["BME280", "PCA9306", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an SPI temperature sensor interface with MAX31855 thermocouple IC, 74HC4050 level shifter for 5V MCU, 100nF decoupling on MAX31855, and 10nF ceramic capacitor near thermocouple input",
        "prompt_style": "medium",
        "required_ics": ["MAX31855", "74HC4050"],
        "required_components": ["100nF", "10nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "MAX31855 thermocouple interface",
            "subcircuit_tags": ["sensor", "spi", "thermocouple", "temperature"],
            "subcircuit_components": ["MAX31855", "74HC4050", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an analog sensor interface with MCP3208 8-channel ADC, TLV2462 dual op-amp for signal conditioning with gain of 10 using 10k and 100k resistors, and 0.1uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MCP3208", "TLV2462"],
        "required_components": ["10k", "100k", "10k", "100k", "0.1uF", "0.1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "MCP3208 analog sensor interface",
            "subcircuit_tags": ["sensor", "adc", "op-amp", "analog"],
            "subcircuit_components": ["MCP3208", "TLV2462", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an I2C accelerometer interface with ADXL345, TXS0108E bidirectional level shifter, 2.2k pull-ups on 3.3V side, 4.7k pull-ups on 5V side, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["ADXL345", "TXS0108E"],
        "required_components": ["2.2k", "2.2k", "4.7k", "4.7k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "ADXL345 accelerometer interface",
            "subcircuit_tags": ["sensor", "i2c", "accelerometer", "level-shifter"],
            "subcircuit_components": ["ADXL345", "TXS0108E", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a 1-Wire temperature sensor interface with DS18B20, DS2482-100 I2C to 1-Wire bridge, 4.7k pull-up on 1-Wire bus, 2.2k pull-ups on I2C, and 0.1uF decoupling on DS2482",
        "prompt_style": "medium",
        "required_ics": ["DS18B20", "DS2482-100"],
        "required_components": ["4.7k", "2.2k", "2.2k", "0.1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "DS18B20 1-Wire interface",
            "subcircuit_tags": ["sensor", "1-wire", "i2c", "temperature"],
            "subcircuit_components": ["DS18B20", "DS2482-100", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a pressure sensor interface with BMP388, BSS138 level shifter MOSFETs for I2C, 10k pull-ups to 3.3V on low side, 10k pull-ups to 5V on high side, and 100nF decoupling on BMP388",
        "prompt_style": "medium",
        "required_ics": ["BMP388", "BSS138"],
        "required_components": ["10k", "10k", "10k", "10k", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "BMP388 pressure sensor interface",
            "subcircuit_tags": ["sensor", "i2c", "pressure", "level-shifter"],
            "subcircuit_components": ["BMP388", "BSS138", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a light sensor interface with TSL2561, PCA9517 I2C buffer/repeater for long cable runs, 4.7k pull-ups on sensor side, 2.2k pull-ups on MCU side, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["TSL2561", "PCA9517"],
        "required_components": ["4.7k", "4.7k", "2.2k", "2.2k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "TSL2561 light sensor interface",
            "subcircuit_tags": ["sensor", "i2c", "light", "buffer"],
            "subcircuit_components": ["TSL2561", "PCA9517", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a magnetometer interface with HMC5883L, 74LVC2T45 dual supply level translator, 4.7k pull-ups on I2C lines, 10k on DRDY signal, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["HMC5883L", "74LVC2T45"],
        "required_components": ["4.7k", "4.7k", "10k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "HMC5883L magnetometer interface",
            "subcircuit_tags": ["sensor", "i2c", "magnetometer", "level-translator"],
            "subcircuit_components": ["HMC5883L", "74LVC2T45", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a gas sensor interface with MQ-135 analog sensor, MCP6002 dual op-amp with first stage gain of 5 using 10k and 50k resistors, second stage unity gain buffer, and 100nF decoupling",
        "prompt_style": "medium",
        "required_ics": ["MQ-135", "MCP6002"],
        "required_components": ["10k", "50k", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "MQ-135 gas sensor interface",
            "subcircuit_tags": ["sensor", "analog", "gas", "op-amp"],
            "subcircuit_components": ["MQ-135", "MCP6002", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a humidity sensor interface with SHT31, ISO1540 I2C isolator for electrical isolation, 4.7k pull-ups on both sides, 100nF decoupling on SHT31, and 1uF decoupling on ISO1540",
        "prompt_style": "medium",
        "required_ics": ["SHT31", "ISO1540"],
        "required_components": ["4.7k", "4.7k", "4.7k", "4.7k", "100nF", "1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "SHT31 isolated humidity interface",
            "subcircuit_tags": ["sensor", "i2c", "humidity", "isolation"],
            "subcircuit_components": ["SHT31", "ISO1540", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },

    # Category 3: Motor Drivers (10 prompts)
    {
        "prompt": "Design an H-bridge motor driver with L298N dual driver IC, IR2104 high-side gate driver, 10 ohm gate resistors, 100nF bootstrap capacitor, and 0.1uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["L298N", "IR2104"],
        "required_components": ["10", "10", "100nF", "0.1uF", "0.1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "L298N H-bridge with gate driver",
            "subcircuit_tags": ["motor", "h-bridge", "gate-driver", "power"],
            "subcircuit_components": ["L298N", "IR2104", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a stepper motor driver with DRV8825, TLP281-4 quad optocoupler for isolated inputs, 100 ohm current sense resistor, 100uF bulk capacitor, and 0.1uF decoupling on DRV8825",
        "prompt_style": "medium",
        "required_ics": ["DRV8825", "TLP281-4"],
        "required_components": ["100", "100uF", "0.1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "DRV8825 stepper driver",
            "subcircuit_tags": ["motor", "stepper", "optocoupler", "isolation"],
            "subcircuit_components": ["DRV8825", "TLP281-4", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a brushless DC motor driver with DRV10963, INA180A2 current sense amplifier with 50 milliohm shunt resistor, 10uF input capacitor, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["DRV10963", "INA180A2"],
        "required_components": ["50m", "10uF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "DRV10963 BLDC driver",
            "subcircuit_tags": ["motor", "bldc", "current-sense", "brushless"],
            "subcircuit_components": ["DRV10963", "INA180A2", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a DC motor controller with TB6612FNG dual driver, LM358 dual op-amp for current monitoring with 0.1 ohm sense resistors and 100x gain, and 0.1uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["TB6612FNG", "LM358"],
        "required_components": ["0.1", "0.1", "10k", "1M", "0.1uF", "0.1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "TB6612FNG motor driver with monitoring",
            "subcircuit_tags": ["motor", "dc-motor", "current-sense", "op-amp"],
            "subcircuit_components": ["TB6612FNG", "LM358", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a servo motor driver with PCA9685 16-channel PWM controller, ULN2003A Darlington array for 5V to 6V level shifting, 10k pull-ups on I2C, and 100nF decoupling on PCA9685",
        "prompt_style": "medium",
        "required_ics": ["PCA9685", "ULN2003A"],
        "required_components": ["10k", "10k", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "PCA9685 servo controller",
            "subcircuit_tags": ["motor", "servo", "pwm", "i2c"],
            "subcircuit_components": ["PCA9685", "ULN2003A", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a stepper motor driver with A4988, PC817 optocoupler for step/dir isolation with 220 ohm LED resistors, 0.2 ohm current sense resistors, and 0.1uF decoupling on A4988",
        "prompt_style": "medium",
        "required_ics": ["A4988", "PC817"],
        "required_components": ["220", "220", "0.2", "0.2", "0.1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "A4988 isolated stepper driver",
            "subcircuit_tags": ["motor", "stepper", "optocoupler", "isolation"],
            "subcircuit_components": ["A4988", "PC817", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a motor driver with L293D quad half-H driver, 74HC14 Schmitt trigger for PWM signal conditioning, 1N4148 flyback diodes on each output, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["L293D", "74HC14"],
        "required_components": ["1N4148", "1N4148", "1N4148", "1N4148", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "L293D motor driver",
            "subcircuit_tags": ["motor", "h-bridge", "schmitt-trigger", "protection"],
            "subcircuit_components": ["L293D", "74HC14", "diodes", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a BLDC motor controller with DRV8313, MAX9918 bidirectional current sense amplifier with 10 milliohm shunt, gain setting 20V/V using 100k and 2M resistors, and 0.1uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["DRV8313", "MAX9918"],
        "required_components": ["10m", "100k", "2M", "0.1uF", "0.1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "DRV8313 BLDC with current sense",
            "subcircuit_tags": ["motor", "bldc", "current-sense", "amplifier"],
            "subcircuit_components": ["DRV8313", "MAX9918", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a high-current motor driver with BTS7960 H-bridge, IR2110 high-low side gate driver, 22 ohm gate resistors, 100nF bootstrap capacitors, and 1uF decoupling on IR2110",
        "prompt_style": "medium",
        "required_ics": ["BTS7960", "IR2110"],
        "required_components": ["22", "22", "100nF", "100nF", "1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "BTS7960 high-current motor driver",
            "subcircuit_tags": ["motor", "h-bridge", "gate-driver", "high-current"],
            "subcircuit_components": ["BTS7960", "IR2110", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a stepper motor driver with TMC2209, HCPL-2630 optocoupler for UART isolation with 150 ohm LED resistors, 120 ohm RS sense resistor, and 100nF decoupling on TMC2209",
        "prompt_style": "medium",
        "required_ics": ["TMC2209", "HCPL-2630"],
        "required_components": ["150", "120", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "TMC2209 silent stepper driver",
            "subcircuit_tags": ["motor", "stepper", "uart", "optocoupler"],
            "subcircuit_components": ["TMC2209", "HCPL-2630", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },

    # Category 4: Audio Preamps (10 prompts)
    {
        "prompt": "Design a microphone preamp with MAX4466 electret preamp IC, TL072 dual op-amp for second stage with gain of 20 using 10k and 200k resistors, 10uF coupling capacitors, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MAX4466", "TL072"],
        "required_components": ["10k", "200k", "10uF", "10uF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Microphone preamp",
            "subcircuit_tags": ["audio", "microphone", "op-amp", "preamp"],
            "subcircuit_components": ["MAX4466", "TL072", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a phono preamp with NE5532 dual op-amp for RIAA equalization, THAT1510 ultra-low noise preamp, 75k and 47nF for RIAA pole, 3.3k and 150nF for RIAA zero, and 10uF decoupling",
        "prompt_style": "medium",
        "required_ics": ["NE5532", "THAT1510"],
        "required_components": ["75k", "47nF", "3.3k", "150nF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "RIAA phono preamp",
            "subcircuit_tags": ["audio", "phono", "riaa", "preamp"],
            "subcircuit_components": ["NE5532", "THAT1510", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a balanced line receiver with THAT1240 balanced input IC, OPA2134 dual op-amp for output buffering and filtering, 22k input resistors, 100 ohm output resistors, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["THAT1240", "OPA2134"],
        "required_components": ["22k", "22k", "100", "100", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Balanced line receiver",
            "subcircuit_tags": ["audio", "balanced", "line-input", "preamp"],
            "subcircuit_components": ["THAT1240", "OPA2134", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a guitar preamp with LM833 dual op-amp, SSM2167 microphone preamp with AGC, 1M input impedance, 470pF input capacitor, gain set to 40dB with 100k resistor, and 10uF decoupling",
        "prompt_style": "medium",
        "required_ics": ["LM833", "SSM2167"],
        "required_components": ["1M", "470pF", "100k", "10uF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Guitar preamp with AGC",
            "subcircuit_tags": ["audio", "guitar", "agc", "preamp"],
            "subcircuit_components": ["LM833", "SSM2167", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a studio preamp with OPA1612 ultra-low-noise op-amp, PGA2311 digital volume control, 10k input resistors, 1k output resistors, 22uF coupling capacitors, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["OPA1612", "PGA2311"],
        "required_components": ["10k", "10k", "1k", "1k", "22uF", "22uF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Studio preamp with digital volume",
            "subcircuit_tags": ["audio", "studio", "volume-control", "preamp"],
            "subcircuit_components": ["OPA1612", "PGA2311", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a condenser microphone preamp with INA217 instrumentation amplifier, OPA2604 dual op-amp for phantom power filtering, 6.8k phantom resistors, 10uF coupling capacitors, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["INA217", "OPA2604"],
        "required_components": ["6.8k", "6.8k", "10uF", "10uF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Condenser mic preamp",
            "subcircuit_tags": ["audio", "microphone", "phantom-power", "preamp"],
            "subcircuit_components": ["INA217", "OPA2604", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a DJ mixer input with TL074 quad op-amp, VCA810 voltage-controlled amplifier for fader control, 47k input resistors, 10k gain setting resistors, and 10uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["TL074", "VCA810"],
        "required_components": ["47k", "47k", "10k", "10k", "10uF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "DJ mixer input channel",
            "subcircuit_tags": ["audio", "mixer", "vca", "preamp"],
            "subcircuit_components": ["TL074", "VCA810", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a bass guitar preamp with AD8022 dual op-amp, THAT1646 audio line driver for balanced output, 220k input impedance, 100pF input cap, 600 ohm output resistors, and 100nF decoupling",
        "prompt_style": "medium",
        "required_ics": ["AD8022", "THAT1646"],
        "required_components": ["220k", "100pF", "600", "600", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Bass guitar preamp",
            "subcircuit_tags": ["audio", "bass", "balanced-output", "preamp"],
            "subcircuit_components": ["AD8022", "THAT1646", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a tube mic preamp with OPA2132 op-amp for servo bias, LT1210 high-current buffer for tube heater regulation, 10k bias resistors, 220uF heater capacitor, and 100nF decoupling",
        "prompt_style": "medium",
        "required_ics": ["OPA2132", "LT1210"],
        "required_components": ["10k", "10k", "220uF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Tube mic preamp support",
            "subcircuit_tags": ["audio", "tube", "servo", "preamp"],
            "subcircuit_components": ["OPA2132", "LT1210", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a broadcast preamp with SSM2019 microphone preamp, NJM4580 op-amp for EQ section with 1k and 10k resistors for shelving filter, 47uF coupling capacitors, and 10uF decoupling",
        "prompt_style": "medium",
        "required_ics": ["SSM2019", "NJM4580"],
        "required_components": ["1k", "10k", "47uF", "47uF", "10uF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Broadcast mic preamp",
            "subcircuit_tags": ["audio", "broadcast", "eq", "preamp"],
            "subcircuit_components": ["SSM2019", "NJM4580", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },

    # Category 5: Power Supplies with Monitoring (10 prompts)
    {
        "prompt": "Design a 3.3V power supply with AMS1117-3.3 LDO regulator, INA219 power monitor on I2C with 0.1 ohm shunt resistor, 10uF input and output capacitors, and 100nF decoupling on INA219",
        "prompt_style": "medium",
        "required_ics": ["AMS1117-3.3", "INA219"],
        "required_components": ["0.1", "10uF", "10uF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "3.3V supply with power monitor",
            "subcircuit_tags": ["power", "ldo", "current-monitor", "i2c"],
            "subcircuit_components": ["AMS1117-3.3", "INA219", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a 5V buck converter with LM2596, TLV431 voltage reference for output regulation with 1k and 3.9k divider, 100uH inductor, 220uF output capacitor, and 100nF decoupling on TLV431",
        "prompt_style": "medium",
        "required_ics": ["LM2596", "TLV431"],
        "required_components": ["1k", "3.9k", "100uH", "220uF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "5V buck with precision reference",
            "subcircuit_tags": ["power", "buck", "voltage-reference", "switching"],
            "subcircuit_components": ["LM2596", "TLV431", "resistors", "inductor", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a dual supply with LM317 and LM337 tracking regulators, TLC27M2 op-amp for voltage monitoring with 10k and 100k dividers, 240 ohm programming resistors, and 1uF decoupling on op-amp",
        "prompt_style": "medium",
        "required_ics": ["LM317", "LM337", "TLC27M2"],
        "required_components": ["10k", "100k", "10k", "100k", "240", "240", "1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Dual tracking supply",
            "subcircuit_tags": ["power", "dual-supply", "ldo", "monitoring"],
            "subcircuit_components": ["LM317", "LM337", "TLC27M2", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a battery-backed supply with MCP73831 Li-Ion charger, TPS3431 voltage supervisor for low-battery warning, 2k programming resistor for 500mA charge, and 4.7uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MCP73831", "TPS3431"],
        "required_components": ["2k", "4.7uF", "4.7uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Li-Ion charger with monitoring",
            "subcircuit_tags": ["power", "battery", "charger", "supervisor"],
            "subcircuit_components": ["MCP73831", "TPS3431", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a 12V to 5V converter with MP1584EN buck module, LM393 comparator for overvoltage protection with 10k and 2.2k divider triggering at 5.5V, and 100nF decoupling on LM393",
        "prompt_style": "medium",
        "required_ics": ["MP1584EN", "LM393"],
        "required_components": ["10k", "2.2k", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Buck with overvoltage protection",
            "subcircuit_tags": ["power", "buck", "protection", "comparator"],
            "subcircuit_components": ["MP1584EN", "LM393", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a precision 5V supply with LT1763-5 LDO regulator, LTC2990 quad voltage monitor on I2C, 4.7k pull-ups on I2C, 10uF ceramic output capacitor, and 100nF decoupling on LTC2990",
        "prompt_style": "medium",
        "required_ics": ["LT1763-5", "LTC2990"],
        "required_components": ["4.7k", "4.7k", "10uF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Precision 5V with monitoring",
            "subcircuit_tags": ["power", "ldo", "voltage-monitor", "i2c"],
            "subcircuit_components": ["LT1763-5", "LTC2990", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a hot-swap controller with LTC4217 load switch IC, LM358 op-amp for current limit monitoring, 10 milliohm sense resistor, 100k timer capacitor, and 1uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["LTC4217", "LM358"],
        "required_components": ["10m", "100k", "1uF", "1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Hot-swap controller",
            "subcircuit_tags": ["power", "hot-swap", "current-limit", "protection"],
            "subcircuit_components": ["LTC4217", "LM358", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a switching supply with TPS54331 buck converter, INA3221 triple-channel power monitor, 22uH inductor, 47uF output cap, 100k and 10k divider for 5V output, and 10uF decoupling on INA3221",
        "prompt_style": "medium",
        "required_ics": ["TPS54331", "INA3221"],
        "required_components": ["22uH", "47uF", "100k", "10k", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Buck with triple-channel monitor",
            "subcircuit_tags": ["power", "buck", "monitoring", "i2c"],
            "subcircuit_components": ["TPS54331", "INA3221", "resistors", "inductor", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a load sharing circuit with LM2940-5 low-dropout regulator, LTC4412 ideal diode controller for OR-ing two supplies, 100k resistor for hysteresis, and 22uF output capacitor",
        "prompt_style": "medium",
        "required_ics": ["LM2940-5", "LTC4412"],
        "required_components": ["100k", "22uF", "22uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Load sharing supply",
            "subcircuit_tags": ["power", "load-sharing", "ideal-diode", "redundancy"],
            "subcircuit_components": ["LM2940-5", "LTC4412", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a POE supply with LM5072 POE controller, LNK304P flyback controller for isolated 5V output, 10 ohm gate resistor, 100nF snubber capacitor, and 1uF decoupling on LM5072",
        "prompt_style": "medium",
        "required_ics": ["LM5072", "LNK304P"],
        "required_components": ["10", "100nF", "1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "POE power supply",
            "subcircuit_tags": ["power", "poe", "flyback", "isolation"],
            "subcircuit_components": ["LM5072", "LNK304P", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },

    # Category 6: Communication Interfaces (10 prompts)
    {
        "prompt": "Design an RS485 interface with MAX485 transceiver, ADUM1201 digital isolator for galvanic isolation, 120 ohm termination resistor, 10k bias resistors, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MAX485", "ADUM1201"],
        "required_components": ["120", "10k", "10k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Isolated RS485 interface",
            "subcircuit_tags": ["communication", "rs485", "isolation", "differential"],
            "subcircuit_components": ["MAX485", "ADUM1201", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a CAN bus interface with MCP2551 CAN transceiver, SI8421 isolated CAN transceiver, 120 ohm termination, 10k bias resistors to split termination, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MCP2551", "SI8421"],
        "required_components": ["120", "10k", "10k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Isolated CAN interface",
            "subcircuit_tags": ["communication", "can", "isolation", "automotive"],
            "subcircuit_components": ["MCP2551", "SI8421", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a LoRa wireless interface with RFM95W module, TXS0108E level shifter for 5V to 3.3V SPI signals, 10k pull-ups on SPI lines, 10uF decoupling on RFM95W, and 100nF on level shifter",
        "prompt_style": "medium",
        "required_ics": ["RFM95W", "TXS0108E"],
        "required_components": ["10k", "10k", "10k", "10uF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "LoRa wireless interface",
            "subcircuit_tags": ["communication", "lora", "wireless", "spi"],
            "subcircuit_components": ["RFM95W", "TXS0108E", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an Ethernet interface with ENC28J60 Ethernet controller, HR911105A RJ45 connector with integrated magnetics, 25MHz crystal, two 22pF load capacitors, and 100nF decoupling on ENC28J60",
        "prompt_style": "medium",
        "required_ics": ["ENC28J60", "HR911105A"],
        "required_components": ["25MHz", "22pF", "22pF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "SPI Ethernet interface",
            "subcircuit_tags": ["communication", "ethernet", "spi", "network"],
            "subcircuit_components": ["ENC28J60", "HR911105A", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a Zigbee interface with CC2530 wireless MCU, SN74LVC1T45 single-bit level translator for antenna control, 32MHz crystal, two 10pF capacitors, and 100nF decoupling on CC2530",
        "prompt_style": "medium",
        "required_ics": ["CC2530", "SN74LVC1T45"],
        "required_components": ["32MHz", "10pF", "10pF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Zigbee wireless interface",
            "subcircuit_tags": ["communication", "zigbee", "wireless", "iot"],
            "subcircuit_components": ["CC2530", "SN74LVC1T45", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an RS232 interface with MAX232 level converter, SP3232 RS232 transceiver for extra channels, four 1uF charge pump capacitors on MAX232, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MAX232", "SP3232"],
        "required_components": ["1uF", "1uF", "1uF", "1uF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Dual RS232 interface",
            "subcircuit_tags": ["communication", "rs232", "serial", "level-converter"],
            "subcircuit_components": ["MAX232", "SP3232", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a ModBus interface with MAX13487E RS485 transceiver with extended ESD protection, ADuM1250 I2C isolator for configuration, 120 ohm termination, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MAX13487E", "ADuM1250"],
        "required_components": ["120", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "ModBus RTU interface",
            "subcircuit_tags": ["communication", "modbus", "rs485", "isolation"],
            "subcircuit_components": ["MAX13487E", "ADuM1250", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a Bluetooth interface with HC-05 Bluetooth module, 74HC125 quad buffer for 5V to 3.3V level shifting on UART, 10k voltage divider resistors, and 100nF decoupling on buffer",
        "prompt_style": "medium",
        "required_ics": ["HC-05", "74HC125"],
        "required_components": ["10k", "10k", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Bluetooth UART interface",
            "subcircuit_tags": ["communication", "bluetooth", "uart", "wireless"],
            "subcircuit_components": ["HC-05", "74HC125", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an I2C isolator with ISO1541 bidirectional I2C isolator, PCA9615 I2C bus extender for long cables, 2.2k pull-ups on local side, 4.7k pull-ups on remote side, and 1uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["ISO1541", "PCA9615"],
        "required_components": ["2.2k", "2.2k", "4.7k", "4.7k", "1uF", "1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Isolated I2C extender",
            "subcircuit_tags": ["communication", "i2c", "isolation", "extender"],
            "subcircuit_components": ["ISO1541", "PCA9615", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a WiFi interface with ESP8266-12E module, AMS1117-3.3 LDO for power, 10k pull-up on CH_PD, 10k pull-down on GPIO15, 10uF and 100nF decoupling capacitors on both ICs",
        "prompt_style": "medium",
        "required_ics": ["ESP8266-12E", "AMS1117-3.3"],
        "required_components": ["10k", "10k", "10uF", "100nF", "10uF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "WiFi interface with power",
            "subcircuit_tags": ["communication", "wifi", "wireless", "esp8266"],
            "subcircuit_components": ["ESP8266-12E", "AMS1117-3.3", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },

    # Category 7: DAC/ADC Front-ends (10 prompts)
    {
        "prompt": "Design a precision ADC front-end with ADS1115 16-bit ADC, REF3033 3.3V voltage reference, LMV324 quad op-amp for input buffering with unity gain, and 100nF decoupling on all three ICs",
        "prompt_style": "medium",
        "required_ics": ["ADS1115", "REF3033", "LMV324"],
        "required_components": ["100nF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "16-bit ADC with reference",
            "subcircuit_tags": ["adc", "voltage-reference", "precision", "i2c"],
            "subcircuit_components": ["ADS1115", "REF3033", "LMV324", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a DAC output stage with MCP4725 12-bit DAC, OPA2277 precision op-amp for buffering and gain of 2 using 10k resistors, 10uF output capacitor, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MCP4725", "OPA2277"],
        "required_components": ["10k", "10k", "10uF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "12-bit DAC with buffer",
            "subcircuit_tags": ["dac", "op-amp", "precision", "i2c"],
            "subcircuit_components": ["MCP4725", "OPA2277", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a high-speed ADC with AD7606 8-channel simultaneous sampling ADC, LT1021-5 precision voltage reference, 10uF bypass on reference, 100nF decoupling on ADC, and 1k series resistors on inputs",
        "prompt_style": "medium",
        "required_ics": ["AD7606", "LT1021-5"],
        "required_components": ["10uF", "100nF", "1k", "1k", "1k", "1k"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "8-channel simultaneous ADC",
            "subcircuit_tags": ["adc", "voltage-reference", "high-speed", "multichannel"],
            "subcircuit_components": ["AD7606", "LT1021-5", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a bipolar DAC with DAC8552 dual 16-bit DAC, OPA2188 zero-drift op-amp for inverting output stage with 10k feedback resistors, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["DAC8552", "OPA2188"],
        "required_components": ["10k", "10k", "10k", "10k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Dual 16-bit bipolar DAC",
            "subcircuit_tags": ["dac", "op-amp", "bipolar", "precision"],
            "subcircuit_components": ["DAC8552", "OPA2188", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an ADC with anti-aliasing filter using MCP3561 24-bit delta-sigma ADC, MAX7404 8th-order lowpass filter with 10kHz cutoff, 10k input resistor, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MCP3561", "MAX7404"],
        "required_components": ["10k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "24-bit ADC with anti-aliasing",
            "subcircuit_tags": ["adc", "filter", "delta-sigma", "precision"],
            "subcircuit_components": ["MCP3561", "MAX7404", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a current output DAC with AD5412 quad 12-bit DAC, LM334 current source for calibration, 100 ohm sense resistor, 10uF output capacitors, and 100nF decoupling on AD5412",
        "prompt_style": "medium",
        "required_ics": ["AD5412", "LM334"],
        "required_components": ["100", "10uF", "10uF", "10uF", "10uF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Quad current-output DAC",
            "subcircuit_tags": ["dac", "current-output", "calibration", "industrial"],
            "subcircuit_components": ["AD5412", "LM334", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a ratiometric ADC with ADS1220 24-bit ADC, LM4040-2.5 precision shunt reference, 1k bias resistor for reference, 10uF bypass capacitor, and 100nF decoupling on ADS1220",
        "prompt_style": "medium",
        "required_ics": ["ADS1220", "LM4040-2.5"],
        "required_components": ["1k", "10uF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Ratiometric 24-bit ADC",
            "subcircuit_tags": ["adc", "voltage-reference", "ratiometric", "precision"],
            "subcircuit_components": ["ADS1220", "LM4040-2.5", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a differential ADC front-end with LTC2492 24-bit ADC, INA128 instrumentation amplifier with gain of 10 using 5.49k resistor, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["LTC2492", "INA128"],
        "required_components": ["5.49k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Differential ADC front-end",
            "subcircuit_tags": ["adc", "instrumentation-amplifier", "differential", "precision"],
            "subcircuit_components": ["LTC2492", "INA128", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a DAC with output filter using TLV5638 dual 12-bit DAC, UAF42 universal active filter configured as 4th-order Butterworth lowpass with 1kHz cutoff, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["TLV5638", "UAF42"],
        "required_components": ["100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "DAC with reconstruction filter",
            "subcircuit_tags": ["dac", "filter", "lowpass", "reconstruction"],
            "subcircuit_components": ["TLV5638", "UAF42", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a high-precision ADC with AD7124-8 24-bit ADC, ADR4525 2.5V ultra-precision reference with 10uF and 100nF decoupling, 100 ohm resistor for reference drive, and 100nF on ADC",
        "prompt_style": "medium",
        "required_ics": ["AD7124-8", "ADR4525"],
        "required_components": ["10uF", "100nF", "100", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Ultra-precision ADC system",
            "subcircuit_tags": ["adc", "voltage-reference", "ultra-precision", "spi"],
            "subcircuit_components": ["AD7124-8", "ADR4525", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },

    # Category 8: Display Drivers (10 prompts)
    {
        "prompt": "Design an LCD display interface with HD44780 character LCD controller, PCF8574 I2C expander for 4-bit mode, 10k contrast potentiometer, 220 ohm LED backlight resistor, and 100nF decoupling on PCF8574",
        "prompt_style": "medium",
        "required_ics": ["HD44780", "PCF8574"],
        "required_components": ["10k", "220", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "I2C character LCD interface",
            "subcircuit_tags": ["display", "lcd", "i2c", "character"],
            "subcircuit_components": ["HD44780", "PCF8574", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an OLED display driver with SSD1306 128x64 OLED controller, MCP4531 digital potentiometer for contrast control via I2C, 10k pull-ups on I2C, and 4.7uF decoupling on SSD1306",
        "prompt_style": "medium",
        "required_ics": ["SSD1306", "MCP4531"],
        "required_components": ["10k", "10k", "4.7uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "OLED display with digital contrast",
            "subcircuit_tags": ["display", "oled", "i2c", "contrast"],
            "subcircuit_components": ["SSD1306", "MCP4531", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a TFT display interface with ILI9341 TFT controller, 74HC4050 hex buffer for 5V to 3.3V level shifting on SPI, 100nF decoupling on both ICs, and 10uF bulk capacitor on display",
        "prompt_style": "medium",
        "required_ics": ["ILI9341", "74HC4050"],
        "required_components": ["100nF", "100nF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "SPI TFT display interface",
            "subcircuit_tags": ["display", "tft", "spi", "level-shifter"],
            "subcircuit_components": ["ILI9341", "74HC4050", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a 7-segment display driver with MAX7219 LED driver, 74HC595 shift register for additional outputs, 10k ISET resistor on MAX7219, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MAX7219", "74HC595"],
        "required_components": ["10k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "7-segment display controller",
            "subcircuit_tags": ["display", "7-segment", "led", "spi"],
            "subcircuit_components": ["MAX7219", "74HC595", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an E-ink display interface with SSD1680 E-paper controller, TPS65185 PMIC for E-ink power with 4.7uF output capacitors, 100nF decoupling on SSD1680, and 10uF on TPS65185",
        "prompt_style": "medium",
        "required_ics": ["SSD1680", "TPS65185"],
        "required_components": ["4.7uF", "4.7uF", "4.7uF", "100nF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "E-ink display driver",
            "subcircuit_tags": ["display", "e-ink", "e-paper", "pmic"],
            "subcircuit_components": ["SSD1680", "TPS65185", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an LED matrix driver with HT16K33 LED controller with built-in keyscan, TLC5940 PWM LED driver for brightness control, 2.2k IREF resistor on TLC5940, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["HT16K33", "TLC5940"],
        "required_components": ["2.2k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "LED matrix with PWM",
            "subcircuit_tags": ["display", "led-matrix", "pwm", "i2c"],
            "subcircuit_components": ["HT16K33", "TLC5940", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a VGA output circuit with THS7316 video amplifier, 74HC4040 binary counter for pixel clock division, 75 ohm termination resistors on RGB outputs, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["THS7316", "74HC4040"],
        "required_components": ["75", "75", "75", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "VGA video output",
            "subcircuit_tags": ["display", "vga", "video", "analog"],
            "subcircuit_components": ["THS7316", "74HC4040", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a touchscreen controller with FT6236 capacitive touch IC, TCA9548A I2C multiplexer for multiple displays, 4.7k pull-ups on each I2C channel, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["FT6236", "TCA9548A"],
        "required_components": ["4.7k", "4.7k", "4.7k", "4.7k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Multi-display touch controller",
            "subcircuit_tags": ["display", "touchscreen", "i2c", "multiplexer"],
            "subcircuit_components": ["FT6236", "TCA9548A", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design an LCD backlight driver with CAT4238 white LED driver, LM358 op-amp for PWM dimming control with 100k feedback resistor, 0.1 ohm current sense resistor, and 4.7uF output capacitor",
        "prompt_style": "medium",
        "required_ics": ["CAT4238", "LM358"],
        "required_components": ["100k", "0.1", "4.7uF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "LED backlight driver",
            "subcircuit_tags": ["display", "backlight", "led-driver", "pwm"],
            "subcircuit_components": ["CAT4238", "LM358", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a dot matrix display with AS1108 LED driver, CD4017 decade counter for row scanning, 220 ohm current limit resistors per column, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["AS1108", "CD4017"],
        "required_components": ["220", "220", "220", "220", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Dot matrix LED display",
            "subcircuit_tags": ["display", "led", "matrix", "scanning"],
            "subcircuit_components": ["AS1108", "CD4017", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },

    # Category 9: USB Interfaces (10 prompts)
    {
        "prompt": "Design a USB-UART interface with FT232RL USB-UART bridge, TPD4E05U ESD protection IC on USB lines, 27 ohm series resistors on D+/D-, 10uF decoupling on FT232RL, and 100nF on TPD4E05U",
        "prompt_style": "medium",
        "required_ics": ["FT232RL", "TPD4E05U"],
        "required_components": ["27", "27", "10uF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "USB-UART with ESD protection",
            "subcircuit_tags": ["usb", "uart", "esd", "bridge"],
            "subcircuit_components": ["FT232RL", "TPD4E05U", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a USB hub with FE1.1s 4-port USB hub controller, USBLC6-2 dual ESD suppressor per port, 15k pull-down resistors on D+/D- per port, and 100nF decoupling on hub IC",
        "prompt_style": "medium",
        "required_ics": ["FE1.1s", "USBLC6-2"],
        "required_components": ["15k", "15k", "15k", "15k", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "4-port USB hub",
            "subcircuit_tags": ["usb", "hub", "esd", "multiport"],
            "subcircuit_components": ["FE1.1s", "USBLC6-2", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a USB-SPI bridge with CH341A USB-SPI/I2C converter, PRTR5V0U2X ESD protection on USB, 4.7k pull-ups on I2C lines, 22 ohm series resistors on D+/D-, and 100nF decoupling on CH341A",
        "prompt_style": "medium",
        "required_ics": ["CH341A", "PRTR5V0U2X"],
        "required_components": ["4.7k", "4.7k", "22", "22", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "USB-SPI/I2C bridge",
            "subcircuit_tags": ["usb", "spi", "i2c", "bridge"],
            "subcircuit_components": ["CH341A", "PRTR5V0U2X", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a USB Type-C interface with FUSB302 USB-C controller, STUSB4500 USB PD controller for power delivery negotiation, 5.1k CC resistors, and 4.7uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["FUSB302", "STUSB4500"],
        "required_components": ["5.1k", "5.1k", "4.7uF", "4.7uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "USB Type-C PD interface",
            "subcircuit_tags": ["usb", "usb-c", "power-delivery", "pd"],
            "subcircuit_components": ["FUSB302", "STUSB4500", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a USB isolator with ADuM4160 USB isolator, SI8621 isolated DC-DC converter for power, 100nF decoupling on ADuM4160, and 10uF input/output capacitors on SI8621",
        "prompt_style": "medium",
        "required_ics": ["ADuM4160", "SI8621"],
        "required_components": ["100nF", "10uF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Isolated USB interface",
            "subcircuit_tags": ["usb", "isolation", "galvanic", "dc-dc"],
            "subcircuit_components": ["ADuM4160", "SI8621", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a USB-CAN interface with MCP2515 CAN controller with SPI, MCP2551 CAN transceiver, 120 ohm termination, 16MHz crystal with 22pF capacitors, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MCP2515", "MCP2551"],
        "required_components": ["120", "16MHz", "22pF", "22pF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "USB-CAN bridge",
            "subcircuit_tags": ["usb", "can", "automotive", "bridge"],
            "subcircuit_components": ["MCP2515", "MCP2551", "resistors", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a USB audio interface with PCM2902 USB audio codec, TPA6132A2 stereo headphone amplifier, 10uF coupling capacitors, 100 ohm output resistors, and 10uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["PCM2902", "TPA6132A2"],
        "required_components": ["10uF", "10uF", "100", "100", "10uF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "USB audio codec",
            "subcircuit_tags": ["usb", "audio", "codec", "headphone"],
            "subcircuit_components": ["PCM2902", "TPA6132A2", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a USB charging port with TPS2511 USB charging controller, SMBJ5.0A TVS diode for overvoltage protection, 24.9k resistor for 2.4A limit, and 10uF decoupling on TPS2511",
        "prompt_style": "medium",
        "required_ics": ["TPS2511", "SMBJ5.0A"],
        "required_components": ["24.9k", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "USB charging port",
            "subcircuit_tags": ["usb", "charging", "protection", "current-limit"],
            "subcircuit_components": ["TPS2511", "SMBJ5.0A", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a USB OTG interface with MAX3421E USB host controller, IP4234CZ8 quad ESD suppressor, 15k pull-downs on D+/D-, 12MHz crystal with 18pF capacitors, and 100nF decoupling on MAX3421E",
        "prompt_style": "medium",
        "required_ics": ["MAX3421E", "IP4234CZ8"],
        "required_components": ["15k", "15k", "12MHz", "18pF", "18pF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "USB OTG host controller",
            "subcircuit_tags": ["usb", "otg", "host", "esd"],
            "subcircuit_components": ["MAX3421E", "IP4234CZ8", "resistors", "crystal", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a USB-RS485 converter with FT232RQ USB-UART IC, MAX3485 RS485 transceiver, 120 ohm termination, automatic direction control with 10k pull-up, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["FT232RQ", "MAX3485"],
        "required_components": ["120", "10k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "USB-RS485 converter",
            "subcircuit_tags": ["usb", "rs485", "uart", "industrial"],
            "subcircuit_components": ["FT232RQ", "MAX3485", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },

    # Category 10: Battery Charging (10 prompts)
    {
        "prompt": "Design a Li-Ion battery charger with BQ24072 charge controller, MAX17043 fuel gauge for SOC monitoring on I2C, 1.2k programming resistor for 950mA charge, and 10uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["BQ24072", "MAX17043"],
        "required_components": ["1.2k", "10uF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Li-Ion charger with fuel gauge",
            "subcircuit_tags": ["battery", "charger", "fuel-gauge", "li-ion"],
            "subcircuit_components": ["BQ24072", "MAX17043", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a solar battery charger with CN3791 MPPT solar charger, ACS712 current sensor for load monitoring, 0.05 ohm sense resistor, 22uF input capacitor, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["CN3791", "ACS712"],
        "required_components": ["0.05", "22uF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Solar MPPT battery charger",
            "subcircuit_tags": ["battery", "solar", "mppt", "current-sense"],
            "subcircuit_components": ["CN3791", "ACS712", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a multi-cell charger with BQ76920 3-5 cell battery monitor, LTC4015 buck-boost battery charger, 2 milliohm shunt resistor, 10k thermistor for temperature sensing, and 4.7uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["BQ76920", "LTC4015"],
        "required_components": ["2m", "10k", "4.7uF", "4.7uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Multi-cell Li-Ion charger",
            "subcircuit_tags": ["battery", "charger", "multi-cell", "bms"],
            "subcircuit_components": ["BQ76920", "LTC4015", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a wireless charging receiver with BQ51003 Qi receiver IC, TPS63020 buck-boost converter for battery charging, 22uH inductor, 22uF output capacitor, and 10uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["BQ51003", "TPS63020"],
        "required_components": ["22uH", "22uF", "10uF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Wireless Qi charger",
            "subcircuit_tags": ["battery", "wireless", "qi", "inductive"],
            "subcircuit_components": ["BQ51003", "TPS63020", "inductor", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a NiMH battery charger with MAX713 NiMH charger IC, LM35 temperature sensor for thermal monitoring, 10k voltage divider for cell count detection, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["MAX713", "LM35"],
        "required_components": ["10k", "10k", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "NiMH battery charger",
            "subcircuit_tags": ["battery", "charger", "nimh", "temperature"],
            "subcircuit_components": ["MAX713", "LM35", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a supercapacitor charger with LTC3225 supercap charger, TPS3813 voltage supervisor for under-voltage lockout, 100k current limit resistor, and 10uF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["LTC3225", "TPS3813"],
        "required_components": ["100k", "10uF", "10uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Supercapacitor charger",
            "subcircuit_tags": ["battery", "supercapacitor", "charger", "energy-storage"],
            "subcircuit_components": ["LTC3225", "TPS3813", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a USB-C PD battery charger with STUSB4500 USB PD controller, BQ25703A buck-boost charger, 5 milliohm sense resistors, 10uH inductor, and 22uF capacitors on both ICs",
        "prompt_style": "medium",
        "required_ics": ["STUSB4500", "BQ25703A"],
        "required_components": ["5m", "5m", "10uH", "22uF", "22uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "USB-C PD fast charger",
            "subcircuit_tags": ["battery", "usb-c", "power-delivery", "charger"],
            "subcircuit_components": ["STUSB4500", "BQ25703A", "resistors", "inductor", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a lead-acid battery charger with LT1510 switching charger controller, LT1635 voltage reference for precision regulation, 330uH inductor, 220uF output capacitor, and 100nF decoupling on both ICs",
        "prompt_style": "medium",
        "required_ics": ["LT1510", "LT1635"],
        "required_components": ["330uH", "220uF", "100nF", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Lead-acid battery charger",
            "subcircuit_tags": ["battery", "charger", "lead-acid", "automotive"],
            "subcircuit_components": ["LT1510", "LT1635", "inductor", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a battery balancing circuit with LTC6804 12-cell battery monitor, SI7336ADP balancing MOSFETs, 100 ohm balancing resistors per cell, and 100nF decoupling on LTC6804",
        "prompt_style": "medium",
        "required_ics": ["LTC6804", "SI7336ADP"],
        "required_components": ["100", "100", "100", "100", "100nF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Multi-cell battery balancer",
            "subcircuit_tags": ["battery", "bms", "balancing", "multi-cell"],
            "subcircuit_components": ["LTC6804", "SI7336ADP", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
    {
        "prompt": "Design a battery protection circuit with DW01A battery protection IC, FS8205A dual MOSFET for over-current protection, 100 milliohm sense resistor, 0.1uF and 1uF decoupling capacitors",
        "prompt_style": "medium",
        "required_ics": ["DW01A", "FS8205A"],
        "required_components": ["100m", "0.1uF", "1uF"],
        "reference_tokn": "",
        "metadata": {
            "subcircuit_name": "Li-Ion protection circuit",
            "subcircuit_tags": ["battery", "protection", "over-current", "li-ion"],
            "subcircuit_components": ["DW01A", "FS8205A", "resistors", "capacitors"],
            "file_id": 0,
            "file_name": "benchmark",
            "repo": "benchmark/medium",
            "score": 10.0
        }
    },
]


def export_medium_prompts(output_path):
    """
    Export medium benchmark prompts to JSONL format

    Args:
        output_path: Path to output JSONL file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write prompts to JSONL file
    with open(output_path, 'w') as f:
        for prompt in MEDIUM_PROMPTS:
            f.write(json.dumps(prompt) + '\n')

    print(f"Exported {len(MEDIUM_PROMPTS)} medium prompts to {output_path}")


def main():
    """Main function to export prompts"""
    output_path = os.path.join("benchmark", "prompts_medium.jsonl")
    export_medium_prompts(output_path)


if __name__ == "__main__":
    main()

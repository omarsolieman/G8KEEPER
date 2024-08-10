---

# 🔒G8KEEPER The Offline & Secure Hardware Password Manager

This project is an **Offline & Secure Hardware Password Manager** based on the RP2040 chip. Designed to be secure, portable, and easy to use, it ensures that your passwords are always safe and accessible only to you. With robust encryption and hardware-level protection, your data remains secure even when you're on the go.

## 🚀 Features

- **RP2040 Chip**: Powered by the powerful RP2040 microcontroller.
- **16MB Storage**: Ample space to securely store your passwords.
- **USB-C & Battery Powered**: Flexibility to operate via USB-C or battery for portability.
- **Tiny Form Factor**: Compact design that fits in your pocket.
- **Secure Encryption**:
  - PBKDF2-HMAC-SHA256 for key derivation.
  - AES256 for password encryption.
- **Simple Interface**: Easy to use with a minimalistic design.
- **OLED Display**: Integrated display for viewing and managing passwords.
- **Physical Buttons**: Intuitive physical controls for navigation and operation.

## 🛠️ Setup Instructions

1. **Hardware Assembly**:
   - Connect the RP2040 chip to the OLED display and other peripherals as per the schematic.
   - Ensure the battery is properly connected if you intend to use the device in portable mode.

2. **Software Installation**:
   - Clone this repository to your local machine:
     ```bash
     git clone https://github.com/yourusername/offline-password-manager.git
     ```
   - Flash the provided firmware to the RP2040 chip using your preferred method.

3. **Configuration**:
   - Open the `config.py` file and set your preferences for encryption keys, display settings, etc.
   - Upload the configuration to the device.

4. **Password Management**:
   - Store your passwords in the `passwords.csv` file. Each entry should be formatted as:
     ```
     service_name,username,password
     ```
   - The device will encrypt and securely store this information.

## 🔑 Usage

1. **Power On**: Power the device using USB-C or the battery.
2. **Navigate Menu**: Use the physical buttons to navigate through the menu.
3. **View Passwords**: Select the "View Passwords" option to see your stored credentials.
4. **Generate Passwords**: Use the "Generate Password" feature to create new, secure passwords.
5. **Lock Screen**: Secure the device when not in use by enabling the lock screen.

## 📷 Screenshots

![Device in Action](path-to-your-image-1.png)
*Caption: The device displaying the main menu.*

![Compact Design](path-to-your-image-2.png)
*Caption: A close-up of the hardware setup.*

## 🔒 Security

This device is built with security in mind. All passwords are encrypted using AES256, and the keys are derived using PBKDF2-HMAC-SHA256, ensuring robust protection against unauthorized access.

## 🤝 Contributing

We welcome contributions! Please feel free to submit pull requests or open issues to improve the project.

## 🧑‍💻 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0) - see the [LICENSE](LICENSE) file for details.

---

Let me know if you'd like any changes or additional sections! You can replace the placeholder paths with actual image links or files as needed.

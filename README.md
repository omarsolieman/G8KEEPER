# 🔒 G8KEEPER
### The Offline & Secure Hardware Password Manager

> A completely offline hardware password manager that puts you in control of your security

## 🎯 About
G8KEEPER is a DIY hardware password manager based on the RP2040 chip. Designed to be secure, portable, and easy to use, it ensures that your passwords are always safe and accessible only to you. With robust encryption and hardware-level protection, your data remains secure even when you're on the go.

## ⭐ Key Features
* **💾 Secure Storage**
  * 16MB dedicated storage space
  * Hardware-level encryption
  * Complete offline operation
  * No wireless connectivity = No remote attacks

* **🔐 Advanced Security**
  * PBKDF2-HMAC-SHA256 key derivation
  * AES256 password encryption
  * Pattern-based unlock (387M combinations)
  * Auto-lock functionality

* **🎮 User Experience**
  * Simple joystick + 2 button interface
  * OLED display for clear visibility
  * Intuitive menu navigation
  * Password generation capability

* **⚡ Power & Connectivity**
  * USB-C connection
  * Battery powered operation
  * Long battery life
  * No cables needed for viewing

## 🛠️ Hardware Components
* RP2040 microcontroller
* 128x64 SSD1306 OLED display
* Joystick for navigation
* 2 tactile buttons
* Custom 3D printed enclosure
* Battery management system

## 📱 Interface
```
Main Menu
├── View Passwords
├── Add New Password
├── Generate Password
├── Settings
└── Lock Device
```

## 🔧 Setup Guide
1. **Hardware Assembly**
   ```
   1. Print the 3D enclosure parts
   2. Wire the components following schematic
   3. Test connections before assembly
   4. Complete final assembly
   ```

2. **Software Installation**
   ```bash
   git clone https://github.com/yourusername/g8keeper.git
   cd g8keeper
   # Follow firmware flashing instructions
   ```

3. **Initial Configuration**
   ```python
   # config.py example
   DISPLAY_TIMEOUT = 30  # seconds
   AUTO_LOCK = True
   PATTERN_LENGTH = 6    # unlock pattern length
   ```

## 💻 Development
Currently working on:
- [ ] Enhanced encryption options
- [ ] Improved battery life
- [ ] Smaller form factor
- [ ] Additional authentication methods

## 🤝 Contributing
Contributions are welcome! Please feel free to submit issues and pull requests.

## 📜 License
This project is licensed under GPL-3.0 - see [LICENSE](LICENSE) for details.

## ⚠️ Security Notice
While G8KEEPER is designed to be secure, it requires physical security. Keep the device safe and protected from physical tampering.

## 🙏 Acknowledgments
* Raspberry Pi Foundation for the RP2040
* CircuitPython community
* Open-source security tools

## 📞 Contact
* GitHub Issues: [Create an issue](https://github.com/yourusername/g8keeper/issues)

---
*Built with ❤️ for security and privacy*

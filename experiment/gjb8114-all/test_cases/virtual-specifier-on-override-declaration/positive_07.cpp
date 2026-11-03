#include <iostream>

class Device {
public:
    virtual void reset() noexcept;
    virtual ~Device() = default;
};

void Device::reset() noexcept {}

class Sensor : public Device {
public:
    virtual void reset() noexcept;
};

void Sensor::reset() noexcept {}

int main() {
    Sensor s;
    Device& d = s;
    d.reset();
    return 0;
}

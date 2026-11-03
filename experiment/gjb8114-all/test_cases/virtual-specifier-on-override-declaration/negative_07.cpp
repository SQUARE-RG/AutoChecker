#include <iostream>

class Device {
public:
    virtual void reset() noexcept;
    virtual ~Device() = default;
};

void Device::reset() noexcept {}

class Sensor : public Device {
public:
    void reset() noexcept; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-2]
};

void Sensor::reset() noexcept {}

int main() {
    Sensor s;
    Device& d = s;
    d.reset();
    return 0;
}

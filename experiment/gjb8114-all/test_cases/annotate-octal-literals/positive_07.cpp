#include <iostream>

class Device {
public:
    Device() : address(0377 /* octal */) {}

    int getAddress() const { return address; }

private:
    int address;
};

int main()
{
    Device d;
    std::cout << d.getAddress() << '\n';
    return 0;
}

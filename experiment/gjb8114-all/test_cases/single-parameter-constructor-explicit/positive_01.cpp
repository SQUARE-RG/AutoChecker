#include <iostream>

class Celsius {
public:
    Celsius();
    explicit Celsius(int degrees);
    int getDegrees() const;
    ~Celsius();
private:
    int degrees_;
};

Celsius::Celsius() : degrees_(0) {}
Celsius::Celsius(int degrees) : degrees_(degrees) {}
int Celsius::getDegrees() const { return degrees_; }
Celsius::~Celsius() {}

int main() {
    Celsius c(21);
    std::cout << c.getDegrees() << std::endl;
    return 0;
}

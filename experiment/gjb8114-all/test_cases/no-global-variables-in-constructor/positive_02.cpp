#include <iostream>

int gValue = 7;

class Config {
public:
    explicit Config(int v) : value(v) {}
    int get() const { return value; }
private:
    int value;
};

int main() {
    Config c(gValue);
    return c.get() == 7 ? 0 : 1;
}

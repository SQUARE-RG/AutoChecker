#include <iostream>

class Data {
public:
    Data(int va, int vb) : a(va), b(vb) {
        c = 0;
    }
    int getA() const { return a; }
    int getB() const { return b; }
    int getC() const { return c; }
private:
    int a;
    int b;
    int c;
};

int main() {
    Data d(1, 2);
    std::cout << d.getA() << " " << d.getB() << " " << d.getC() << std::endl;
    return 0;
}

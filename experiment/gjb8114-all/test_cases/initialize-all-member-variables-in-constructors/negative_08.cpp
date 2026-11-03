#include <iostream>

class Data {
public:
    Data(int va, int vb) : a(va) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-4]
        b = vb;
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
    std::cout << d.getA() << " " << d.getB() << std::endl;
    return 0;
}

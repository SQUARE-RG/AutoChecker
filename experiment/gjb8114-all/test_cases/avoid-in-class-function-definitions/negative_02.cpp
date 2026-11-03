#include <iostream>

class MathUtil {
public:
    static int Square(int x) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-1]
    {
        return x * x;
    }

    static int Cube(int x);
};

int MathUtil::Cube(int x) {
    return x * x * x;
}

int main() {
    std::cout << MathUtil::Square(4) << '\n';
    return 0;
}

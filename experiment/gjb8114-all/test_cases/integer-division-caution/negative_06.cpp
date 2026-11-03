#include <iostream>

class Ratio {
public:
    int numerator;
    int denominator;

    int compute() const {
        return numerator / denominator; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-2]
    }
};

int main() {
    Ratio r{10, 3};
    std::cout << r.compute() << std::endl;
    return 0;
}

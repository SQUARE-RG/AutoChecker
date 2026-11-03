#include <iostream>
#include <algorithm>

int gThreshold = 10;

class Limiter {
public:
    explicit Limiter(int seed);
    int limit_value() const;
private:
    int limit;
};

Limiter::Limiter(int seed) {
    limit = std::max(gThreshold, seed); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-1]
}

int Limiter::limit_value() const { return limit; }

int main() {
    Limiter l(3);
    std::cout << l.limit_value() << std::endl;
    return 0;
}

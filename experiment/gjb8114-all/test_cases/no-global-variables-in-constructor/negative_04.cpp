#include <iostream>

struct Limits {
    int max;
    int min;
};

Limits gLimits{100, 0};

class Meter {
public:
    explicit Meter(int raw);
    int level() const;
private:
    int level_;
};

Meter::Meter(int raw) {
    level_ = raw + gLimits.max; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-1]
}

int Meter::level() const {
    return level_;
}

int main() {
    Meter m(20);
    return m.level() == 120 ? 0 : 1;
}

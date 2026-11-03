#include <iostream>

int gValues[3] = { 1, 2, 3 };

class Sum {
public:
    Sum() {
        total = gValues[0] + gValues[1] + gValues[2]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-1]
    }

    int getTotal() const { return total; }

private:
    int total;
};

int main() {
    Sum s;
    return s.getTotal() == 6 ? 0 : 1;
}

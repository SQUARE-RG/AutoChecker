#include <stdexcept>

int compute(int value) try { if (value < 0) { throw std::runtime_error("negative"); } return 100 / value; } catch (const std::runtime_error&) { return 0; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-1]

int main() {
    compute(4);
    return 0;
}

#include <stdexcept>

void release_pointer(bool should_throw) { try { if (should_throw) { throw new std::runtime_error("allocated"); } } catch (const std::runtime_error* e) { delete e; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-1]
}

int main() {
    release_pointer(true);
    return 0;
}

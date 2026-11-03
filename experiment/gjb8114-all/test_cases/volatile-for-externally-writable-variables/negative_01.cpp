#include <cstdint>

// This flag is set asynchronously by the external interrupt controller.
// The main flow only reads it, but the hardware can change its value at any time.
bool g_interrupt_pending = false; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-12]

void external_interrupt_handler() {
    // Simulates the ISR running outside the normal program flow.
    g_interrupt_pending = true;
}

int main() {
    if (g_interrupt_pending) {
        return 1;
    }
    return 0;
}

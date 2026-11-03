#include <float.h> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-4]

int main() {
    float max_value = FLT_MAX;
    return max_value > 0.0f ? 0 : 1;
}

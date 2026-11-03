#include <cstdlib>
#include <cstring>

int main() {
    double* value = static_cast<double*>(std::malloc(sizeof(double)));
    std::memset(value, 0, sizeof(double)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-8]
    return 0;
}

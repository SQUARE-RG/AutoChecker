#include <cstdlib>

int main()
{
    bool enabled = true;
    int chosen = enabled ? NULL : 100; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-14]
    return chosen;
}

#include <atomic>

std::atomic<int> g_ctrl{0};

int main()
{
    int sum = 0;
    for (g_ctrl = 0; g_ctrl.load() < 5; ++g_ctrl) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-1]
    {
        sum += g_ctrl.load();
    }
    return 0;
}

#include <cstdint>

// 该变量由另一个线程异步改写，但未使用 volatile 限定
bool g_shared_ready = false; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-12]

void thread_sets_ready() {
    g_shared_ready = true;
}

int main() {
    thread_sets_ready();
    return g_shared_ready ? 0 : 1;
}

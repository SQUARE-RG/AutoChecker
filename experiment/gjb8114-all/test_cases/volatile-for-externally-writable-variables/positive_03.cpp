#include <cstdint>

// 该变量由另一个线程异步改写，使用 volatile 限定
volatile bool g_shared_ready = false;

void thread_sets_ready() {
    g_shared_ready = true;
}

int main() {
    thread_sets_ready();
    return g_shared_ready ? 0 : 1;
}

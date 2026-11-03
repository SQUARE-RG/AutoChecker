namespace app {
namespace globals {
int* g_buffer = new int[16]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-2]
}
}

int main() {
    delete[] app::globals::g_buffer;
    return 0;
}

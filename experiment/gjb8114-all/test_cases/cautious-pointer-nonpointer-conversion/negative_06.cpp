typedef int* IntPtr;

int main() {
    int raw = 0x1000;
    IntPtr ptr = IntPtr(raw); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-4]
    return ptr == nullptr ? 0 : 1;
}

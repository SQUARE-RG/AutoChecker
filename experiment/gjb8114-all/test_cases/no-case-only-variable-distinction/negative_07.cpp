int main() {
    static int bufferCount = 0;
    int buffercount = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-8]
    return bufferCount + buffercount;
}
